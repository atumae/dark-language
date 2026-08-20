#!/bin/bash
# Rebuild the full chain from the known-good committed darkc_linux.
# Run inside the repo root after `git pull`.
set -e
cd "$(dirname "$0")"

echo "== 1) build darkc.exe (windows) =="
./darkc_linux examples/darkc.dark -o darkc.exe --target windows

echo "== 2) build test exes (windows) =="
./darkc_linux examples/libtest_wconn2.dark -o wconn2.exe --target windows
./darkc_linux examples/libtest_wdns.dark -o wdns.exe --target windows
./darkc_linux examples/libtest_whttp.dark -o whttp.exe --target windows
./darkc_linux examples/libtest_whttps.dark -o whttps.exe --target windows

echo "== 3) sanitiy check: balance of stack frames and no bogus calls =="
python3 - <<'PYEOF'
def load(fn):
    return open(fn,'rb').read()[0x200:]
import glob, os
for fn in ["darkc.exe","wconn2.exe","wdns.exe","whttp.exe","whttps.exe"]:
    b = load(fn)
    s1 = b.count(bytes([0x48,0x81,0xEC,0xB8,0x01,0,0])); a1 = b.count(bytes([0x48,0x81,0xC4,0xB8,0x01,0,0]))
    s8 = b.count(bytes([0x48,0x81,0xEC,0x00,0x08,0,0])); a8 = b.count(bytes([0x48,0x81,0xC4,0x00,0x08,0,0]))
    bogus = b.count(bytes([0xE8,0x5B,0xFE,0xFF,0xFF])) + b.count(bytes([0xE8,0x52,0xFE,0xFF,0xFF]))
    ok = (s1==a1) and (s8==a8) and bogus==0
    print(f"{fn}: sub1B8={s1} add1B8={a1} sub800={s8} add800={a8} bogus={bogus} -> {'OK' if ok else 'CHECK!'}")
PYEOF
echo "done"