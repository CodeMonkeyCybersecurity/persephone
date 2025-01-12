#!/bin/bash
# createMinIO.sh

wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/
USER=$(whoami)
sudo mkdir -p /data
sudo chown -R $USER: /data && sudo chmod u+rxw /data