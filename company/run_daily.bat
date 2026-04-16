@echo off
cd /d "C:\Users\lian1\Documents\Work\core\company"
set PYTHONUTF8=1
.\venv\Scripts\python.exe -m core.ops_loop daily "사장님도구함" >> "C:\Users\lian1\Documents\Work\core\company\logs\daily.log" 2>&1
.\venv\Scripts\python.exe -m core.ops_loop daily "스마트스토어 셀러 AI 콘텐츠 납품" >> "C:\Users\lian1\Documents\Work\core\company\logs\daily.log" 2>&1
