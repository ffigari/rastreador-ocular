import plugins from './plugins/index.js'

// Esto carga a JSPsych los plugins que están en la carpeta /plugins que se
// importa acá arriba
plugins.forEach(({ name, trialCb }) => {
  jsPsych.plugins[name] = (function () {
    return {
      info: {
        name,
        parameters: {},
      },
      trial: trialCb
    }
  })();
});
