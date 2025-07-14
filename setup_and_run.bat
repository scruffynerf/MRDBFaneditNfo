@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo -----------------------------
echo Setting up MRDBFaneditNfo...
echo -----------------------------

REM Check if Python is installed
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3 from https://www.python.org/downloads/windows/
    pause
    exit /b
)

REM Create virtual environment if not exists
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
echo Installing dependencies from requirements.txt...
pip install --upgrade pip
pip install -r requirements.txt

REM Run the script
echo Running MRDB_fanedit_nfo_maker.py (change the location listed below in the bat file!)...
echo using C:\mymediafolder
echo You can also add other arguments like username/password
python MRDB_fanedit_nfo_maker.py C:\mymediafolder
