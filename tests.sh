#!/usr/bin/bash

FILE_DIR="$( cd "$(dirname -- "$0")" &> /dev/null && pwd )"
VENV_DIR="${FILE_DIR}/venv"


if [ -n "${VIRTUAL_ENV}" ]; then
  echo " -> Using active virtualenv"
elif [ -d "${VENV_DIR}" ]; then
  echo " -> Activating virtualenv: ${VENV_DIR}"
  source "${VENV_DIR}/bin/activate"
else
  echo " -> Virtualenv not found, using default Python of system"
fi

cd "$FILE_DIR" || exit 1
pytest -v