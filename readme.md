# Decision Points AI System
![Decision Points AI Logo](https://i.imgur.com/5AVm5uo.jpeg)

## Summary/Overview

Decision Points is an AI-powered system designed to assist with various business automation and analysis tasks. It features a web-based dashboard with functional pages for Automation (Workflow creation/listing), Analytics, Insights, Customers, and Revenue (currently using placeholder data for the latter four). A key feature is the Orchestrator Panel, allowing direct interaction with a Google Gemini-powered agent via WebSockets. The system is built with a Flask backend, React frontend, and utilizes Docker for a streamlined local development and deployment setup.

## Key Features

*   **Functional Dashboard Pages:**
    *   **Automation:** Create and list automated workflows.
    *   **Analytics, Insights, Customers, Revenue:** Dedicated pages (currently displaying placeholder data fetched from backend APIs).
*   **Orchestrator Panel:** Interact directly with a Gemini-powered AI agent via a WebSocket connection for real-time task execution and feedback.
*   **Workflow Management:** Backend support for defining and managing automated workflows.
*   **API Endpoints:** Provides backend APIs for dashboard data and orchestrator tasks.
*   **Dockerized Setup:** Easy-to-use local development and deployment environment using Docker and Docker Compose.
*   **Autonomous Income Workflow:** An integrated workflow utilizing specialized agents (Market Research, Improvement, Branding, Deployment) orchestrated by a `WorkflowManagerAgent` to identify, refine, brand, and deploy simple digital products or services.

## Technology Stack

*   **Backend:**
    *   Language: Python 3.11+
    *   Framework: Flask, Flask-SocketIO (for WebSocket communication)
    *   AI: Google Generative AI (Gemini)
    *   Server: Gunicorn (in Docker)
*   **Frontend:**
    *   Library: React
    *   Build Tool: Vite
    *   Server: Nginx (in Docker)
*   **Containerization:** Docker, Docker Compose
*   **Communication:** REST APIs, WebSockets

## Architecture Overview

The system uses a Client-Server architecture. A React frontend (built with Vite, served by Nginx) communicates with a Flask backend API (served by Gunicorn) via REST calls for standard data retrieval and WebSockets for real-time interaction with the Orchestrator agent. The backend leverages Google Gemini for its AI capabilities. Docker Compose manages the services, running the frontend and backend in separate containers defined by `docker-compose.yml` and a root `Dockerfile` for the backend.

## Autonomous Income Generation Workflow

This system includes an autonomous workflow designed to generate income by identifying a market need, creating/improving a simple digital product or service, branding it, and deploying it. This workflow is orchestrated by the `WorkflowManagerAgent` and involves the following specialized agents running within the backend service:

1.  **Market Research Agent:** Scans the web, analyzes trends, and identifies potential niches or product ideas with low competition and high demand.
2.  **Improvement Agent:** Takes the initial idea or existing simple product and refines it, potentially adding features, improving code quality, or enhancing its value proposition based on research.
3.  **Branding Agent:** Develops a simple brand identity, including name suggestions, logos (potentially placeholder/simple generation), and marketing copy for the product.
4.  **Deployment Agent:** Takes the finalized product and branding assets and deploys them to a suitable platform (e.g., Vercel, Netlify, Cloudflare Pages, simple web hosting).

The `WorkflowManagerAgent` coordinates the execution of these agents, passing context and results between steps. The user can trigger this workflow via specific prompts to the Orchestrator Panel (e.g., "start income workflow").

**Note on Analytics:** The `CodeGenerationAgent` (used implicitly by the workflow) now includes a basic Google Analytics (GA4) setup in the generated application's `index.html`. However, it uses a placeholder Measurement ID (`G-XXXXXXXXXX`). For analytics tracking to function, you **must** replace this placeholder with your actual GA4 Measurement ID in the deployed application's code.

**Note on AdSense:** Similarly, the `CodeGenerationAgent` includes placeholder Google AdSense setup (script in `index.html` and example ad units in components). These use placeholder IDs (`ca-pub-XXXXXXXXXXXXXXXX`, `YYYYYYYYYY`). For monetization to work, you **must** replace these placeholders with your actual Google AdSense Publisher ID and Ad Unit Slot IDs. You will also need an active and approved Google AdSense account.

## Local Setup (Docker - Recommended Method)

This is the primary and recommended method for local development and testing using Docker.

*   **Prerequisites:**
    *   Ensure Docker Desktop (or Docker Engine + Docker Compose) is installed and running.
    *   Ensure your frontend application is built. If not, run `npm install && npm run build` (or equivalent) inside the `frontend/` directory to generate the `frontend/dist` folder.
*   **Environment Setup:**
    *   Copy the root `.env.example` file to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   **Crucially, edit the new `.env` file and fill in *all* required values.** This includes:
        *   `SECRET_KEY`: Generate a unique secret key (see `.env.example` for command).
        *   `GEMINI_API_KEY`: Your API key from Google AI Studio.
        *   `VITE_API_BASE_URL`: Set this to `http://localhost:5001` (the backend port exposed by Docker Compose).
        *   *(Review the "Environment Variables" section below for other important variables).*
*   **Run:**
    *   Open your terminal in the project root directory (`decision-points/`).
    *   Build and start the services using Docker Compose:
        ```bash
        docker compose up --build -d
        ```
    *   Use `-d` to run in detached mode (background). Omit it to see logs directly.
    *   The `--build` flag ensures images are rebuilt based on the `Dockerfile` and context.
*   **Access:**
    *   Frontend: `http://localhost:8080` (served by Nginx)
    *   Backend API: `http://localhost:5001` (Flask/Gunicorn)
*   **How it Works:**
    *   `docker-compose.yml` defines `frontend` (Nginx) and `backend` (Python/Gunicorn) services.
    *   The `backend` service is built using the root `Dockerfile`.
    *   The `frontend` service uses a standard Nginx image and serves the static build artifacts from `frontend/dist`.
    *   Services are connected on a Docker network. The frontend JavaScript code running in your **browser** accesses the API via the host machine's mapped backend port: `http://localhost:5001` (as configured by `VITE_API_BASE_URL` in your `.env` file).
    *   The root `.env` file provides environment variables to the backend service.
*   **Stopping:**
    ```bash
    docker compose down
    ```

## Environment Variables

The following environment variables need to be configured in your `.env` file (copied from `.env.example`):

*   `SECRET_KEY`: **(Required)** A strong, unique secret used by Flask for session security. Generate one using `python -c "import secrets; print(secrets.token_hex(32))"`.
*   `GEMINI_API_KEY`: **(Required)** Your API key for Google Generative AI (Gemini), obtained from Google AI Studio. This is essential for the Orchestrator Panel and other AI features.
*   `ORCHESTRATOR_LLM_MODEL`: **(Required)** The Gemini model name for the primary Orchestrator agent (e.g., `gemini-1.5-pro-latest`). Defaults to `gemini-1.5-pro-latest` if not set.
*   `SPECIALIZED_AGENT_LLM_MODEL`: **(Required)** The default Gemini model name for specialized agents (e.g., Market Research, Branding). Defaults to `gemini-1.5-flash-latest` if not set.
*   `VITE_API_BASE_URL`: **(Required for Frontend)** The URL the frontend uses to reach the backend API. For the default Docker setup, this **must** be `http://localhost:5001`.

*   **(Optional)** `GCP_PROJECT_ID`: Google Cloud Project ID, potentially used by agents like `FreelanceTaskAgent`.
*   **(Optional)** `BRAVE_API_KEY`: API key for Brave Search, used by `WebSearchAgent`.

### Optional Agent-Specific LLM Models:

You can optionally override the `SPECIALIZED_AGENT_LLM_MODEL` for individual agents by setting specific environment variables. If an agent-specific variable is not set, the agent will use the model defined by `SPECIALIZED_AGENT_LLM_MODEL`. Examples include:

*   `MARKET_RESEARCH_LLM_MODEL`
*   `IMPROVEMENT_LLM_MODEL`
*   `BRANDING_LLM_MODEL`
*   *(Add others as needed based on implemented agents)*

### Autonomous Income Workflow Variables:

*   **(Optional)** `OPENAI_API_KEY`: Potentially used by `MarketResearchAgent`.
*   `FIRECRAWL_API_KEY`: **(Required)** Used by `MarketResearchAgent` for web scraping. Get from [Firecrawl](https://www.firecrawl.dev/).
*   **(Optional)** `COMPETITOR_SEARCH_PROVIDER`: Search engine for competitor analysis (e.g., 'google').
*   **(Conditional)** `EXA_API_KEY`: Required if using Exa Search in `MarketResearchAgent`. Get from [Exa AI](https://exa.ai/).
*   **(Conditional)** `PERPLEXITY_API_KEY`: Required if using Perplexity AI in `MarketResearchAgent`. Get from [Perplexity AI](https://docs.perplexity.ai/docs/getting-started).
*   **(Conditional)** Deployment Provider Keys (e.g., `VERCEL_API_TOKEN`, `CLOUDFLARE_API_TOKEN`, etc.): Required by the `DeploymentAgent` based on the chosen deployment platform(s). Add the specific keys needed for your setup.

**Note on Agent URLs:** Variables like `MARKET_RESEARCH_AGENT_URL`, `IMPROVEMENT_AGENT_URL`, etc., are **not** typically required when running the entire application via the provided `docker-compose.yml`, as all agents run within the single backend container. These variables are primarily relevant if you deploy agents as separate microservices.

## API Endpoints

The backend provides several API endpoints, including:

*   `/api/workflows`: Manage automation workflows (GET, POST).
*   `/api/analytics`: Fetch data for the Analytics dashboard (GET).
*   `/api/insights`: Fetch data for the Insights dashboard (GET).
*   `/api/customers`: Fetch data for the Customers dashboard (GET).
*   `/api/revenue`: Fetch data for the Revenue dashboard (GET).
*   `/api/orchestrator/tasks`: Endpoint related to orchestrator tasks (details may vary).
*   WebSocket Endpoint (typically `/socket.io/`, handled by Flask-SocketIO): For real-time communication with the Orchestrator Panel.

*(Note: This list might not be exhaustive. Refer to backend route definitions for complete details.)*

## Development Status

*   **Stage:** Active Development / Functional Prototype
*   **Core Features:** Dashboard pages (Automation, Analytics, etc.), Orchestrator Panel (Gemini/WebSocket), Workflow backend.
*   **Data:** Analytics, Insights, Customers, Revenue pages currently use placeholder data from their respective API endpoints.
*   **Setup:** Docker Compose is the standard local development environment.
*   **Known Issues:** Frontend needs to be manually built (`npm run build`) before running `docker compose up`.
*   **Roadmap:** Implement real data fetching for dashboard pages, Integrate frontend build into Docker process, Expand workflow capabilities.

## Contribution Guidelines

Contributions are welcome. Please establish contribution guidelines (e.g., in a `CONTRIBUTING.md` file) covering coding standards, branch strategy, and the pull request process.

## License

Apache License 2.0 (Verify LICENSE file)
