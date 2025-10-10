@echo off
echo 🌊 Starting FloatChat Ocean Data Explorer...
echo.

echo 📊 Starting API Backend...
cd /d "%~dp0\api"
start "FloatChat API" cmd /k "python main.py"

timeout /t 3 /nobreak > nul

echo 🖥️ Starting Frontend...
cd /d "%~dp0\frontend" 
start "FloatChat Frontend" cmd /k "streamlit run front.py"

echo.
echo ✅ FloatChat is starting up!
echo 🌐 Frontend will be available at: http://localhost:8501
echo 🔧 API will be available at: http://localhost:5000
echo.
echo Press any key to close this window...
pause > nul