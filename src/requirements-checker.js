const requirementsChecker = (function () {
  const MINIMUM_HEIGHT = 500;
  const MINIMUM_WIDTH = 700;

  return {
    checkSystem() {
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
        viewportHeight > MINIMUM_HEIGHT &&
        viewportWidth > MINIMUM_HEIGHT;

      !viewportSizeIsRespected && errors.push(
        `La pantalla debe tener al menos una resolución de ${
          MINIMUM_WIDTH
        }x${
          MINIMUM_HEIGHT
        }.`
      );

      return {
        systemIsOk: viewportSizeIsRespected,
        errors,
      };
    }
  };
})();
