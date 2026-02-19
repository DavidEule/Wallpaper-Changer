@echo off
setlocal

REM Always work from the folder this launcher is in
set "DIR=%~dp0"
set "PYFILE=%DIR%wallpaper.py"

REM Safety: refuse if the main script is missing
if not exist "%PYFILE%" (
  echo ERROR: "%PYFILE%" not found.
  echo Put Run-Wallpaper-Admin.cmd in the same folder as wallpaper.py
  pause
  exit /b 1
)

REM Prefer the Python launcher (py). If not available, fallback to python.exe.
where py >nul 2>nul
if %errorlevel%==0 (
  set "PYEXE=py"
  set "PYARGS=-3 ""%PYFILE%"""
) else (
  set "PYEXE=python"
  set "PYARGS=""%PYFILE%"""
)

REM Elevate and run python directly, with WorkingDirectory = script folder
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$d = '%DIR%'; $exe = '%PYEXE%'; $args = '%PYARGS%'; Start-Process -Verb RunAs -FilePath $exe -ArgumentList $args -WorkingDirectory $d"

endlocal