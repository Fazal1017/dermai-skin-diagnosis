@echo off
REM Skin Diagnosis Backend - Windows Startup Script

echo.
echo ====================================
echo Skin Diagnosis Backend Server
echo ====================================
echo.

REM Activate virtual environment
call ..\venv\Scripts\activate.bat

REM Run migrations if needed
echo Running database migrations...
python manage.py migrate --noinput

REM Start server
echo.
echo Starting development server at http://127.0.0.1:8000
echo.
echo API Endpoints:
echo   - Predict: http://127.0.0.1:8000/api/diagnoses/predict/
echo   - List: http://127.0.0.1:8000/api/diagnoses/
echo   - Admin: http://127.0.0.1:8000/admin/
echo.
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver 0.0.0.0:8000
