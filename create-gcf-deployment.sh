#!/bin/bash

# Script to create a Google Cloud Functions deployment package

# Set the Python runtime version
PYTHON_RUNTIME="python311"

# Set the Google Cloud Functions region
GCP_REGION="us-central1"

# Set the Google Cloud Functions name
GCP_FUNCTION_NAME="dualagent-api"

# Set the environment variables
OPENAI_API_KEY="your_openai_api_key"
FLASK_ENV="production"
SECRET_KEY="your_secret_key"

echo "Creating Google Cloud Functions deployment package..."

# Create the deployment directory
mkdir -p gcp-deployment

echo "Copying main entry point and configuration files..."

# Copy main files
cp backend/main.py gcp-deployment/
cp backend/app.py gcp-deployment/
cp backend/config.py gcp-deployment/
cp backend/requirements-gcf.txt gcp-deployment/requirements.txt

echo "Copying backend directories..."

# Copy backend directories recursively
if [ -d "backend/utils" ]; then
  cp -r backend/utils gcp-deployment/
else
  echo "Warning: backend/utils directory not found."
fi

if [ -d "backend/routes" ]; then
  cp -r backend/routes gcp-deployment/
else
  echo "Warning: backend/routes directory not found."
fi

if [ -d "backend/modules" ]; then
  cp -r backend/modules gcp-deployment/
else
  echo "Warning: backend/modules directory not found."
fi

if [ -d "backend/models" ]; then
  cp -r backend/models gcp-deployment/
else
  echo "Warning: backend/models directory not found."
fi

echo "Deployment package created in gcp-deployment directory."
echo

echo "Next steps:"
echo "1. Navigate to the gcp-deployment directory"
echo "2. Deploy to Google Cloud Functions using:"
echo "   gcloud functions deploy ${GCP_FUNCTION_NAME} \\"
echo "     --gen2 \\"
echo "     --runtime=${PYTHON_RUNTIME} \\"
echo "     --region=${GCP_REGION} \\"
echo "     --source=. \\"
echo "     --entry-point=entrypoint \\"
echo "     --trigger-http \\"
echo "     --allow-unauthenticated \\"
echo "     --memory=1024MB \\"
echo "     --timeout=540s \\"
echo "     --min-instances=0 \\"
echo "     --max-instances=10 \\"
echo "     --set-env-vars=\"OPENAI_API_KEY=${OPENAI_API_KEY},FLASK_ENV=${FLASK_ENV},SECRET_KEY=${SECRET_KEY}\""
echo

echo "Remember to replace the environment variables with your actual values."
