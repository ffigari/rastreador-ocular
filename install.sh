#!/bin/bash
set -euo pipefail

INSTALL_PATH=www/vendor
rm -rf $INSTALL_PATH
mkdir $INSTALL_PATH

# Psychophysics
PSYCHOPHYSICS_VERSION=3.1.0
PSYCHOPHYSICS_ZIP_NAME=jspsych-psychophysics-$PSYCHOPHYSICS_VERSION.zip

wget \
  -O $INSTALL_PATH/$PSYCHOPHYSICS_ZIP_NAME \
  https://github.com/kurokida/jspsych-psychophysics/archive/refs/tags/v$PSYCHOPHYSICS_VERSION.zip
unzip $INSTALL_PATH/$PSYCHOPHYSICS_ZIP_NAME \
  -d $INSTALL_PATH
rm $INSTALL_PATH/$PSYCHOPHYSICS_ZIP_NAME

echo Done installing JSPsych-Psychophysics $PSYCHOPHYSICS_VERSION

# TODO: Checkout wg fork, compile into www directory
