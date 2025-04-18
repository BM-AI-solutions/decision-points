# Decision Points AI System
![Decision Points AI Logo](https://i.imgur.com/5AVm5uo.jpeg)
## Summary/Overview

Decision Points is an AI-powered system designed to automate the creation, deployment, and monetization of online businesses. Utilizing specialized agents (Guide, Action, Archon, etc.), it analyzes markets, implements business models and features, generates branding materials, and projects cash flow, requiring minimal human input. The system supports flexible model selection for each agent, including integration with Google Gemini AI and OpenAI models, and is designed for both developers (setup/maintenance) and end-users (web UI for business creation).

## Key Features

*   **Market Analysis:** In-depth analysis of potential business markets.
*   **Business & Feature Implementation:** Automated setup of core business logic and features.
*   **Branding Generation:** Creates branding elements for the new business.
*   **Automated Deployment:** Supports deployment to multiple targets (Docker, Cloud Platforms, VPS).
*   **Cash Flow Projection:** Estimates potential financial performance.
*   **User Authentication:** Secure user management.
*   **Stripe-Based Monetization:** Integration with Stripe for payment processing.
*   **Chat Interaction:** User interaction facilitated through a chat interface.
*   **Flexible Model Selection:** Configure which LLM (e.g., Gemini, GPT-4o) each agent uses via environment variables.

## Technology Stack

*   **Backend:**
    *   Language: Python (3.8+/3.9)
    *   Framework: Flask
    *   Server: Gunicorn / uWSGI
    *   AI: Google Gemini API, Langchain, OpenAI (configurable per agent)
    *   Database (Deployment Dependent): Google Cloud Datastore OR PostgreSQL (with SQLAlchemy/Alembic) OR MongoDB
    *   Caching (Deployment Dependent): Cachetools OR Redis
*   **Frontend:**
    *   Stack: Vanilla HTML, CSS, JavaScript
    *   Build Tools: PostCSS, Terser
*   **Workers:**
    *   Environment: Node.js (e.g., Cloudflare Workers for API proxy)
*   **Containerization:** Docker, Docker Compose
*   **Payments:** Stripe

## Architecture Overview

The system employs a Client-Server architecture, featuring a static frontend communicating with a Flask-based backend API. An optional Cloudflare Worker layer can act as an API proxy. The backend utilizes a multi-agent design to handle different aspects of business creation, with each agent's LLM model configurable via environment variables. The architecture supports multiple deployment targets, including Docker Compose for local/simple deployments, Google Cloud Functions combined with Cloudflare, or a self-hosted Linux VPS.

## Installation

### Local Setup

Two primary methods are supported for local development and testing:

1.  **Docker Desktop (Recommended Method):**
    *   **Prerequisites:** Ensure Docker Desktop is installed and running.
    *   **Environment Setup:**
        *   Copy the root `.env.example` file to `.env`: `cp .env.example .env`
        *   Edit the new `.env` file and fill in the necessary values, especially `SECRET_KEY` and `GEMINI_API_KEY`. For local development, `BILLING_REQUIRED=false` is usually appropriate. Ensure `VITE_API_BASE_URL` is set to `http://localhost:5000` (the default in `.env.example`).
    *   **Run:**
        ```bash
        docker compose -f docker-compose.dev.yml up --build -d
        ```
        *   Use `-d` to run in detached mode (background). Omit it to see logs directly.
        *   The `--build` flag ensures images are rebuilt if Dockerfiles or contexts change.
    *   **Access:**
        *   Frontend: `http://localhost:8000` (served by Vite dev server with hot-reloading)
        *   Backend API: `http://localhost:5000` (Flask dev server with hot-reloading)
    *   **How it Works:**
        *   `docker-compose.dev.yml` defines `frontend` and `backend` services.
        *   It uses multi-stage Dockerfiles optimized for development (volume mounts for code, dev servers).
        *   Services are connected on a Docker network (`appnet`). The frontend container *can* reach the backend container at `http://backend:5000`, but the frontend JavaScript code running in your **browser** accesses the API via the host machine's mapped port: `http://localhost:5000` (as configured by `VITE_API_BASE_URL` in your `.env` file).
        *   The root `.env` file provides environment variables to the services.
        *   No Google Cloud SDK/credentials needed locally; an in-memory database is used.
    *   **Stopping:**
        ```bash
        docker compose -f docker-compose.dev.yml down
        ```
    *   **Stripe Webhooks (Optional):** To forward Stripe webhooks during development:
        ```bash
        stripe listen --forward-to localhost:5000/api/stripe/webhook
        ```
        (Requires [Stripe CLI](https://stripe.com/docs/stripe-cli))

### Using Development vs. Production Docker Configurations

*   **Development (`docker-compose.dev.yml`):** Use this for local development (hot-reloading, dev servers). Commands above apply.
*   **Production (`docker-compose.prod.yml`):** Builds optimized production images (Gunicorn backend, Nginx frontend). Access frontend at `http://localhost:8000`. Run with:
    ```bash
    docker compose -f docker-compose.prod.yml up --build -d
    ```
    *(Note: Production setup might require additional configuration, e.g., database, secrets management. See `DEPLOYMENT.md`)*

---

2.  **Alternative: Manual Python Setup (venv):**
    *   This method runs the backend directly on your host machine using a Python virtual environment. It requires manual setup of Python and dependencies.
    *   Ensure Python 3.8+ or 3.9+ is installed.
    *   Navigate to the `backend` directory: `cd backend`
    *   Create and activate a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate # On Windows use `venv\Scripts\activate`
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   Configure environment variables: You'll need to set variables like `SECRET_KEY`, `GEMINI_API_KEY`, etc., directly in your shell or using a tool like `python-dotenv` (requires adding a `.env` file *inside* the `backend` directory for this method).
    *   Run the Flask development server (from the `backend` directory):
        ```bash
        flask run --host=0.0.0.0 --port=5000
        ```
    *   You would also need to manually build and serve the frontend separately (e.g., `cd ../frontend && npm install && npm run dev`).
    *   Return to the root directory when done: `cd ..`

---

## Environment Variables & Dual Deployment Modes

The system supports two deployment modes, each with different environment variable requirements:

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

- See the root `.env.example` for a complete, annotated template.

### Google Cloud Datastore & Credentials

- **Hosted/SaaS Mode (`BILLING_REQUIRED=true`):**
  Google Cloud Datastore and credentials are required for user/session data. You must provide Google Cloud credentials as described in `DEPLOYMENT.md`.

- **Local/Self-Hosted Mode (`BILLING_REQUIRED=false`):**
  The backend uses a local in-memory database for user/session data. **No Google Cloud SDK, Datastore, or credentials are required** for local development or Docker Compose. You can run the backend and frontend locally without any Google Cloud setup.

### BILLING_REQUIRED

- **Local/Self-Hosted:** Set `BILLING_REQUIRED=false` (default). Stripe and billing variables are ignored; all features are enabled for all users.
- **Hosted/SaaS:** Set `BILLING_REQUIRED=true`. Stripe keys and webhook secret are required; users must have an active subscription to access premium features.

### SECRET_KEY

- Used for cryptographic signing (sessions, tokens, etc.).
- **Must be a strong, random value.**
- Generate with:
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```
- Never share or commit your real SECRET_KEY.

### Example .env for Local Development

```
# --- Backend ---
BILLING_REQUIRED=false
SECRET_KEY=your_local_dev_secret_key # Replace with output from: python -c "import secrets; print(secrets.token_hex(32))"
GEMINI_API_KEY=your_google_api_key
# Optional: Override default agent models
# ACTION_AGENT_MODEL=gemini-pro
# GUIDE_AGENT_MODEL=gemini-pro
# ARCHON_AGENT_MODEL=gemini-pro

# --- Frontend ---
VITE_API_BASE_URL=http://localhost:5000 # URL for browser to reach backend API
VITE_DEPLOYMENT_MODE= # Leave blank for local/self-hosted features
```

### Example .env for Hosted/SaaS Deployment

```
BILLING_REQUIRED=true
SECRET_KEY=your_strong_production_secret_key
GOOGLE_API_KEY=your_google_api_key
STRIPE_API_KEY=your_stripe_api_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
ACTION_AGENT_MODEL=gemini-2.5-pro-exp-03-25
GUIDE_AGENT_MODEL=gemini-2.5-pro-exp-03-25
ARCHON_AGENT_MODEL=gemini-2.5-pro-exp-03-25
```

- For production, use a secure secret manager (e.g., Google Secret Manager) and never commit secrets to version control.
- See `DEPLOYMENT.md` for cloud/production deployment details.

---

### Agent Model Selection

You can configure which LLM model each agent uses by setting the following environment variables:

- `ACTION_AGENT_MODEL`: Model for the Action Agent (default: `gemini-pro`)
- `GUIDE_AGENT_MODEL`: Model for the Guide Agent (default: `gemini-pro`)
- `ARCHON_AGENT_MODEL`: Model for the Archon Agent (default: `gemini-pro`)

Supported values include `"gemini-pro"`, `"gpt-4o"`, and any other supported LLM model.

**Example (.env):**
```
ACTION_AGENT_MODEL=gemini-pro
GUIDE_AGENT_MODEL=gpt-4o
ARCHON_AGENT_MODEL=gemini-pro
```

If a variable is not set, the system default (`gemini-pro`) will be used.  
You may override these in a separate `.env.production` file if needed for production deployments.

---
### Frontend Configuration

- **`VITE_API_BASE_URL`**: The URL the frontend (running in the browser) uses to make API calls to the backend. For the standard Docker development setup, this should be `http://localhost:5000` (pointing to the port mapped from the backend container to your host machine).
- **`VITE_DEPLOYMENT_MODE`**: Controls frontend behavior (e.g., signup flow).
    - Set to `'cloud'` for cloud-hosted features (like free tier signup).
    - Leave blank (default in `.env.example`) for standard self-hosted/local features.
- Both variables are configured in the root `.env` file and automatically picked up by the frontend build process within Docker.

---

### Production Deployment

Detailed guides for deploying to production environments are available in the `docs/` directory:

*   `docs/production_deployment_guide.md`: General guide for self-hosted Linux VPS.
*   `docs/cloudflare-gcp-deployment-guide.md`: Specific guide for deploying using Google Cloud Platform (GCP) Functions and Cloudflare.

## Usage

End-users interact with the system primarily through the web user interface. The process is typically guided, initiated by the user selecting options or providing initial input. The frontend communicates with the backend API to trigger agent actions. User authentication is required for most operations. Stripe integration handles payment processing for monetization features.  
The backend will use the configured LLM model for each agent as specified in your environment variables.

## Development Status

*   **Stage:** Mature (Testing / Early Production)
*   **AI Integration:** Supports Google Gemini and OpenAI models, with per-agent model selection via environment variables.
*   **Environment Configuration:** Flexible, with clear templates for local and production use.
*   **Recent Changes:** Added flexible model selection for each agent; improved Gemini AI integration; updated environment configuration.
*   **Known Issues:** (List known issues here)
*   **Roadmap:** (Outline future plans here)

## Contribution Guidelines

Contributions are welcome. Please refer to `CONTRIBUTING.md` (to be created) for details on how to contribute, coding standards, and the pull request process.

## License

Apache License
