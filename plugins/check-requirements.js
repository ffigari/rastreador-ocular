jsPsych.plugins['check-requirements'] = (function(){
  return {
    info: {
      name: 'check-requirements',
    },
    trial: async function(display_element, trial) {
      if (!requirementsChecker.requirementsAreMet()) {
        display_element.innerHTML = `
          <h2>Hardware insuficiente</h2>
          <p>
            Tu sistema no cumple con los requerimientos de hardware necesarios
            por lo que no podremos continuar con el experimento.
          </p>
        `;
      } else {
        jsPsych.finishTrial();
      }
    },
  }
})();
