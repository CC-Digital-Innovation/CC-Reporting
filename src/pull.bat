@echo off
git fetch origin
git pull
.\.venv\Scripts\python.exe .\src\wrapper.py
