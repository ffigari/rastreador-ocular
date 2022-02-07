#!/bin/bash
set -euo pipefail

INSTALL_PATH=www/vendor
rm -rf $INSTALL_PATH
mkdir $INSTALL_PATH

# webgazer
rm -f ./$INSTALL_PATH/webgazer.js
rm -rf ./webgazer
git clone -b develop https://github.com/ffigari/WebGazer webgazer

(
  . ~/.nvm/nvm.sh
  nvm use 14
  cd webgazer
  npm i
  npm run build
  cp dist/webgazer.js ../$INSTALL_PATH/
)
rm -rf ./webgazer

# Psychophysics
PSYCHOPHYSICS_VERSION=3.1.0
PSYCHOPHYSICS_ZIP_NAME=jspsych-psychophysics-$PSYCHOPHYSICS_VERSION.zip

wget \
  -O $INSTALL_PATH/$PSYCHOPHYSICS_ZIP_NAME \
  https://github.com/kurokida/jspsych-psychophysics/archive/refs/tags/v$PSYCHOPHYSICS_VERSION.zip
unzip $INSTALL_PATH/$PSYCHOPHYSICS_ZIP_NAME \
  -d $INSTALL_PATH
rm $INSTALL_PATH/$PSYCHOPHYSICS_ZIP_NAME

echo Done installing WebGazer fork and JSPsych-Psychophysics $PSYCHOPHYSICS_VERSION
