@echo off
cd /d %~dp0
if not exist venv (
    echo Creating virtual environment...
    py -m venv venv
    if errorlevel 1 python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
python -m streamlit run app.py
pause
