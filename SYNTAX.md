# Dark — справочник по синтаксису

Dark — минималистичный динамически-типизированный язык для Linux x86_64.
Программа — последовательность инструкций, исполняемых сверху вниз.
Компилятор написан на самом Dark и порождает нативные ELF-бинарники.

## Комментарии

```dark
// однострочный комментарий
```

## Типы данных

| Тип | Пример | Примечание |
|---|---|---|
| число | `42`, `-7`, `0x1F` | целое (64-bit), hex-литерал `0x…` |
| строка | `"hello"`, `"a\nb"` | экранирование: `\n \t \" \\` |
| массив | `[1, 2, 3]` | гетерогенный |
| объект | `{"a": 1, "b": 2}` | словарь; поля через `obj["key"]` |
| null | `null` | отсутствие значения |

## Переменные и присваивание

```dark
x = 42
x = x + 1
arr[i] = v        // запись в массив
obj["key"] = v    // запись в объект по строковому ключу
```

## Операторы

По приоритету (от низкого к высокому):

```dark
|                    // побитовое ИЛИ
^                    // исключающее ИЛИ
&                    // побитовое И
== != > < >= <=      // сравнение
<< >>                // сдвиг влево / вправо
+ -                  // сложение / конкатенация строк
* / %                // умножение / целочисленное деление / остаток
- ! ~                // унарные: минус / НЕ / побитовое НЕ
() []                // вызов / индексация
```

`&&` и `||` работают как логические над 0/1 (токенизируются в `&`/`|`).
Строки конкатенируются `+`: `"a" + "b"` → `"ab"`.

## Управление

```dark
if (x > 0) {
    emit("positive")
} else {
    emit("non-positive")
}

while (i < 10) {
    i = i + 1
    if (i == 5) { skip }    // continue
    if (i == 8) { break }
}

for (x of [1, 2, 3]) {     // цикл по элементам
    emit(x)
}

for (i, x of ["a", "b"]) { // цикл с индексом
    emit(to_string(i) + x)
}

exit_code(0)                // завершить процесс с кодом
```

## Функции

```dark
fn add(a, b) {
    give a + b
}

fn factorial(n) {
    if (n <= 1) { give 1 }
    give n * factorial(n - 1)    // рекурсия
}
```

Функции — значения первого класса: их можно передавать в другие функции.

```dark
extract array

fn double(x) { give x * 2 }
emit(join(map([1, 2, 3], double), ","))   // 2,4,6
```

## Модули

```dark
extract math          // грузит std/math.dark
```

`extract` делает функции модуля доступными. Вызов функции из
неподключённого модуля — ошибка компиляции:

```sh
$ ./darkc prog.dark
error: undefined function: gcd
```

## Встроенные функции

| Функция | Описание |
|---|---|
| `emit(x)` | печать с новой строкой |
| `to_string(n)` | число → строка |
| `to_int(s)` | строка → число |
| `size(x)` | длина строки / массива |
| `char_at(s, i)` | символ строки как строка |
| `ord(s)` | код первого символа |
| `substring(s, a, b)` | подстрока `[a, b)` |
| `kind(v)` | 1 — число, 2 — строка, 4 — массив, 6 — объект/null |
| `push(arr, x)` | добавить элемент в массив |
| `keys(obj)` | массив ключей объекта |
| `values(obj)` | массив значений объекта |
| `slurp(path)` | файл → строка |
| `make_exe(path, bytes)` | записать байтовый массив в файл |
| `args()` | массив аргументов командной строки |

## Компиляция

```sh
./darkc program.dark /tmp/program    # скомпилировать в нативный ELF
./darkc program.dark -o /tmp/p -v    # флаги: -o <out>, -v (verbose)
./build.sh                           # пересобрать компилятор из исходников
```

Коды возврата: `0` — успех, `1` — ошибка компиляции, `2` — неверные флаги.

## Стандартная библиотека (`std/`)

| Модуль | Назначение |
|---|---|
| `math` | gcd, lcm, is_prime, fibonacci, sum, product, mean, median, clamp, sign, sqrt_int, fact |
| `string` | upper, lower, split, join, trim, replace, contains, index_of, starts_with, ends_with, … |
| `array` | range, map, filter, reduce, zip, flatten, unique, chunk, take, drop, sum, min, max |
| `map` | has_key, get_or, size_map, merge, to_pairs |
| `json` | json_stringify, json_parse (JSON → объекты и обратно) |
| `fs` | read_text, write_text, read_lines, ls, mk, rm, is_file, is_dir, copy, move |
| `io` | read_file, write_file, read_lines, exists, append_file |
| `os` | os_name, shell, argv, getenv, setenv, exit, cwd, hostname, uname, cpu_count |
| `time` | now, now_sec, sleep_ms, sleep_sec |
| `random` | rand, rand_int, rand_bool, chance, pick, shuffle |
| `parser` | tokenize, parse_program (исходник → AST) |
| `codegen` | compile_auto (AST → нативный ELF) |
| `pe` | to_le2/4/8, join_arrays, zeros, make_pe |

> Прочие модули (`native`, `net`, `gui`, `html`, `http`) написаны под старый
> интерпретатор и переносятся на self-hosted рантайм.

Пример:

```dark
extract math

emit(gcd(12, 18))       // 6
emit(is_prime(17))      // 1
emit(fibonacci(10))     // 55
```

## Как это устроено

Компилятор состоит из двух частей, обе на Dark:

- `std/parser.dark` — лексер + парсер (рекурсивный спуск) → AST
- `std/codegen.dark` — кодогенератор AST → нативный x86_64 ELF

`examples/darkc.dark` — драйвер: читает исходник, парсит, резолвит `extract`,
компилирует и выводит ошибки. Bootstrap — один прекомпилированный бинарник
`darkc`; `./build.sh` пересобирает его из исходников (неподвижная точка —
результат байт-в-байт идентичен).
