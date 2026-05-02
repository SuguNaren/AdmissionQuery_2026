@echo off
setlocal

set "RUN_SCRIPT=%~dp0run.py"
set "PYEXE="

if defined PYTHON_BIN if exist "%PYTHON_BIN%" set "PYEXE=%PYTHON_BIN%"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python313\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python312\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python311\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python310\python.exe"
if not defined PYEXE if exist "C:\Python313\python.exe" set "PYEXE=C:\Python313\python.exe"
if not defined PYEXE if exist "C:\Python312\python.exe" set "PYEXE=C:\Python312\python.exe"
if not defined PYEXE if exist "C:\Python311\python.exe" set "PYEXE=C:\Python311\python.exe"
if not defined PYEXE if exist "C:\Python310\python.exe" set "PYEXE=C:\Python310\python.exe"
if not defined PYEXE if exist "C:\Program Files\IBM\SPSS Statistics\Python3\python.exe" set "PYEXE=C:\Program Files\IBM\SPSS Statistics\Python3\python.exe"

if not defined PYEXE (
    for %%P in (py.exe python.exe python3.exe) do (
        for /f "delims=" %%I in ('where %%P 2^>nul') do (
            echo %%I | findstr /I /C:"WindowsApps" >nul
            if errorlevel 1 if not defined PYEXE set "PYEXE=%%I"
        )
    )
)

if not defined PYEXE (
    echo Python was not found on this machine.
    echo Install Python 3.10+ or set PYTHON_BIN to a valid python.exe path.
    exit /b 1
)

"%PYEXE%" "%RUN_SCRIPT%" %*
exit /b %errorlevel%
