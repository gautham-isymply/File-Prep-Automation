@echo off
setlocal
if "%~1"=="" (
  echo Drag the downloaded attendance .xls file onto this .bat file.
  echo Or run: run_prepare_sgp.bat "C:\path\to\attendance.xls"
  pause
  exit /b 1
)
where py >nul 2>&1
if not errorlevel 1 (
  py -3 "%~dp0prepare_sgp.py" "%~1"
) else (
  python "%~dp0prepare_sgp.py" "%~1"
)
if errorlevel 1 echo Please review the error messages above.
pause
