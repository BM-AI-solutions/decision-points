#!/bin/bash

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
fi

if [ -d "backend/routes" ]; then
  cp -r backend/routes gcp-deployment/
fi

if [ -d "backend/modules" ]; then
  cp -r backend/modules gcp-deployment/
fi

if [ -d "backend/models" ]; then
  cp -r backend/models gcp-deployment/
fi

echo "Deployment package created in gcp-deployment directory."
echo
echo "Next steps:"
echo "1. Navigate to the gcp-deployment directory"
echo "2. Deploy to Google Cloud Functions using:"
echo "   gcloud functions deploy dualagent-api \\"
echo "     --gen2 \\"
echo "     --runtime=python39 \\"
echo "     --region=us-central1 \\"
echo "     --source=. \\"
echo "     --entry-point=entrypoint \\"
echo "     --trigger-http \\"
echo "     --allow-unauthenticated \\"
echo "     --memory=1024MB \\"
echo "     --timeout=540s \\"
echo "     --min-instances=0 \\"
echo "     --max-instances=10 \\"
echo "     --set-env-vars=\"OPENAI_API_KEY=your_api_key,FLASK_ENV=production,SECRET_KEY=your_secret_key\""
echo
echo "Remember to replace the environment variables with your actual values."
