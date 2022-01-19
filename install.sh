#!/bin/bash
set -euo pipefail

# Script para instalar las dependencias en el directorio `/vendor`
rm -rf vendor
mkdir vendor

# JSPsych
JSPSYCH_VERSION=6.3.1  # Si se actualiza a la versión 7 tmb hay que actualizar
                       #   - la versión del script incluido en los archivos html
                       #   - la versión del plugin psychophysics acá abajo
JSPSYCH_LIB_NAME=jspsych-$JSPSYCH_VERSION
JSPSYCH_ZIP_NAME=$JSPSYCH_LIB_NAME.zip
wget https://github.com/jspsych/jsPsych/releases/download/v$JSPSYCH_VERSION/$JSPSYCH_ZIP_NAME \
  -P vendor
unzip vendor/$JSPSYCH_ZIP_NAME \
  -d vendor
rm vendor/$JSPSYCH_ZIP_NAME


# el fork de JSPsych de WebGazer
# más info en https://www.jspsych.org/overview/eye-tracking/ 
WEBGAZER_EXTENSION_NAME=webgazer-jspsych-$JSPSYCH_VERSION
cp -r \
  vendor/$JSPSYCH_LIB_NAME/examples/js/webgazer \
  vendor/$WEBGAZER_EXTENSION_NAME


# el plugin psychophysics para dibujar en la pantalla
# respecto de la versión tener en cuenta el comentario de acá arriba
PSYCHOPHYSICS_VERSION=2.3.4
PSYCHOPHYSICS_ZIP_NAME=jspsych-psychophysics-$PSYCHOPHYSICS_VERSION.zip

wget \
  -O vendor/$PSYCHOPHYSICS_ZIP_NAME \
  https://github.com/kurokida/jspsych-psychophysics/archive/refs/tags/v$PSYCHOPHYSICS_VERSION.zip
unzip vendor/$PSYCHOPHYSICS_ZIP_NAME \
  -d vendor
rm vendor/$PSYCHOPHYSICS_ZIP_NAME


echo Instalado JSPsych $JSPSYCH_VERSION, su extensión para WebGazer y JSPsych-Psychophysics $PSYCHOPHYSICS_VERSION
