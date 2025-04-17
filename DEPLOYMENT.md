# Cloud Deployment Guide

This guide explains how to deploy the backend to Google Cloud Run and the frontend to Firebase Hosting, using Google Secret Manager for sensitive variables and CI/CD automation via GitHub Actions.

---

## 1. Google Cloud Project Setup

### a. Prerequisites
- A Google Cloud project (note the Project ID).
- Billing enabled.
- Owner or Editor permissions.

### b. Enable Required APIs
Enable these APIs in your project:
- Cloud Run
- Artifact Registry (or Container Registry)
- Secret Manager
- IAM Service Account Credentials

### c. Create a Service Account
- Go to IAM & Admin > Service Accounts.
- Create a service account (e.g., `cloud-run-deployer`).
- Grant roles:
  - Cloud Run Admin
  - Artifact Registry Writer
  - Secret Manager Secret Accessor
- Create and download a JSON key for this account.
- Add the JSON key as a GitHub secret named `GCP_SA_KEY`.

### d. Create Artifact Registry (GCR)
```sh
gcloud artifacts repositories create backend-repo --repository-format=docker --location=us-central1
```
Or use the default GCR.

---

## 2. Secret Management (Google Secret Manager)

- For each required environment variable in `backend/.env.production.template`, create a secret:
  ```sh
  gcloud secrets create VAR_NAME --data-file=<(echo "value")
  ```
- Grant access to the Cloud Run service account:
  ```sh
  gcloud secrets add-iam-policy-binding VAR_NAME \
    --member="serviceAccount:YOUR_SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"
  ```

---

## 3. Backend Deployment (Cloud Run)

### a. Build & Push Docker Image
Handled automatically by GitHub Actions (`.github/workflows/backend-cloudrun.yml`).

### b. Deploy to Cloud Run
- The workflow deploys the image and injects secrets as environment variables.
- Secrets are mapped using the names in `.env.production.template`.

---

## 4. Frontend Deployment (Firebase Hosting)

### a. Prerequisites
- Firebase project created and Hosting enabled.
- Firebase CLI installed locally for manual deploys.

### b. Set Firebase Environment Config
- Store public keys using:
  ```sh
  firebase functions:config:set public.key="YOUR_PUBLIC_KEY"
  ```
- Add your Firebase token as a GitHub secret named `FIREBASE_TOKEN`.

### c. Build & Deploy
- The workflow in `.github/workflows/frontend-firebase.yml` builds and deploys the frontend on push to main.

---

## 5. CI/CD Automation

### a. GitHub Actions
- Backend: `.github/workflows/backend-cloudrun.yml`
- Frontend: `.github/workflows/frontend-firebase.yml`
- Both workflows require secrets to be set in your GitHub repository:
  - `GCP_PROJECT_ID`, `GCP_REGION`, `CLOUD_RUN_SERVICE`, `GCP_SA_KEY` (backend)
  - `FIREBASE_TOKEN`, `PUBLIC_KEY` (frontend)

### b. Manual Triggers
- You can trigger deployments manually via the GitHub Actions tab.

---

## 6. Environment Configuration

### Dual-Mode Billing/Subscription Enforcement

The backend supports dual-mode operation for subscription enforcement, controlled by the `BILLING_REQUIRED` environment variable:

- **Local/Docker Development:** Set `BILLING_REQUIRED=false` (the default in `backend/.env.example`). All subscription checks are bypassed and users have full access.
- **Hosted/Cloud Production:** Set `BILLING_REQUIRED=true` in your production environment (e.g., in Google Secret Manager or your cloud provider's env config). This enforces Stripe subscription checks and restricts access for non-subscribed users.

This allows seamless local development and testing without payment requirements, while ensuring proper billing enforcement in production.

- Backend: All required variables are listed in `backend/.env.production.template`. These must be created as secrets in Google Secret Manager.
- Frontend: Public keys and config are set via Firebase environment config.

---

## 6a. Environment Variable Requirements by Deployment Mode

The following table summarizes which environment variables are required for each deployment mode. See `backend/.env.example` for a complete, annotated template and `readme.md` for setup instructions.

| Variable                | Local/Self-Hosted | Hosted/SaaS (Billing) | Description / Notes                                 |
|-------------------------|:-----------------:|:---------------------:|-----------------------------------------------------|
| BILLING_REQUIRED        |        ✔️         |          ✔️           | Set to `false` for local/dev, `true` for SaaS/prod  |
| SECRET_KEY              |        ✔️         |          ✔️           | Strong random value, see below                      |
| GOOGLE_API_KEY          |        ✔️         |          ✔️           | Required for AI agents                              |
| STRIPE_API_KEY          |                   |          ✔️           | Only required if `BILLING_REQUIRED=true`            |
| STRIPE_WEBHOOK_SECRET   |                   |          ✔️           | Only required if `BILLING_REQUIRED=true`            |
| ACTION_AGENT_MODEL      |        ✔️         |          ✔️           | Optional, overrides default agent model             |
| GUIDE_AGENT_MODEL       |        ✔️         |          ✔️           | Optional, overrides default agent model             |
| ARCHON_AGENT_MODEL      |        ✔️         |          ✔️           | Optional, overrides default agent model             |
| ...other integrations   |   optional        |       optional        | See `.env.example` for more                         |

**SECRET_KEY:**  
- Used for cryptographic signing (sessions, tokens, etc.).
- Must be a strong, random value.
- Generate with:
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```
- Never share or commit your real SECRET_KEY.

**BILLING_REQUIRED:**  
- Set to `false` for local/self-hosted development (no billing, all features enabled).
- Set to `true` for hosted/SaaS deployments (billing enforced, users must subscribe).
- Stripe keys are only required if `BILLING_REQUIRED=true`.

**Best Practices:**  
- For production, use a secure secret manager (e.g., Google Secret Manager) and never commit secrets to version control.
- Reference `backend/.env.example` and `readme.md` for full setup instructions and best practices.

---

## 7. Useful Commands

- Deploy backend manually:
  ```sh
  docker build -t gcr.io/PROJECT_ID/backend:TAG ./backend
  docker push gcr.io/PROJECT_ID/backend:TAG
  gcloud run deploy SERVICE_NAME --image gcr.io/PROJECT_ID/backend:TAG --region REGION --platform managed --set-secrets ...
  ```

- Deploy frontend manually:
  ```sh
  cd frontend
  npm install
  npm run build
  firebase deploy --only hosting
  ```

---

## 8. References

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Google Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Firebase Hosting Documentation](https://firebase.google.com/docs/hosting)

---

## 9. SaaS Subscription & Payment System (Stripe)

### a. Stripe API Keys & Environment
- Set both `STRIPE_API_KEY_LIVE` and `STRIPE_API_KEY_TEST` as secrets in Google Secret Manager.
- Set `STRIPE_MODE` to `live` or `test` as appropriate for your deployment.
- Set `STRIPE_WEBHOOK_SECRET` to the signing secret from your Stripe dashboard (Developers > Webhooks).
- All keys must be present in production; deployment will fail if missing.

### b. Webhook Endpoint Configuration
- The backend exposes a secure Stripe webhook endpoint at `/webhook/stripe`.
- In your Stripe dashboard, add a webhook endpoint pointing to:
  - `https://<your-backend-domain>/webhook/stripe`
- Subscribe to these events at minimum:
  - `payment_intent.succeeded`
  - `invoice.paid`
  - `customer.subscription.updated`
- Copy the webhook signing secret and set it as `STRIPE_WEBHOOK_SECRET` in Secret Manager.
- The backend validates all webhook signatures and logs all received events.

### c. User Authentication & Management
- JWT-based authentication is enforced for all sensitive endpoints.
- JWT secret (`JWT_SECRET_KEY`) must be set as a secret in production.
- Google OAuth is supported for user registration/login.
- User and subscription data are stored in Google Cloud Datastore.

### d. Subscription Status Enforcement

- Subscription enforcement is controlled by the `BILLING_REQUIRED` environment variable. See Section 6 above for details on dual-mode configuration.

- Protected resources and endpoints should check for an active subscription using the provided helper (`has_active_subscription`).
- The `/profile` endpoint now returns a `subscription_active` field for the authenticated user.
- Extend this logic to other endpoints as needed for your business model.

### e. Security Best Practices
- Never hardcode API keys or secrets; always use environment variables and Secret Manager.
- Always validate Stripe webhook signatures.
- Use separate keys for test and live environments.
- Rotate secrets regularly and restrict access to only necessary services.

---

- [GitHub Actions for Google Cloud](https://github.com/google-github-actions/setup-gcloud)