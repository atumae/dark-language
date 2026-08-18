#!/bin/bash
cd /home/dark/projects/dark-language
for t in array random time html math json map string fs os; do
    echo "=== $t ==="
    ./darkc examples/libtest_$t.dark /tmp/libtest_$t 2>&1 | head -5
    /tmp/libtest_$t 2>&1 | head -40
    echo "exit=$?"
done
