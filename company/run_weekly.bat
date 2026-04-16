@echo off
chcp 65001 > nul
cd /d "C:\Users\lian1\Documents\Work\core\company"
set PYTHONUTF8=1

.\venv\Scripts\python.exe weekly_runner.py
