#!/bin/bash
set -euo pipefail

rm -rf vendor
mkdir vendor

# Psychophysics
PSYCHOPHYSICS_VERSION=3.1.0
PSYCHOPHYSICS_ZIP_NAME=jspsych-psychophysics-$PSYCHOPHYSICS_VERSION.zip

wget \
  -O vendor/$PSYCHOPHYSICS_ZIP_NAME \
  https://github.com/kurokida/jspsych-psychophysics/archive/refs/tags/v$PSYCHOPHYSICS_VERSION.zip
unzip vendor/$PSYCHOPHYSICS_ZIP_NAME \
  -d vendor
rm vendor/$PSYCHOPHYSICS_ZIP_NAME


echo Done installing JSPsych-Psychophysics $PSYCHOPHYSICS_VERSION
