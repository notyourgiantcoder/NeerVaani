@echo off
chcp 65001 > nul
echo Starting FloatChat Ocean Data Explorer...
echo.

REM Check if Python is available
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import flask" > nul 2>&1
if errorlevel 1 (
    echo ERROR: Flask is not installed
    echo Installing Flask...
    pip install flask
)

python -c "import streamlit" > nul 2>&1
if errorlevel 1 (
    echo ERROR: Streamlit is not installed
    echo Installing Streamlit...
    pip install streamlit
)

echo.
echo Starting API Backend...
cd /d "%~dp0api"
if not exist "main.py" (
    echo ERROR: main.py not found in api folder
    pause
    exit /b 1
)
start "FloatChat API" cmd /k "python main.py"

echo Waiting for API to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend...
cd /d "%~dp0frontend" 
if not exist "front.py" (
    echo ERROR: front.py not found in frontend folder
    pause
    exit /b 1
)
start "FloatChat Frontend" cmd /k "streamlit run front.py"

echo.
echo FloatChat is starting up!
echo.
echo Frontend will be available at: http://localhost:8501
echo API will be available at: http://localhost:5000
echo.
echo Two command windows should have opened.
echo If they don't appear, check for errors in those windows.
echo.
echo Press any key to close this window...
pause > nul