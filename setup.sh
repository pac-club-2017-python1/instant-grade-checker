#!/usr/bin/env bash

sh ./scripts/_clearDatabase.sh
python ./_clearFingerprints.py
echo "Initalization complete"