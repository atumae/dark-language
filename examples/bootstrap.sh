#!/bin/bash
# Two-stage self-host bootstrap: rebuild darkc (linux) and darkc.exe (windows)
cd /home/dark/projects/dark-language
./darkc examples/darkc.dark -o /tmp/darkc1 --target linux || exit 1
/tmp/darkc1 examples/darkc.dark -o /tmp/darkc2 --target linux || exit 1
cp /tmp/darkc2 darkc
./darkc examples/darkc.dark -o darkc.exe --target windows || exit 1
echo "bootstrap ok"
