#!/usr/bin/env bash

sh ./_clearDatabase.sh
python ./_clearFingerprints.py
javac ./bootloader/src/IGC.java
mv ./bootloader/src/IGC.class ./Bootloader.class
echo "Initalization complete"