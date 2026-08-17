@echo off
setlocal enabledelayedexpansion
set "DARKC=darkc.exe"
set "TMPD=%TEMP%\darkrepl"
if not exist "%TMPD%" mkdir "%TMPD%"

echo Dark REPL (Windows)
echo   expression     -^> evaluate and print
echo   ^> statement    -^> run as-is (no auto-print)
echo   fn name^(...^)  -^> define a function (persists for the session)
echo   quit / exit    -^> leave
echo.

set "PREAMBLE="

:loop
set "line="
set /p "line=^> "
if not defined line goto loop
if /i "!line!"=="quit" goto end
if /i "!line!"=="exit" goto end
if /i "!line!"=="q" goto end

set "first=!line:~0,3!"
if /i "!first!"=="fn " (
    set "PREAMBLE=!PREAMBLE!!line!"^
"
    echo   defined
    goto loop
)

set "second=!line:~0,1!"
if "!second!"==">" (
    set "prog=!PREAMBLE!^
!line:~1!"
) else (
    set "prog=!PREAMBLE!^
emit^(!line!^)"
)

> "%TMPD%\prog.dark" echo !prog!
"%DARKC%" "%TMPD%\prog.dark" "%TMPD%\prog.exe" >nul 2>"%TMPD%\err.txt"
if errorlevel 1 (
    echo error:
    type "%TMPD%\err.txt"
    goto loop
)
"%TMPD%\prog.exe"
echo.
goto loop

:end
endlocal
