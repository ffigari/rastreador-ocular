#!/bin/bash
set -euo pipefail

DIST_PATH=www/vendor
SRC_PATH=src/vendor
rm -rf $DIST_PATH
mkdir $DIST_PATH
rm -rf $SRC_PATH
mkdir $SRC_PATH

# webgazer
rm -f ./$DIST_PATH/webgazer.js
rm -rf ./$SRC_PATH/webgazer
git clone -b develop https://github.com/ffigari/WebGazer $SRC_PATH/webgazer

(
  nvm install
  nvm use
  cd $SRC_PATH/webgazer
  npm i
  npm run build
  cp dist/webgazer.js ../../../$DIST_PATH/
)

# Psychophysics
PSYCHOPHYSICS_VERSION=3.1.0
PSYCHOPHYSICS_ZIP_NAME=jspsych-psychophysics-$PSYCHOPHYSICS_VERSION.zip

wget \
  -O $DIST_PATH/$PSYCHOPHYSICS_ZIP_NAME \
  https://github.com/kurokida/jspsych-psychophysics/archive/refs/tags/v$PSYCHOPHYSICS_VERSION.zip
unzip $DIST_PATH/$PSYCHOPHYSICS_ZIP_NAME \
  -d $DIST_PATH
rm $DIST_PATH/$PSYCHOPHYSICS_ZIP_NAME

echo Done installing WebGazer fork and JSPsych-Psychophysics $PSYCHOPHYSICS_VERSION
