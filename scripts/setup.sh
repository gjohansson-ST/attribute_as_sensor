#!/bin/sh

set -e

cd "$(dirname "$0")/.."

if ! [ -x "$(command -v uv)" ]; then
  python3 -m pip install uv
fi

if [ ! -d .venv ]; then
  uv venv .venv
fi
. .venv/bin/activate

uv pip install -r requirements_dev.txt

prek install
