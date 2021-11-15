# rastreador-ocular

## Implementación

### módulos de js + plugins

Con `./install.sh` se instalan las dependencias.  
El entry point es `index.html`.
Se puede hacer `firefox index.html` por ejemplo.

### heatmap

Setear el entorno:
```
python -m venv rastoc-env  # armado con Python 3.9.7
source rastoc-env/bin/activate
pip install -r requirements.txt 
```

## Armar experimentos

En `/plugins` hay una serie de plugins de JSPsych que permiten la interacción
con el sistema de eyetracking. Para armar un experimento que incluya la
detección de movimiento y la estimación de la mirada deben incluirse los
siguientes archivos dentro de su `<head>`:
```html
<!-- JS de tensorflow utilizado para la detección de movimiento -->
<script src="https://unpkg.com/@tensorflow/tfjs-core@2.4.0/dist/tf-core.js"></script>
<script src="https://unpkg.com/@tensorflow/tfjs-converter@2.4.0/dist/tf-converter.js"></script>
<script src="https://unpkg.com/@tensorflow/tfjs-backend-webgl@2.4.0/dist/tf-backend-webgl.js"></script>
<script src="https://unpkg.com/@tensorflow-models/face-landmarks-detection@0.0.1/dist/face-landmarks-detection.js"></script>

<!--
  JS propio para la detección de movimiento, la estimación de mirada y utils.
  El path dependenrá de la posición relativa del html en cuestión
-->
<script src="../src/movement-detection.js"></script>
<script src="../src/index.js"></script>
<script src="../src/rastoc.js"></script>
```
Tendrá luego que importarse al menos el plugin de calibración.
[`/experimentos/antisacadas.html`](/experimentos/antisacadas.html) puede
utilizarse como referencia.

## Utilización directa

Pueden utilizarse directamente los módulos de estimación de mirada y de
detección de movimiento, por ejemplo para la construcción de un plugin propio de
JSPsych. Más adelante habrá una documentación más concreta. De momento pueden
mirarse los objetos exportados dentro de cada módulo ([`/src/rastoc.js`](
/src/rastoc.js), [`/src/movement-detection.js`](/src/movement-detection.js)).
Ambos módulos deben calibrarse previo a poder ser utilizados. Sin embargo, si se
importa el módulo de detección de movimiento entonces se calibrará a la par del
de estimación de mirada cuando se llame al método `runExplicitCalibration`.

## Notas del trabajo

En la carpeta [`/notas`](/notas/README.md) se encuentra un markdown en estilo
informe que documenta algunas ideas relacionadas al trabajo. Hay también notas
menos formales de algunos papers relacionados.
