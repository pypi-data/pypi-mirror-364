#!/usr/bin/env bash
set -euo pipefail

SELF=$(readlink -f "${BASH_SOURCE[0]}")
DIR=${SELF%/*/*}

cd -- "$DIR"
./scripts/install_in_venv.sh tests
source ./venv/bin/activate
python -m unittest discover -v ./test
