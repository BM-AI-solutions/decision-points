@echo off
:: Script to create a Google Cloud Functions deployment package

:: Set the Python runtime version
set PYTHON_RUNTIME=python311

:: Set the Google Cloud Functions region
set GCP_REGION=us-central1

:: Set the Google Cloud Functions name
set GCP_FUNCTION_NAME=dualagent-api

:: Set the environment variables
set OPENAI_API_KEY=your_openai_api_key
set FLASK_ENV=production
set SECRET_KEY=your_secret_key

echo Creating Google Cloud Functions deployment package...

:: Create the deployment directory
if not exist gcp-deployment mkdir gcp-deployment

echo Copying main entry point and configuration files...
:: Copy main files
copy backend\main.py gcp-deployment\ /Y
copy backend\app.py gcp-deployment\ /Y
copy backend\config.py gcp-deployment\ /Y
copy backend\requirements-gcf.txt gcp-deployment\requirements.txt /Y

echo Copying backend directories...
:: Copy backend directories recursively
if exist backend\utils xcopy backend\utils gcp-deployment\utils\ /E /I /Y
if exist backend\routes xcopy backend\routes gcp-deployment\routes\ /E /I /Y
if exist backend\modules xcopy backend\modules gcp-deployment\modules\ /E /I /Y
if exist backend\models xcopy backend\models gcp-deployment\models\ /E /I /Y

echo Deployment package created in gcp-deployment directory.
echo.
echo Next steps:
echo 1. Navigate to the gcp-deployment directory
echo 2. Deploy to Google Cloud Functions using:
echo    gcloud functions deploy %GCP_FUNCTION_NAME% ^
echo      --gen2 ^
echo      --runtime=%PYTHON_RUNTIME% ^
echo      --region=%GCP_REGION% ^
echo      --source=. ^
echo      --entry-point=entrypoint ^
echo      --trigger-http ^
echo      --allow-unauthenticated ^
echo      --memory=1024MB ^
echo      --timeout=540s ^
echo      --min-instances=0 ^
echo      --max-instances=10 ^
echo      --set-env-vars="OPENAI_API_KEY=%OPENAI_API_KEY%,FLASK_ENV=%FLASK_ENV%,SECRET_KEY=%SECRET_KEY%"
echo.
echo Remember to replace the environment variables with your actual values.
