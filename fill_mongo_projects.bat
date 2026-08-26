@echo off
cd DigitalTwinWebsite

REM Activate virtual environment and run fill_mongo_projects.py
echo Preparing environment for fill_mongo_projects.py...

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo Installing requirements...
    venv\Scripts\pip install -r requirements.txt
)

REM Activate virtual environment
call venv\Scripts\activate.bat

cd ..
REM Load environment variables from .env.local file
if exist ".env.local" (
    echo Loading environment variables from .env.local file...
    for /f "usebackq tokens=1,* delims==" %%a in (".env.local") do (
        set "%%a=%%b"
    )
) else (
    echo Warning: .env.local file not found. Using default values.
    set MONGO_URI=mongodb://localhost:27017
    set MONGO_DBNAME=digitalTwin
    set SECRET_KEY='secret'
)

REM Run fill_mongo_projects.py
echo Running fill_mongo_projects.py...
cd DigitalTwinWebsite/code
python fill_mongo_projects.py --owner x %*
PAUSE
