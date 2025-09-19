@echo off
REM This batch file ensures dependencies are installed and then runs the main Python application.

REM Get the directory where this batch file is located.
SET "SCRIPT_DIR=%~dp0"

REM Find python.exe on the system PATH.
for %%i in (python.exe) do set "PYTHON_EXE=%%~fi"

REM If python.exe is not found, exit.
if not defined PYTHON_EXE exit /b 1

REM Step 1: Run the requirements installer silently. This ensures the correct environment has the packages.
REM We remove output redirection to see errors, but we check ERRORLEVEL.
"%PYTHON_EXE%" "%SCRIPT_DIR%install_requirements.py"

REM Check if the installation script failed.
if %ERRORLEVEL% neq 0 (
    exit /b 1
)

REM Step 2: Run the main application, passing along any arguments from the browser.
"%PYTHON_EXE%" "%SCRIPT_DIR%idm.py" --from-browser %*