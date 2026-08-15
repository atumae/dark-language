# Dark

A self-hosting programming language and compiler for Linux x86_64 and Windows.

Dark is a minimal dynamically-typed language: integers, strings, arrays, objects,
functions and modules. Its defining feature is **self-hosting** — the compiler is
written in Dark itself and compiles Dark source to native ELF (Linux) or PE
(Windows) binaries, with no external toolchain.

## Quick start

```sh
# Linux — compile a .dark program to a native executable
./darkc examples/fib.dark /tmp/fib
chmod +x /tmp/fib && /tmp/fib      # fib(10) = 55

# Windows — darkc.exe is a native PE; it compiles to .exe by default
./darkc.exe examples/fib.dark fib.exe

# rebuild both compilers from their own source
./build.sh

# flags: -o <out>, -v (verbose), --target linux|windows
./darkc examples/fib.dark -o /tmp/fib --target linux -v
```

## Example

```dark
extract math

fn fib(n) {
    if (n < 2) { give n }
    give fib(n - 1) + fib(n - 2)
}

emit("fib(10) = " + to_string(fib(10)))
emit("gcd(12, 18) = " + to_string(gcd(12, 18)))
```

## Language

- **Types**: integers (i64), strings, arrays, objects, null
- **Control flow**: `if`/`else`, `while`, `skip`, `break`
- **Functions**: `fn`/`give`, recursion
- **Operators**: `+ - * / %`, `== != > < >= <=`, bitwise `& | ^ << >>`
- **Modules**: `extract math` imports a std module; calling an unimported
  function is a compile error
- **Builtins**: `emit`, `to_string`, `size`, `char_at`, `ord`, `substring`,
  `to_int`, `kind`, `push`, `slurp`, `make_exe`, `args`
- **Stdlib**: `math`, `string`, `array`, `map`, `fs`, `io`, `os`, `time`,
  `random`, `pe`

## How it works

The compiler has two parts, both written in Dark:

- `std/parser.dark` — lexer + recursive-descent parser (source → AST)
- `std/codegen.dark` — code generator (AST → native x86_64 ELF / PE)

`examples/darkc.dark` is the compiler driver: it reads the source, parses it,
resolves `extract` modules, compiles to native and reports errors.

The bootstrap is two prebuilt binaries (`darkc`, `darkc.exe`). `./build.sh`
recompiles both from source, and the result is byte-identical — a fixed point.

## Errors

```sh
$ ./darkc nope.dark
error: cannot read nope.dark            # exit 1

$ ./darkc prog_without_math.dark
error: undefined function: gcd          # exit 1 (missing `extract math`)

$ ./darkc prog.dark --bogus
error: unknown flag --bogus             # exit 2
```

## Structure

```
darkc                  — prebuilt Linux bootstrap compiler
darkc.exe              — prebuilt Windows bootstrap compiler
build.sh               — self-hosting rebuild
std/                   — standard library (Dark)
  parser.dark  codegen.dark  pe.dark  math.dark  string.dark  array.dark  ...
examples/
  darkc.dark           — compiler driver
  fib.dark             — example program
  math_demo.dark       — module system demo
```

## License

MIT (see LICENSE).
