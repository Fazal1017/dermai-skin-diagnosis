# Skin Diagnosis Backend - PowerShell Startup Script

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Skin Diagnosis Backend Server" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ..\venv\Scripts\Activate.ps1

# Run migrations if needed
Write-Host ""
Write-Host "Running database migrations..." -ForegroundColor Yellow
python manage.py migrate --noinput

# Start server
Write-Host ""
Write-Host "Starting development server..." -ForegroundColor Green
Write-Host ""
Write-Host "Server is ready! Access it at:" -ForegroundColor Cyan
Write-Host "  - API Root: http://127.0.0.1:8000/api/" -ForegroundColor White
Write-Host "  - Predict: http://127.0.0.1:8000/api/diagnoses/predict/" -ForegroundColor White
Write-Host "  - Admin: http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver 0.0.0.0:8000
