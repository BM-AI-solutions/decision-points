# Deploying Dual Agent System to Google Cloud Functions and Cloudflare

This guide provides step-by-step instructions for deploying the Dual Agent System to Google Cloud Functions and Cloudflare. It covers all necessary steps from setting up your Google Cloud project to configuring Cloudflare for serving your application.

## Prerequisites

1. A Google Cloud Platform account
2. A Cloudflare account with your domain (intellisol.cc) already added
3. Google Cloud SDK installed on your local machine
4. Git repository for your project (optional but recommended)

## 1. Setting Up Google Cloud Project

### 1.1 Create or Select a Google Cloud Project

```bash
# List existing projects
gcloud projects list

# Create a new project (optional)
gcloud projects create [YOUR_PROJECT_ID] --name="Dual Agent System"

# Set the active project
gcloud config set project [YOUR_PROJECT_ID]
```

### 1.2 Enable Required APIs

```bash
# Enable Cloud Functions API
gcloud services enable cloudfunctions.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Enable Artifact Registry API
gcloud services enable artifactregistry.googleapis.com
```

## 2. Preparing Your Backend for Deployment

### 2.1 Create Deployment Package Structure

Create a deployment directory with the required files:

```
gcp-deployment/
├── main.py                # Cloud Functions entry point (already created)
├── app.py                 # Your main Flask application
├── config.py              # Configuration file
├── requirements-gcf.txt   # Dependencies for GCP (already created)
└── other backend folders  # utils, routes, modules, models
```

### 2.2 Copy Backend Files to Deployment Directory

```bash
# Create deployment directory
mkdir -p gcp-deployment

# Copy necessary files
cp backend/main.py gcp-deployment/
cp backend/app.py gcp-deployment/
cp backend/config.py gcp-deployment/
cp backend/requirements-gcf.txt gcp-deployment/requirements.txt

# Copy backend directories (recursive)
cp -r backend/utils gcp-deployment/
cp -r backend/routes gcp-deployment/
cp -r backend/modules gcp-deployment/
cp -r backend/models gcp-deployment/
```

## 3. Deploying to Google Cloud Functions

### 3.1 Deploy the Function

```bash
# Navigate to your deployment directory
cd gcp-deployment

# Deploy to Google Cloud Functions
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
  --set-env-vars="OPENAI_API_KEY=your_openai_api_key,FLASK_ENV=production,SECRET_KEY=your_secure_random_key"
```

### 3.2 Verify Deployment

```bash
# List deployed functions
gcloud functions list

# Get function details
gcloud functions describe dualagent-api --region=us-central1
```

Note down the function URL, it will look like:
`https://us-central1-your-project-id.cloudfunctions.net/dualagent-api`

Test the function with:
```bash
curl https://us-central1-your-project-id.cloudfunctions.net/dualagent-api/api/health
```

## 4. Deploying Frontend to Cloudflare Pages

### 4.1 Prepare Your Frontend for Deployment

Ensure your frontend code is in a Git repository (GitHub, GitLab, or Bitbucket).

### 4.2 Set Up Cloudflare Pages Project

1. Log in to your Cloudflare dashboard
2. Navigate to "Pages"
3. Click "Create a project"
4. Connect to your Git provider and select your repository
5. Configure build settings:
   - Build command: (leave empty for static site)
   - Build output directory: `frontend`
   - Environment variables: (none needed)
6. Click "Save and Deploy"

### 4.3 Configure Custom Domain

1. In your Pages project, go to "Custom domains"
2. Click "Set up a custom domain"
3. Enter `dualagent.intellisol.cc` and click "Continue"
4. Cloudflare will automatically configure the DNS for you
5. Wait for the domain to be activated (this may take a few minutes)

## 5. Setting Up Cloudflare Worker for API Proxy

### 5.1 Create and Deploy the Worker

1. In your Cloudflare dashboard, navigate to "Workers & Pages"
2. Click "Create a Service"
3. Name it "dualagent-api-proxy"
4. Click "Create service"
5. Select the "Quick edit" option
6. Replace the code with the modified API proxy code (workers/api-proxy.js)
7. Update the `API_HOST` value to your actual Google Cloud Function URL (without the https://)
8. Click "Save and deploy"

### 5.2 Configure Worker Routes

1. In your Worker's dashboard, navigate to "Triggers"
2. Click "Add route"
3. Enter the route pattern: `dualagent.intellisol.cc/api/*`
4. Zone: intellisol.cc (Zone ID: 83f6f0d954589cd372dfcdbe37ba27c0)
5. Click "Add route"

## 6. Testing Your Deployment

### 6.1 Test the Frontend

Open a browser and navigate to `https://dualagent.intellisol.cc`

### 6.2 Test the API

```bash
# Test the health endpoint
curl https://dualagent.intellisol.cc/api/health

# Test the config endpoint
curl https://dualagent.intellisol.cc/api/config
```

## 7. Maintenance and Updates

### 7.1 Updating the Backend

```bash
# Make changes to your code
# ...

# Redeploy the function
cd gcp-deployment
# Update necessary files
gcloud functions deploy dualagent-api --gen2 --source=. [other flags as before]
```

### 7.2 Updating the Frontend

Simply push changes to your Git repository. Cloudflare Pages will automatically detect changes and rebuild/deploy your site.

### 7.3 Updating the Cloudflare Worker

1. In your Cloudflare dashboard, go to your Worker
2. Click on "Quick edit"
3. Make necessary changes
4. Save and deploy

## 8. Monitoring and Troubleshooting

### 8.1 Google Cloud Functions Logs

```bash
# View logs for your function
gcloud functions logs read dualagent-api --region=us-central1
```

Or use the Google Cloud Console:
1. Go to Cloud Functions
2. Select your function
3. Click on "Logs"

### 8.2 Cloudflare Workers Logs

1. In your Cloudflare dashboard, go to "Workers"
2. Select your worker
3. Navigate to "Logs"

## 9. Cost Management

### 9.1 Google Cloud Functions

- Free tier: 2 million invocations per month
- Beyond free tier: $0.40 per million invocations
- Compute time: $0.000000231 per GB-second

Set up a budget alert to monitor costs:
1. Go to Billing in Google Cloud Console
2. Select "Budgets & alerts"
3. Click "Create budget"

### 9.2 Cloudflare

- Pages: Free for personal projects
- Workers: 100,000 requests per day on the free plan
- Additional requests: $0.50 per million requests

## 10. Security Considerations

### 10.1 API Keys and Secrets

- Never store API keys in your code
- Use environment variables for all sensitive information
- Rotate keys periodically

### 10.2 CORS and API Security

- The Cloudflare Worker handles CORS headers
- Consider implementing additional security like rate limiting or API key authentication for production use

### 10.3 Cloudflare Security Features

Consider enabling:
- Cloudflare WAF (Web Application Firewall)
- Bot protection
- HTTPS enforcement
- Automatic HTTPS rewrites

## Conclusion

Your Dual Agent System should now be fully deployed with:
- Backend running on Google Cloud Functions
- Frontend hosted on Cloudflare Pages
- API requests securely proxied through Cloudflare Workers
- Custom subdomain configuration (dualagent.intellisol.cc)

For any issues, check the logs in both Google Cloud and Cloudflare, and refer to their respective documentation for advanced configurations.
