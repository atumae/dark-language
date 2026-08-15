#!/bin/sh
# Self-hosting bootstrap: rebuild darkc and darkc.exe from their own Dark source.
set -e
./darkc examples/darkc.dark ./darkc.new
chmod +x ./darkc.new
mv ./darkc.new ./darkc
./darkc examples/darkc.dark ./darkc.exe --target windows
echo "darkc and darkc.exe rebuilt"
