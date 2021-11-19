jsPsych.plugins['rastoc-initialize'] = (function(){
  return {
    info: {
      name: 'rastoc-initialize',
    },
    trial: async function(display_element, trial) {
      const {
        systemConfig, systemIsOk, errors
      } = await requirementsChecker.checkSystem()
      if (!systemIsOk) {
        display_element.innerHTML = `
          <h2>Hardware insuficiente</h2>
          <p>
            Tu sistema no cumple con los requerimientos de hardware necesarios
            por lo que no podremos continuar con el experimento.
          </p>
          <ul>
            ${errors.map(e => `<li>${e}</li>`).join('')}
          </ul>
        `;
      } else {
        jsPsych.finishTrial({ systemConfig });
      }
    },
  }
})();
