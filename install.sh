#!/bin/bash
set -euo pipefail

# Script para instalar las dependencias en el directorio `/vendor`
rm -rf vendor
mkdir vendor

# JSPsych
VERSION=6.3.1  # Si se cambia la versión también hay que cambiarlo en los
               # archivos html
JSPSYCH_LIB_NAME=jspsych-$VERSION
JSPSYCH_ZIM_NAME=$JSPSYCH_LIB_NAME.zip
wget https://github.com/jspsych/jsPsych/releases/download/v$VERSION/$JSPSYCH_ZIM_NAME \
  -P vendor
unzip vendor/$JSPSYCH_ZIM_NAME \
  -d vendor
rm vendor/$JSPSYCH_ZIM_NAME

# el fork de JSPsych de WebGazer
# más info en https://www.jspsych.org/overview/eye-tracking/ 
WEBGAZER_EXTENSION_NAME=webgazer-jspsych-$VERSION
cp -r \
  vendor/$JSPSYCH_LIB_NAME/examples/js/webgazer \
  vendor/$WEBGAZER_EXTENSION_NAME

echo Instalados JSPsych y su extensión de WebGazer
