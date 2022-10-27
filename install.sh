#!/bin/bash
set -euo pipefail

if ! command -v node &> /dev/null
then
    echo node was not found, please install node v14
    exit
fi

if ! node --version | grep -q "v14"; then
  echo version $(node --version) was found, please install node v14
fi

npm i

DIST_PATH=www/vendor
INSTALL_PATH=eye-tracker/webgazer
rm -rf $DIST_PATH
mkdir $DIST_PATH
rm -rf $INSTALL_PATH

# webgazer
rm -f ./$DIST_PATH/webgazer.js
git clone -b develop https://github.com/ffigari/WebGazer $INSTALL_PATH

(
  cd $INSTALL_PATH
  npm i
  npm run build
  cp dist/webgazer.js ../../$DIST_PATH/
)

# Psychophysics
PSYCHOPHYSICS_VERSION=3.2.0
PSYCHOPHYSICS_ZIP_NAME=jspsych-psychophysics-$PSYCHOPHYSICS_VERSION.zip

wget \
  -O $DIST_PATH/$PSYCHOPHYSICS_ZIP_NAME \
  https://github.com/kurokida/jspsych-psychophysics/archive/refs/tags/v$PSYCHOPHYSICS_VERSION.zip
unzip $DIST_PATH/$PSYCHOPHYSICS_ZIP_NAME \
  -d $DIST_PATH
rm $DIST_PATH/$PSYCHOPHYSICS_ZIP_NAME

echo Done installing WebGazer fork and JSPsych-Psychophysics $PSYCHOPHYSICS_VERSION
