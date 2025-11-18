@echo off
title ZKTeco ADMS Server
echo ========================================
echo ZKTeco ADMS Server
echo ========================================
echo Installing/Updating required packages...
pip install -r requirements.txt
echo ========================================
echo Starting server on http://0.0.0.0:8080
echo Press CTRL+C to stop the server
echo ========================================
python start_server.py
pause