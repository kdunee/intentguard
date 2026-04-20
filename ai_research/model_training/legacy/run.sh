#!/bin/bash

bash ./install.sh || exit 1

python ./intentguard_finetuning.py

gcloud compute instances stop "$(curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/name)" --zone="$(curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/zone | awk -F'/' '{print $NF}')"
