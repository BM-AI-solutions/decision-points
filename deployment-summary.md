# Dual Agent System - Cloudflare & Google Cloud Functions Deployment

This document summarizes the deployment setup for the Dual Agent System to Cloudflare (frontend and API proxy) and Google Cloud Functions (backend). All necessary files and configurations have been prepared.

## 1. Files Created/Modified for Deployment

### Backend (Google Cloud Functions)

- **`backend/main.py`**: Entry point for Google Cloud Functions, adapts Flask to GCF environment
- **`backend/requirements-gcf.txt`**: Dependencies specific for Google Cloud Functions

### Frontend (Cloudflare Pages)

- **`frontend/js/config.js`**: Configuration file for frontend environment settings
- **`frontend/js/api.js`**: API client for communicating with the backend through Cloudflare Workers
- **Updated `frontend/index.html`**: Added references to new JS files

### Cloudflare Workers

- **Updated `workers/api-proxy.js`**: Modified to proxy requests to Google Cloud Functions

### Deployment Scripts

- **`create-gcf-deployment.bat`**: Windows script to package files for GCF deployment
- **`create-gcf-deployment.sh`**: Linux/Mac script to package files for GCF deployment

### Documentation

- **`cloudflare-gcp-deployment-guide.md`**: Comprehensive guide with step-by-step instructions

## 2. Deployment Overview

### Step 1: Deploy Backend to Google Cloud Functions

1. Run the appropriate deployment script based on your OS:
   ```
   # Windows
   create-gcf-deployment.bat
   
   # Linux/Mac
   chmod +x create-gcf-deployment.sh
   ./create-gcf-deployment.sh
   ```

2. Navigate to the created `gcp-deployment` directory and deploy using gcloud:
   ```
   cd gcp-deployment
   
   gcloud functions deploy dualagent-api \
     --gen2 \
     --runtime=python39 \
     --region=us-central1 \
     --source=. \
     --entry-point=entrypoint \
     --trigger-http \
     --allow-unauthenticated \
     --memory=1024MB \
     --timeout=540s \
     --min-instances=0 \
     --max-instances=10 \
     --set-env-vars="OPENAI_API_KEY=your_api_key,FLASK_ENV=production,SECRET_KEY=your_secret_key"
   ```

3. Note the function URL provided after deployment (e.g., `https://us-central1-your-project-id.cloudfunctions.net/dualagent-api`)

### Step 2: Deploy Frontend to Cloudflare Pages

1. Push your code to a Git repository (GitHub, GitLab, or Bitbucket)

2. In Cloudflare dashboard:
   - Go to Pages
   - Create a new project
   - Connect to your Git repository
   - Configure build settings:
     - Build command: (leave empty - static site)
     - Build output directory: `frontend`
   - Click "Save and Deploy"

3. Set up custom domain `dualagent.intellisol.cc` in the Cloudflare Pages project

### Step 3: Deploy API Proxy to Cloudflare Workers

1. Update the `workers/api-proxy.js` file with your actual GCF URL:
   ```javascript
   const API_HOST = 'us-central1-your-project-id.cloudfunctions.net';  // Update this
   ```

2. In Cloudflare dashboard:
   - Go to Workers & Pages
   - Create a new service named "dualagent-api-proxy"
   - Copy and paste the updated `workers/api-proxy.js` code
   - Deploy the worker

3. Configure Worker routes:
   - Add route: `dualagent.intellisol.cc/api/*`
   - Zone: intellisol.cc (Zone ID: 83f6f0d954589cd372dfcdbe37ba27c0)

## 3. Testing the Deployment

1. Visit `https://dualagent.intellisol.cc` to verify the frontend is working
2. Test API endpoints:
   ```
   curl https://dualagent.intellisol.cc/api/health
   curl https://dualagent.intellisol.cc/api/config
   ```

## 4. Maintenance

- **Backend updates**: Redeploy using the same gcloud command after making changes
- **Frontend updates**: Push changes to your Git repository; Pages will auto-deploy
- **Worker updates**: Edit the worker code in the Cloudflare dashboard

## 5. Additional Resources

- Full deployment guide: [cloudflare-gcp-deployment-guide.md](cloudflare-gcp-deployment-guide.md)
- GCP documentation: [https://cloud.google.com/functions/docs](https://cloud.google.com/functions/docs)
- Cloudflare Pages: [https://developers.cloudflare.com/pages](https://developers.cloudflare.com/pages)
- Cloudflare Workers: [https://developers.cloudflare.com/workers](https://developers.cloudflare.com/workers)

## 6. Important Notes

- Remember to update environment variables with real values
- Update API_HOST in the worker script with your actual GCF URL
- Set appropriate CORS headers if needed
- Consider implementing rate limiting and authentication for production use
