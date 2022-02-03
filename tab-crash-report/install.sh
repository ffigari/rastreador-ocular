#!/bin/bash

set -euo pipefail

INSTALL_PATH=vendor
rm -rf $INSTALL_PATH
mkdir $INSTALL_PATH

# webgazer
rm -f ./webgazer.js
rm -rf ./webgazer
git clone -b master https://github.com/jspsych/WebGazer webgazer

(
  . ~/.nvm/nvm.sh
  nvm use 14
  cd webgazer
  npm i
  npm run build
  cp dist/webgazer.js ../$INSTALL_PATH/
)

# Psychophysics
PSYCHOPHYSICS_VERSION=3.1.0
PSYCHOPHYSICS_ZIP_NAME=jspsych-psychophysics-$PSYCHOPHYSICS_VERSION.zip

wget \
  -O $INSTALL_PATH/$PSYCHOPHYSICS_ZIP_NAME \
  https://github.com/kurokida/jspsych-psychophysics/archive/refs/tags/v$PSYCHOPHYSICS_VERSION.zip
unzip $INSTALL_PATH/$PSYCHOPHYSICS_ZIP_NAME \
  -d $INSTALL_PATH
rm $INSTALL_PATH/$PSYCHOPHYSICS_ZIP_NAME

echo Done installing JSPsych-Psychophysics $PSYCHOPHYSICS_VERSION and JSPsych fork of WG
