#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 build_ipa.py --config signing.json --profile profile.mobileprovision
