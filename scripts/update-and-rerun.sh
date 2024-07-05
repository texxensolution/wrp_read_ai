#!/usr/bin/bash

git pull

sudo systemctl restart readai_worker.service

echo "readai updated and restarted :)"

sudo systemctl status readai_worker.service