# rastreador-ocular

## Desarollo

### módulos de js + plugins

`./install.sh` para instalar las dependencias.  
`node index.js` para buildear el js.
La versión de `node` requerida está dentro del archivo `.nvmrc` por lo que puede
usarse `nvm use` (luego de instalar al menos una vez con `nvm install`) para
cambiar a la versión requerida (https://github.com/nvm-sh/nvm).

Dps el entry point es `index.html`, con abrirlo en un navegador se pueden usar
los experimentos armados. Se puede por ejemplo hacer `firefox index.html`.

### data analysis

Setear el entorno:
```bash
python -m venv rastoc-env  # para crear el entorno virtual, armado con Python3.9
source rastoc-env/bin/activate  # para activar el entorno
pip install -r requirements.txt  # para instalar las dependencias
```

Armar los heatmaps de un experimento:
```python
python src/data-analysis/main.py data/antisacadas.json
```

## Utilización

Se provee una interfaz JSPsych para utilizar Rastoc. El
experimento de antisacadas ([`html`](/experimentos/online-experiment.html),
[`js`](/experimentos/online-experiment.js)) puede utilizarse como referencia.  
Resumidamente, se debe:
- importar los scripts necesarios (listados abajo)
- llamar a `jsPsych.init` dentro de un listener para el evento `rastoc-ready`:
```javascript
document.addEventListener('rastoc:ready', () => {
  jsPsych.init(...);
})
```
- agregar los llamados a los plugins `webgazer-init-camera`, `rastoc-initialize`
y `rastoc-finish`.
- agregar a WebGazer como extensión.

#### Scripts a importar

```html
<script src="https://unpkg.com/@tensorflow/tfjs-core@2.4.0/dist/tf-core.js"></script>
<script src="https://unpkg.com/@tensorflow/tfjs-converter@2.4.0/dist/tf-converter.js"></script>
<script src="https://unpkg.com/@tensorflow/tfjs-backend-webgl@2.4.0/dist/tf-backend-webgl.js"></script>
<script src="https://unpkg.com/@tensorflow-models/face-landmarks-detection@0.0.1/dist/face-landmarks-detection.js"></script>

<link  href="../vendor/jspsych-6.3.1/css/jspsych.css" rel="stylesheet" type="text/css">
<script src="../vendor/jspsych-6.3.1/jspsych.js"></script>
<script src="../vendor/webgazer-jspsych-6.3.1/webgazer.js"></script>
<script src="../vendor/jspsych-6.3.1/extensions/jspsych-ext-webgazer.js"></script>

<script src="../build/rastoc.js"></script>
<script src="../build/rastoc-jspsych.js"></script>
```

## Investigación

En la carpeta [`/notas`](/notas/README.md) se encuentra un markdown en estilo
informe que documenta algunas ideas relacionadas al trabajo. Hay también notas
menos formales de algunos papers relacionados.  
A partir de un momento las notas las fui subiendo a un drive.
