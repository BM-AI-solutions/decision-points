# Decision Points AI System

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

1.  **Docker Desktop (Recommended):**
    *   Ensure Docker Desktop is installed.
    *   Configure required environment variables (copy `.env.example` to `.env` and fill in values, including your `GOOGLE_API_KEY` for Gemini and any agent model overrides).
    *   Run: `docker compose up --build`
    *   The backend and frontend are fully Dockerized for local development and production builds.
    *   The backend uses a multi-stage Dockerfile supporting both development (hot-reload, volume mount) and production (Gunicorn) modes. Compose uses the dev stage by default for local development.
    *   The frontend uses a Dockerfile to build static assets with npm, then serves them via nginx in production. For local development, the dist/ directory is mounted for live updates.
    *   Both services are orchestrated via `docker-compose.yml`, which sets up a shared network so the frontend can reach the backend at `http://backend:5000`.
    *   Environment variables for the backend are managed via `.env` files (see `backend/.env.example`). Compose loads these automatically for the backend service.
    *   To forward Stripe webhooks to your backend during local development, use the Stripe CLI:
        ```bash
        stripe listen --forward-to localhost:5000/api/stripe/webhook
        ```
        (Requires [Stripe CLI](https://stripe.com/docs/stripe-cli))


2.  **Python Virtual Environment (venv):**
    *   Ensure Python 3.8+ or 3.9+ is installed.
    *   Create and activate a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate # On Windows use `venv\Scripts\activate`
        ```
    *   Install dependencies:
        ```bash
        pip install -r backend/requirements.txt
        ```
    *   Configure required environment variables (e.g., set them in your shell or create a `.env` file, ensuring you set `GOOGLE_API_KEY` for Gemini and any agent model overrides).
    *   Run the Flask development server (refer to Flask documentation or project specifics).

**Environment Variables:**  
### Dual-Mode Billing/Subscription Enforcement

By default, local Docker and development environments **do not require a Stripe subscription**. This is controlled by the `BILLING_REQUIRED` environment variable in `backend/.env.example`:

```
BILLING_REQUIRED=false
```

- When `BILLING_REQUIRED` is set to `false` (the default for local/Docker), all subscription checks are bypassed and users have full access to all features.
- For **hosted/cloud deployments**, set `BILLING_REQUIRED=true` in your production environment to enforce Stripe subscription checks and restrict access for non-subscribed users.

This dual-mode logic allows you to develop and test locally without payment requirements, while ensuring proper billing enforcement in production. See `DEPLOYMENT.md` for more details on configuring this for your deployment target.

The system relies on environment variables for configuration, including API keys, secrets, and agent model selection. For Gemini, set the `GOOGLE_API_KEY` environment variable. Refer to `backend/.env.example` for a template.

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
You may override these in `.env.production` for production deployments (see `backend/.env.production.template` for examples).

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

License information TBD. Please see the `LICENSE` file (to be created).
