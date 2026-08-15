#!/bin/sh
# Self-hosting bootstrap: rebuild darkc from its own Dark source.
set -e
./darkc examples/darkc.dark ./darkc.new
chmod +x ./darkc.new
mv ./darkc.new ./darkc
echo "darkc rebuilt"
