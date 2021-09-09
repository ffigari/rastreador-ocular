const calibrator = (function () {
  const state = {
    lastCalibrationPercentageCoordinates: null
  }
  return {
    get lastCalibrationPercentageCoordinates() {
      if (!state.lastCalibrationPercentageCoordinates) {
        throw new Error('No se detectó una calibración previa.')
      }
      return state.lastCalibrationPercentageCoordinates
    },
    async runExplicitCalibration(stimulusUpdater) {
      let pixCoordinates = [
        [10,10], [10,50], [10,90],
        [50,10], [50,50], [50,90],
        [90,10], [90,50], [90,90],
      ]
      math.shuffle(pixCoordinates)
      state.lastCalibrationPercentageCoordinates = [];
      for (const [xPerGroundTruth, yPerGroundTruth] of pixCoordinates) {
        // Draw this ground truth coordinate...
        const [
          xPixGT, yPixGT
        ] = stimulusUpdater(xPerGroundTruth, yPerGroundTruth);
        // ...and map the coordiante once the user presses the space bar
        await forSingleSpaceBarOn(document)
        wgExt.calibratePoint(xPixGT, yPixGT)
        state.lastCalibrationPercentageCoordinates.push([
          xPerGroundTruth, yPerGroundTruth
        ])
      }
    }
  }
})()

const estimator = (function () {
  const state = {
    visualization: {
      isOn: false,
      elementId: null,
      loopCallbackIntervalId: null,
    }
  }
  return {
    async currentPrediction() {
      const current = await wgExt.getCurrentPrediction();
      if (current === null) {
        throw new Error(
          `WebGazer retornó 'null' para la predicción actual. Verificar que la librería haya sido correctamente inicializada.`
        );
      }
      return [current.x, current.y];
    },
    showVisualization () {
      if (state.visualization.isOn) {
        throw new Error('La visualización de la estimación ya está activada.');
      }

      const visualizationElement = drawer.appendGazeVisualization();
      const intervalId = setInterval(async () => {
        const [x, y] = await this.currentPrediction();
        drawer.moveToPixels(
          visualizationElement,
          x,
          y
        );
      }, 100)

      Object.assign(state.visualization, {
        isOn: true,
        elementId: visualizationElement.id,
        loopCallbackIntervalId: intervalId,
      });
    },
    hideVisualization() {
      if (!state.visualization.isOn) {
        throw new Error('La visualización de la predicción no está activada.');
      }

      document
        .getElementById(state.visualization.elementId)
        .remove();
      clearInterval(state.visualization.loopCallbackIntervalId);

      Object.assign(state.visualization, {
        isOn: false,
        elementId: null,
        loopCallbackIntervalId: null,
      });
    },
    async runValidationRound(drawer) {
      let stimulus = drawer.appendValidationVisualization()
      const stimulusUpdater = (xPercentage, yPercentage) => {
        drawer.moveToPercentages(stimulus, xPercentage, yPercentage)
        return drawer.getCenterInPixels(stimulus)
      }
      const measurements = []
      const stimulusCoordinates = [
        ...calibrator.lastCalibrationPercentageCoordinates
      ]
      math.shuffle(stimulusCoordinates)

      for (const [xPerGroundTruth, yPerGroundTruth] of stimulusCoordinates) {
        const stimulusMeasurements = {
          groundTruthPercentages: [xPerGroundTruth, yPerGroundTruth],
          groundTruthPixels: stimulusUpdater(xPerGroundTruth, yPerGroundTruth),
          startedAt: new Date,
          endedAt: null,
          estimation: null,
        }
        await forSingleSpaceBarOn(document)
        stimulusMeasurements.estimation = {
          coordinate: await this.currentPrediction(),
          ts: new Date,
        }
        stimulusMeasurements.endedAt = new Date
        measurements.push(stimulusMeasurements)
      }
      drawer.erasePoint(stimulus)

      return new function() {
        const rawResults = measurements.map(({
          groundTruthPercentages, groundTruthPixels: [xGTPix, yGTPix], estimation
        }) => ({
          groundTruthPercentages,
          estimation,
          get linearError() {
            const [x, y] = this.estimation.coordinate
            const xErr = Math.abs(x - xGTPix)
            const yErr = Math.abs(y - yGTPix)
            return xErr + yErr
          },
          get squareError() {
            const [x, y] = this.estimation.coordinate
            const xErr = Math.abs(x - xGTPix)
            const yErr = Math.abs(y - yGTPix)
            return xErr * xErr + yErr * yErr
          },
        }))
        Object.assign(this, {
          rawResults,
          get average() {
            const _avged = (arr) => {
              if (arr.length === 0) {
                throw new Error(
                  'No se puede realizar el promedio de un arreglo vacío.'
                )
              }
              return arr.reduce((acc, cur) => acc + cur, 0) / arr.length
            }
            return {
              linearError() {
                return _avged(rawResults.map(({ linearError }) => linearError))
              },
              squareError() {
                return _avged(rawResults.map(({ squareError }) => squareError))
              }
            }
          },
        })
      }
    },
  }
})()

const rastoc = (function() {
  const state = {
    phase: 'idle',
  }
  return {
    get continueTo() {
      return {
        estimate() {
          if (state.phase !== 'estimating') {
            throw new Error(`No se puede continuar estimando por que la fase actual es '${state.phase}'`)
          }
          return estimator
        }
      }
    },
    get switchTo () {
      return {
        idle() {
          if (state.phase === 'idle') {
            throw new Error(`No se pudo cambiar a 'idle' porque la fase ya actual es 'idle'.`)
          }

          Object.assign(state, {
            phase: 'idle',
          })
          wgExt.pause();

          return null
        },
        async calibrating() {
          if (state.phase !== 'idle') {
            throw new Error(`No se pudo cambiar a 'calibrating' porque la fase actual no es 'idle'.`)
          }

          Object.assign(state, {
            phase: 'calibrating',
          })
          await wgExt.resume();

          return calibrator
        },
        async estimating() {
          const msg = (
            reason
          ) => `No se pudo cambiar a 'estimating' porque ${reason}.`
          if (state.phase !== 'idle') {
            throw new Error(msg(`la fase actual no es 'idle'`))
          }

          Object.assign(state, {
            phase: 'estimating',
          })
          await wgExt.resume();

          return estimator
        },
      }
    },
  };
})();
