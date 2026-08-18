#!/bin/bash
cd /home/dark/projects/dark-language
for t in array random html math json map string fs os; do
    echo "=== $t ==="
    ./darkc examples/libtest_$t.dark /tmp/libtest_$t 2>&1 | head -3
    /tmp/libtest_$t 2>&1 | head -20
    echo "exit=$?"
done
