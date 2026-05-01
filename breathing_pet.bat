@echo off
chcp 65001 >nul
cd /d "%~dp0"
python breathing_pet.py
pause
