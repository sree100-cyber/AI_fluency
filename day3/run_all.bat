@echo off
REM Automated workflow: set up venv, install, run both scripts, save logs to outputs\
if not exist .venv ( python -m venv .venv )
call .venv\Scripts\activate
pip install -q -r requirements.txt
if "%ANTHROPIC_API_KEY%"=="" ( echo Set ANTHROPIC_API_KEY first: set ANTHROPIC_API_KEY=your-key & exit /b 1 )
python no_tool.py
python with_tool.py
echo.
echo Done. Take screenshots of both runs and save them in the screenshots folder.
