@echo off
cd /d "%~dp0"
py -m waitress --listen=0.0.0.0:5000 app:app
pause
