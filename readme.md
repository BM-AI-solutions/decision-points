# Decision Points AI System

## Summary/Overview

Decision Points is an AI-powered system designed to automate the creation, deployment, and monetization of online businesses. Utilizing specialized agents (Guide, Action, etc.), it analyzes markets, implements business models and features, generates branding materials, and projects cash flow, requiring minimal human input. The system targets both developers for setup and maintenance, and end-users who interact via a web UI to create their businesses.

## Key Features

*   **Market Analysis:** In-depth analysis of potential business markets.
*   **Business & Feature Implementation:** Automated setup of core business logic and features.
*   **Branding Generation:** Creates branding elements for the new business.
*   **Automated Deployment:** Supports deployment to multiple targets (Docker, Cloud Platforms, VPS).
*   **Cash Flow Projection:** Estimates potential financial performance.
*   **User Authentication:** Secure user management.
*   **Stripe-Based Monetization:** Integration with Stripe for payment processing.
*   **Chat Interaction:** User interaction facilitated through a chat interface.

## Technology Stack

*   **Backend:**
    *   Language: Python (3.8+/3.9)
    *   Framework: Flask
    *   Server: Gunicorn / uWSGI
    *   AI: Google Gemini API, Langchain
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

The system employs a Client-Server architecture, featuring a static frontend communicating with a Flask-based backend API. An optional Cloudflare Worker layer can act as an API proxy. The backend utilizes a multi-agent design to handle different aspects of business creation. The architecture supports multiple deployment targets, including Docker Compose for local/simple deployments, Google Cloud Functions combined with Cloudflare, or a self-hosted Linux VPS.

## Installation

### Local Setup

Two primary methods are supported for local development and testing:

1.  **Docker Compose (Recommended):**
    *   Ensure Docker and Docker Compose are installed.
    *   Configure required environment variables (copy `.env.example` to `.env` and fill in values, including your `GOOGLE_API_KEY` for Gemini).
    *   Run: `docker-compose up --build`

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
    *   Configure required environment variables (e.g., set them in your shell or create a `.env` file, ensuring you set `GOOGLE_API_KEY` for Gemini).
    *   Run the Flask development server (refer to Flask documentation or project specifics).

**Environment Variables:** The system relies on environment variables for configuration, including API keys and secrets. For Gemini, set the `GOOGLE_API_KEY` environment variable. Refer to `backend/.env.example` for a template.

### Production Deployment

Detailed guides for deploying to production environments are available in the `docs/` directory:

*   `docs/production_deployment_guide.md`: General guide for self-hosted Linux VPS.
*   `docs/cloudflare-gcp-deployment-guide.md`: Specific guide for deploying using Google Cloud Platform (GCP) Functions and Cloudflare.

## Usage

End-users interact with the system primarily through the web user interface. The process is typically guided, initiated by the user selecting options or providing initial input. The frontend communicates with the backend API to trigger agent actions. User authentication is required for most operations. Stripe integration handles payment processing for monetization features.

## Development Status

*   **Stage:** Mature (Testing / Early Production)
*   **Version:** (Specific version information TBD)
*   **Recent Changes:** (Details TBD)
*   **Known Issues:** (Placeholder - list known issues here)
*   **Roadmap:** (Placeholder - outline future plans here)

## Contribution Guidelines

Contributions are welcome. Please refer to `CONTRIBUTING.md` (to be created) for details on how to contribute, coding standards, and the pull request process.

## License

License information TBD. Please see the `LICENSE` file (to be created).
