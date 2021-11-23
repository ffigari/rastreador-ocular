const wgExt = jsPsych.extensions.webgazer

// TODO: Las variables 'calibrator' y 'estimator' no tendrían que quedar en el
//       scope global
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
    async reset() {
      typeof movementDetector !== 'undefined' &&
        movementDetector.isReady &&
        movementDetector.stop();

      await wgExt.resetCalibration();
    },
    async runExplicitCalibration(drawer) {
      let stimulus = drawer.appendMarkerFor.calibration()
      const stimulusUpdater = (xPercentage, yPercentage) => {
        drawer.moveToPercentages(stimulus, xPercentage, yPercentage)
        return drawer.getCenterInPixels(stimulus)
      }
      let pixCoordinates = [
        [10,10], [10,50], [10,90],
        [50,10], [50,50], [50,90],
        [90,10], [90,50], [90,90],
      ]
      math.shuffle(pixCoordinates)
      state.lastCalibrationPercentageCoordinates = [];
      typeof movementDetector !== 'undefined' &&
        movementDetector.isReady &&
        movementDetector.start.calibration();
      for (const [xPerGroundTruth, yPerGroundTruth] of pixCoordinates) {
        // Draw this ground truth coordinate...
        const [
          xPixGT, yPixGT
        ] = stimulusUpdater(xPerGroundTruth, yPerGroundTruth);
        // ...and map the coordiante once the user presses the space bar
        await forSingleSpaceBarOn(document)
        typeof movementDetector !== 'undefined' &&
            movementDetector.isReady &&
            movementDetector.useNextFrameAsValidPosition();
        wgExt.calibratePoint(xPixGT, yPixGT)
        state.lastCalibrationPercentageCoordinates.push([
          xPerGroundTruth, yPerGroundTruth
        ])
      }
      typeof movementDetector !== 'undefined' &&
          movementDetector.isReady &&
          movementDetector.start.detection();
      drawer.erasePoint(stimulus)
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

      const visualizationElement = drawer.appendMarkerFor.gaze();
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
      let stimulus = drawer.appendMarkerFor.validation()
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
    dataRecollection: {
      inProgress: false,
      intervalId: null,
      values: [],
    }
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
            throw new Error(
              `No se pudo cambiar a 'idle' porque la fase ya actual es 'idle'.`
            );
          }

          let estimatedGazes = null;
          if (state.dataRecollection.inProgress) {
            estimatedGazes = [...state.dataRecollection.values].map(({
              estimatedAt, estimation
            }) => ({
              name: 'gaze-estimation',
              ts: estimatedAt,
              x: estimation[0],
              y: estimation[1],
              quality: {
                // TODO: Armar algo para poder extrapolar alguna medida de
                //       confianza.
                //       Una primer opción es al momento de la estimación usar
                //       la distancia de los ojos al promedio de las posiciones
                //       de los momentos de calibración
                confidence: 1,
              }
            }));
            clearInterval(state.dataRecollection.intervalId);
            Object.assign(state.dataRecollection, {
              inProgress: false,
              intervalId: null,
              values: [],
            })
          }

          Object.assign(state, {
            phase: 'idle',
          })
          wgExt.pause();

          return estimatedGazes
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
          if (state.phase !== 'idle') {
            throw new Error("No se pudo cambiar a 'estimating' porque la fase actual no es 'idle'.");
          }

          Object.assign(state, {
            phase: 'estimating',
          })
          await wgExt.resume();

          Object.assign(state.dataRecollection, {
            inProgress: true,
            intervalId: setInterval(async () => {
              state.dataRecollection.values.push({
                estimatedAt: new Date,
                estimation: await estimator.currentPrediction()
              })
              if (!state.dataRecollection.inProgress) {
                clearInterval(state.dataRecollection.intervalId)
              }
            }, 1000 / 24)
          })

          return estimator
        },
      }
    },
  };
})();
