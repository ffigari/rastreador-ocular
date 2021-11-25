# rastreador-ocular

## Development

### módulos de js + plugins

Con `./install.sh` se instalan las dependencias.  
El entry point es `index.html`.
Se puede hacer `firefox index.html` por ejemplo.

### data analysis

Setear el entorno:
```
python -m venv rastoc-env  # armado con Python 3.9.7
source rastoc-env/bin/activate
pip install -r requirements.txt 
```

## Interfaz JSPsych

Se provee una interfaz para la utilización de Rastoc a la par de JSPsych. El
experimento de lectura ([`html`](/experimentos/lectura.html),
[`js`](/experimentos/lectura.js)) puede utilizarse como referencia.  
Resumidamente, se debe:
- importar los scripts necesarios
- envolver el llamado a `jsPsych.init` dentro de un listener al evento que nos
indica que Rastoc está listo.
- agregar los llamados a los plugins provistos `rastoc-initialize` y
`rastoc-finish`.
- agregar a WebGazer como extensión.
- realizar un llamado a `convertToTrackedTimeline` al timeline que queramos
decorar. Esta función retornará un nuevo timeline que incluye calibración del
sistema, detección de descalibración y exportación de datos en formato
estandarizado. Adicionalmente, en el último nodo del timeline input se puede 
proveer información sobre el trial ejecutado utilizando 
[`on_finish`](https://www.jspsych.org/7.0/overview/events/#on_finish-trial) y
haciendo `data.trial = { config: { ... } }`.

## Utilización directa

Se planea la adición y documentación de una interfaz directa de Rastoc cosa de
permitir su uso en distintos contextos.

## Investigación

En la carpeta [`/notas`](/notas/README.md) se encuentra un markdown en estilo
informe que documenta algunas ideas relacionadas al trabajo. Hay también notas
menos formales de algunos papers relacionados.
