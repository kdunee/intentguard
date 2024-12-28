#!/bin/bash

python -m pip install torch --index-url https://download.pytorch.org/whl/cu121 || exit 1
python -m pip install -r requirements.txt || exit 1
python -m pip install unsloth || exit 1
python -m pip uninstall unsloth -y && pip install --upgrade --no-cache-dir --no-deps git+https://github.com/unslothai/unsloth.git || exit 1
