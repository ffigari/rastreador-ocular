const requirementsChecker = (function () {
  const MINIMUM_VIEWPORT_WIDTH = 700;
  const MINIMUM_VIEWPORT_HEIGHT = 500;

  const MINIMUM_CAMERA_WIDTH = 640;
  const MINIMUM_CAMERA_HEIGHT = 480;

  return {
    async checkSystem() {
      let errors = [];

      const viewportWidth = Math.max(
        document.documentElement.clientWidth || 0,
        window.innerWidth || 0
      );
      const viewportHeight = Math.max(
        document.documentElement.clientHeight || 0,
        window.innerHeight || 0
      );
      const viewportSizeIsRespected = 
        viewportHeight > MINIMUM_VIEWPORT_HEIGHT &&
        viewportWidth > MINIMUM_VIEWPORT_HEIGHT;
      !viewportSizeIsRespected && errors.push(
        `La pantalla debe tener al menos una resolución de ${
          MINIMUM_VIEWPORT_WIDTH
        }x${
          MINIMUM_VIEWPORT_HEIGHT
        }.`
      );


      let cameraIsAccessible = true;
      try {
        await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
      } catch(e) {
        cameraIsAccessible = false;
        errors.push(
          `No se logró acceso a una cámara web. Asegurate de darle permisos cuando el navegador te lo pida.`
        );
      }

      if (cameraIsAccessible) {
        try {
          await navigator.mediaDevices.getUserMedia({
            audio: false,
            video: {
              width: { min: MINIMUM_CAMERA_WIDTH },
              height: { min: MINIMUM_CAMERA_HEIGHT },
            },
          });
        } catch (e) {
          errors.push(
            `Tu cámara web no tiene la resolución mínima necesaria de ${
              MINIMUM_CAMERA_WIDTH
            }x${
              MINIMUM_CAMERA_HEIGHT
            }.`
          );
        }

      }

      return {
        systemConfig: { viewportWidth, viewportHeight },
        systemIsOk: errors.length === 0,
        errors,
      };
    }
  };
})();
