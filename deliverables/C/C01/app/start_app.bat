@echo off
rem Double-click: start the site (http://localhost:8503) and open the browser. Closing this window stops the server.
cd /d "%~dp0"

rem Already running? Just open the browser.
netstat -ano | findstr /R /C:"127.0.0.1:8503 .*LISTENING" >nul
if %errorlevel%==0 (
  start "" http://localhost:8503
  exit /b
)

start "" /min cmd /c "timeout /t 6 >nul & start http://localhost:8503"
python -X utf8 -m streamlit run app.py --server.headless true
pause
