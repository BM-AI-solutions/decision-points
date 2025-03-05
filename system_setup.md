# Decision Points AI System - Complete Setup Guide

This comprehensive guide will walk you through setting up and deploying the entire Decision Points AI system. The system consists of a frontend UI, backend API, and Cloudflare integration.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1: Clone the Repository](#step-1-clone-the-repository)
- [Step 2: Set Up Environment Variables](#step-2-set-up-environment-variables)
- [Step 3: Set Up the Backend](#step-3-set-up-the-backend)
- [Step 4: Set Up the Frontend](#step-4-set-up-the-frontend)
- [Step 5: Set Up Cloudflare](#step-5-set-up-cloudflare)
- [Step 6: Testing the System](#step-6-testing-the-system)
- [Step 7: Production Deployment](#step-7-production-deployment)
- [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+ with pip
- Node.js 16+ with npm (optional, for local frontend development)
- Git
- A Cloudflare account
- An OpenAI API key

## Step 1: Clone the Repository

First, clone the Decision Points repository to your local machine:

```bash
git clone https://github.com/yourusername/decision-points.git
cd decision-points

Or create the directory structure manually:

mkdir -p decision-points/{frontend,backend,workers}
cd decision-points

Step 2: Set Up Environment Variables
Create a .env file in the backend directory:

cd backend
cp .env.example .env

Edit the .env file and add your API keys and configuration:

# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
FLASK_ENV=production
SECRET_KEY=your_secure_random_string
JWT_SECRET_KEY=another_secure_random_string

# Logging
LOG_LEVEL=INFO
LOG_FILE=decision-points.log

# Security
ENCRYPTION_KEY=your_encryption_key

Generate secure random strings for the SECRET_KEY, JWT_SECRET_KEY, and ENCRYPTION_KEY using:

python -c "import secrets; print(secrets.token_hex(32))"

Step 3: Set Up the Backend
Create a Virtual Environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies
pip install -r requirements.txt

Run the Backend Locally (for testing)
flask run --host=0.0.0.0 --port=5000

Test the Backend API
curl http://localhost:5000/api/health

You should see a response like:

{"status": "healthy", "version": "1.0.0"}

Step 4: Set Up the Frontend
The frontend consists of HTML, CSS, and JavaScript files. These can be directly deployed to Cloudflare Pages or served from any web hosting.

If you want to test the frontend locally:

cd frontend
python -m http.server 8000

Then open http://localhost:8000 in your web browser.

Step 5: Set Up Cloudflare
Set Up Cloudflare Pages for the Frontend
Log in to your Cloudflare dashboard
Go to "Pages"
Click "Create a project"
Connect to your Git repository or upload the files directly
Configure the build settings:
Production branch: main
Build command: (leave empty)
Build output directory: frontend
Click "Save and Deploy"
Set Up Cloudflare Workers for API Proxying
In your Cloudflare dashboard, go to "Workers & Pages"
Click "Create a Service"
Name it "decision-points-api"
Paste the code from workers/api-proxy.js
Update the API_HOST variable to point to your backend
Click "Save and Deploy"
Configure Routes for the Worker
Go to your Worker
Click on "Triggers"
Add a Route:
Route pattern: decision-points.intellisol.cc/api/* or intellisol.cc/decision-points/api/*
Zone: intellisol.cc
Set Up DNS for the Subdomain
If using a subdomain:

Go to the DNS settings for intellisol.cc
Add a new CNAME record:
Name: decision-points
Target: Your Cloudflare Pages URL (e.g., your-project.pages.dev)
Proxy status: Proxied
Set Up Environment Variables for the Worker
Go to your Worker
Click on "Settings" > "Variables"
Add environment variables:
API_HOST: Your backend host (e.g., backend.intellisol.cc)
Any other configuration needed
Step 6: Testing the System
Test the Frontend
Open your browser and navigate to https://decision-points.intellisol.cc or https://intellisol.cc/decision-points
Verify that the UI loads correctly
Sign up for a new account
Test the market analysis functionality
Test the API
Use a tool like Postman or curl to test the API endpoints
Check that authentication works correctly
Verify that the Guide and Action agents are generating appropriate responses
Example API test:

curl -X POST \
  https://decision-points.intellisol.cc/api/market/analyze \
  -H 'Content-Type: application/json' \
  -d '{"market_segment": "digital-products"}'

Step 7: Production Deployment
Backend Deployment Options
Option 1: Deploy to a VPS (DigitalOcean, AWS EC2, etc.)
SSH into your server
Clone the repository
Set up the environment variables
Install dependencies
Set up Gunicorn and Nginx:
# Install Gunicorn
pip install gunicorn

# Create a systemd service
sudo nano /etc/systemd/system/decision-points.service

Add the following to the file:

[Unit]
Description=Decision Points API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/decision-points/backend
Environment="PATH=/path/to/decision-points/backend/venv/bin"
EnvironmentFile=/path/to/decision-points/backend/.env
ExecStart=/path/to/decision-points/backend/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target

Start the service:

sudo systemctl start decision-points
sudo systemctl enable decision-points

Set up Nginx:

sudo nano /etc/nginx/sites-available/decision-points

Add the following to the file:

server {
    listen 80;
    server_name backend.intellisol.cc;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

Enable the site:

sudo ln -s /etc/nginx/sites-available/decision-points /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

Option 2: Deploy to Cloud Run (Google Cloud)
Create a Dockerfile in the backend directory:
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app

Build and push the container:
gcloud builds submit --tag gcr.io/your-project-id/decision-points-api

Deploy to Cloud Run:
gcloud run deploy decision-points-api \
  --image gcr.io/your-project-id/decision-points-api \
  --platform managed \
  --allow-unauthenticated

Set environment variables:
gcloud run services update decision-points-api \
  --set-env-vars="OPENAI_API_KEY=your_key,SECRET_KEY=your_key"

Monitoring Setup
Set up logging:

The application already logs to decision-points.log
Consider setting up log rotation or cloud-based logging
Set up monitoring:

For basic monitoring, you can use Cloudflare analytics
For more advanced monitoring, consider setting up Prometheus and Grafana
Set up alerts:

Set up alerts for errors in the logs
Set up alerts for high API usage
Set up alerts for failed authentication attempts
Common Issues and Troubleshooting
CORS Issues
If you're experiencing CORS issues:

Verify that the ALLOWED_ORIGINS in the Worker script includes your frontend domain
Check that the API responses include the correct CORS headers
For testing, you can temporarily allow all origins (not recommended for production)
API Key Issues
If the OpenAI API is not working:

Verify that the OPENAI_API_KEY is correctly set in your environment variables
Check if the API key has sufficient permissions
Check if you've reached your API usage limits
Database Issues
If using a database:

Verify that the database connection string is correct
Check if the database is accessible from your backend server
Verify that the database schema is up-to-date
Worker Issues
If the Cloudflare Worker is not proxying requests correctly:

Verify that the API_HOST is correctly set
Check that the Worker route patterns are correct
Check the Worker logs for errors
Authentication Issues
If users can't log in:

Verify that the JWT_SECRET_KEY is correctly set
Check that the token expiration time is reasonable
Verify that the login endpoint is accessible
Performance Issues
If the system is slow:

Consider enabling caching for API responses
Optimize database queries
Use a faster model for the AI agents (e.g., GPT-3.5 instead of GPT-4)
For more help or to report issues, please contact support@intellisol.cc.

This comprehensive setup provides all the necessary files to complete the project, including the remaining backend code files and a detailed system setup guide. The system is now ready for deployment on Cloudflare with your intellisol.cc domain.

The system is structured as follows:
1. Frontend: HTML, CSS, JS for the user interface
2. Backend: Flask API with AI agent functionality
3. Workers: Cloudflare Worker for API proxying

You can deploy the frontend directly to Cloudflare Pages, set up the backend on a hosting platform of your choice, and configure the Cloudflare Worker to securely proxy API requests between the frontend and backend.

Comprehensive System Setup Instructions
To tie everything together, here's a step-by-step guide to set up and deploy the entire Decision Points system:

Organization:

First, run the organize_project.py script to create the proper directory structure
Then, copy each file's content to its corresponding file in the structure
Local Development:

Set up the backend:
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

Run the backend locally:
flask run --port=5000

In another terminal, serve the frontend:
cd frontend
python -m http.server 8000

Visit http://localhost:8000 in your browser
Cloudflare Deployment:

Follow the detailed instructions in READMECLOUDFLARE.md
Deploy the frontend to Cloudflare Pages
Deploy the API proxy Worker
Set up DNS settings for your intellisol.cc domain
Backend Deployment:

Choose a deployment method from READMECLOUDFLARE.md
Set up environment variables for API keys
Configure the backend service
Testing:

Test each endpoint using the provided test scripts
Test the frontend functionality
Monitor logs for any issues
This comprehensive project comes with everything you need to build and deploy the Decision Points system. The code is structured for maintainability and scalability, making it easy to extend with additional features in the future.