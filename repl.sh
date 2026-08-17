#!/bin/sh
# Dark REPL — evaluate expressions, define functions, run statements.
#   expr          -> evaluate and print
#   fn name(...)  -> define a function (persists for the session)
#   > stmt        -> run as a top-level statement (no auto-print)
#   quit / exit   -> leave

DARKC="./darkc"
TMPD="${TMPDIR:-/tmp}/darkrepl.$$"
mkdir -p "$TMPD"
trap 'rm -rf "$TMPD"' EXIT

PREAMBLE=""

echo "Dark REPL — type an expression; 'fn name(...) {...}' to define; 'quit' to leave."
echo

while true; do
    printf "> "
    IFS= read -r line || { echo; break; }
    [ -z "$line" ] && continue
    case "$line" in
        quit|exit|q) break ;;
    esac

    case "$line" in
        fn\ *) PREAMBLE="$PREAMBLE$line
"; echo "  defined"; continue ;;
    esac

    if [ "${line#">"}" = "$line" ]; then
        prog="$PREAMBLE
emit($line)"
    else
        prog="$PREAMBLE
${line#">"}"
    fi

    printf '%s\n' "$prog" > "$TMPD/prog.dark"
    if "$DARKC" "$TMPD/prog.dark" "$TMPD/out" 2>"$TMPD/err" >/dev/null; then
        chmod +x "$TMPD/out"
        "$TMPD/out"
        echo
    else
        echo "error:"
        sed 's/^/  /' "$TMPD/err"
    fi
done
