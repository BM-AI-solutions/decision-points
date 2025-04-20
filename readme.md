# Decision Points AI System
![Decision Points AI Logo](https://i.imgur.com/5AVm5uo.jpeg)

## Summary/Overview

Decision Points is an AI-powered system designed to assist with various business automation and analysis tasks. It features a web-based dashboard with functional pages for Automation (Workflow creation/listing), Analytics, Insights, Customers, and Revenue (currently using placeholder data for the latter four). A key feature is the Orchestrator Panel, allowing direct interaction with a Google Gemini-powered agent via WebSockets. The system is built with a Flask backend, React frontend, and utilizes Docker for a streamlined local development setup.

## Key Features

*   **Functional Dashboard Pages:**
    *   **Automation:** Create and list automated workflows.
    *   **Analytics, Insights, Customers, Revenue:** Dedicated pages (currently displaying placeholder data fetched from backend APIs).
*   **Orchestrator Panel:** Interact directly with a Gemini-powered AI agent via a WebSocket connection for real-time task execution and feedback.
*   **Workflow Management:** Backend support for defining and managing automated workflows.
*   **API Endpoints:** Provides backend APIs for dashboard data and orchestrator tasks.
*   **Dockerized Local Setup:** Easy-to-use local development environment using Docker Compose.
*   **Autonomous Income Workflow:** An integrated workflow utilizing specialized agents (Market Research, Improvement, Branding, Deployment) orchestrated by a `WorkflowManagerAgent` to identify, refine, brand, and deploy simple digital products or services.

## Technology Stack

*   **Backend:**
    *   Language: Python 3.0
    *   Framework: Flask, Flask-SocketIO (for WebSocket communication)
    *   AI: Google Generative AI (Gemini)
*   **Frontend:**
    *   Library: React
    *   Build Tool: Vite
    *   Styling: CSS (potentially Tailwind CSS if used)
*   **Containerization:** Docker, Docker Compose
*   **Communication:** REST APIs, WebSockets

## Architecture Overview

The system uses a Client-Server architecture. A React frontend communicates with a Flask backend API via REST calls for standard data retrieval and WebSockets for real-time interaction with the Orchestrator agent. The backend leverages Google Gemini for its AI capabilities. Docker Compose is used to manage the local development environment, running the frontend and backend services in separate containers.

## Autonomous Income Generation Workflow

This system includes an autonomous workflow designed to generate income by identifying a market need, creating/improving a simple digital product or service, branding it, and deploying it. This workflow is orchestrated by the `WorkflowManagerAgent` and involves the following specialized agents:

1.  **Market Research Agent:** Scans the web, analyzes trends, and identifies potential niches or product ideas with low competition and high demand.
2.  **Improvement Agent:** Takes the initial idea or existing simple product and refines it, potentially adding features, improving code quality, or enhancing its value proposition based on research.
3.  **Branding Agent:** Develops a simple brand identity, including name suggestions, logos (potentially placeholder/simple generation), and marketing copy for the product.
4.  **Deployment Agent:** Takes the finalized product and branding assets and deploys them to a suitable platform (e.g., Vercel, Netlify, Cloudflare Pages, simple web hosting).

The `WorkflowManagerAgent` coordinates the execution of these agents, passing context and results between steps. The user can trigger this workflow via specific prompts to the Orchestrator Panel (e.g., "start income workflow").

**Note on Analytics:** The `CodeGenerationAgent` (used implicitly by the workflow) now includes a basic Google Analytics (GA4) setup in the generated application's `index.html`. However, it uses a placeholder Measurement ID (`G-XXXXXXXXXX`). For analytics tracking to function, you **must** replace this placeholder with your actual GA4 Measurement ID in the deployed application's code.

**Note on AdSense:** Similarly, the `CodeGenerationAgent` includes placeholder Google AdSense setup (script in `index.html` and example ad units in components). These use placeholder IDs (`ca-pub-XXXXXXXXXXXXXXXX`, `YYYYYYYYYY`). For monetization to work, you **must** replace these placeholders with your actual Google AdSense Publisher ID and Ad Unit Slot IDs. You will also need an active and approved Google AdSense account.

## Local Setup (Docker - Recommended Method)

This is the primary and recommended method for local development and testing.

*   **Prerequisites:** Ensure Docker Desktop (or Docker Engine + Docker Compose) is installed and running.
*   **Environment Setup:**
    *   Copy the root `.env.example` file to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   **Crucially, edit the new `.env` file and fill in *all* required values.** This includes:
    *   `SECRET_KEY`: Generate a unique secret key (see `.env.example` for command).
    *   `GEMINI_API_KEY`: Your API key from Google AI Studio.
*   **Run:**
    ```bash
    docker compose -f docker-compose.dev.yml up --build -d
    ```
    *   Use `-d` to run in detached mode (background). Omit it to see logs directly.
    *   The `--build` flag ensures images are rebuilt if Dockerfiles or contexts change. It's good practice to include it, especially after pulling code changes.
*   **Access:**
    *   Frontend: `http://localhost:8000` (served by Vite dev server with hot-reloading)
    *   Backend API: `http://localhost:5000` (Flask dev server with hot-reloading)
*   **How it Works:**
    *   `docker-compose.dev.yml` defines `frontend` and `backend` services.
    *   It uses multi-stage Dockerfiles optimized for development (volume mounts for code, dev servers).
    *   Services are connected on a Docker network. The frontend JavaScript code running in your **browser** accesses the API via the host machine's mapped port: `http://localhost:5000` (as configured by `VITE_API_BASE_URL` in your `.env` file).
    *   The root `.env` file provides environment variables to the services.
*   **Stopping:**
    ```bash
    docker compose -f docker-compose.dev.yml down
    ```

## Environment Variables

The following environment variables need to be configured in your `.env` file (copied from `.env.example`):

*   `SECRET_KEY`: **(Required)** A strong, unique secret used by Flask for session security. Generate one using `python -c "import secrets; print(secrets.token_hex(32))"`.
*   `GEMINI_API_KEY`: **(Required)** Your API key for Google Generative AI (Gemini), obtained from Google AI Studio. This is essential for the Orchestrator Panel and other AI features.
*   `ORCHESTRATOR_LLM_MODEL`: **(Required)** The Gemini model name for the primary Orchestrator agent (e.g., `gemini-1.5-pro-latest`). This agent handles user interaction and often benefits from a more powerful model. Defaults to `gemini-1.5-pro-latest` if not set.
*   `SPECIALIZED_AGENT_LLM_MODEL`: **(Required)** The default Gemini model name for specialized agents (e.g., Market Research, Branding, Code Generation). These agents perform focused tasks and can often use a faster/cheaper model like `gemini-1.5-flash-latest`. Defaults to `gemini-1.5-flash-latest` if not set.
*   `VITE_API_BASE_URL`: **(Required)** The URL the frontend uses to reach the backend API. For the default Docker setup, this **must** be `http://localhost:5000`.

*   **(Optional)** `GCP_PROJECT_ID`: Google Cloud Project ID, potentially used by agents like `FreelanceTaskAgent`.
*   **(Optional)** `BRAVE_API_KEY`: API key for Brave Search, used by `WebSearchAgent`.

### Optional Agent-Specific LLM Models:

You can optionally override the `SPECIALIZED_AGENT_LLM_MODEL` for individual agents by setting specific environment variables. If an agent-specific variable is not set, the agent will use the model defined by `SPECIALIZED_AGENT_LLM_MODEL`. Examples include:

*   `MARKET_RESEARCH_LLM_MODEL`: Model for the Market Research Agent.
*   `IMPROVEMENT_LLM_MODEL`: Model for the Improvement Agent.
*   `BRANDING_LLM_MODEL`: Model for the Branding Agent.
*   `DEPLOYMENT_LLM_MODEL`: Model for the Deployment Agent.
*   `CODE_GENERATION_LLM_MODEL`: Model for the Code Generation Agent.
*   `CONTENT_GENERATION_LLM_MODEL`: Model for the Content Generation Agent.
*   `FREELANCE_TASK_LLM_MODEL`: Model for the Freelance Task Agent.
*   `LEAD_GENERATION_LLM_MODEL`: Model for the Lead Generation Agent.
*   `MARKET_ANALYSIS_LLM_MODEL`: Model for the Market Analysis Agent.
*   `MARKETING_LLM_MODEL`: Model for the Marketing Agent.
*   `WEB_SEARCH_LLM_MODEL`: Model for the Web Search Agent.
*   `WORKFLOW_MANAGER_LLM_MODEL`: Model for the Workflow Manager Agent.
*   *(Add others as needed based on implemented agents)*

### Autonomous Income Workflow Variables:

*   **(Optional)** `OPENAI_API_KEY`: Potentially used by `MarketResearchAgent`.
*   `FIRECRAWL_API_KEY`: **(Required)** Used by `MarketResearchAgent` for web scraping. Get from [Firecrawl](https://www.firecrawl.dev/).
*   **(Optional)** `COMPETITOR_SEARCH_PROVIDER`: Search engine for competitor analysis (e.g., 'google').
*   **(Conditional)** `EXA_API_KEY`: Required if using Exa Search in `MarketResearchAgent`. Get from [Exa AI](https://exa.ai/).
*   **(Conditional)** `PERPLEXITY_API_KEY`: Required if using Perplexity AI in `MarketResearchAgent`. Get from [Perplexity AI](https://docs.perplexity.ai/docs/getting-started).
*   `MARKET_RESEARCH_AGENT_URL`: **(Required)** Endpoint for the `WorkflowManagerAgent` to reach the `MarketResearchAgent`. (Example: `http://localhost:5001`)
*   `IMPROVEMENT_AGENT_URL`: **(Required)** Endpoint for the `WorkflowManagerAgent` to reach the `ImprovementAgent`. (Example: `http://localhost:5002`)
*   `BRANDING_AGENT_URL`: **(Required)** Endpoint for the `WorkflowManagerAgent` to reach the `BrandingAgent`. (Example: `http://localhost:5003`)
*   `DEPLOYMENT_AGENT_URL`: **(Required)** Endpoint for the `WorkflowManagerAgent` to reach the `DeploymentAgent`. (Example: `http://localhost:5004`)
*   **(Optional)** `AGENT_TIMEOUT_SECONDS`: Max wait time for sub-agent responses (Default: 300).
*   **(Conditional)** Deployment Provider Keys (e.g., `VERCEL_API_TOKEN`, `CLOUDFLARE_API_TOKEN`, etc.): Required by the `DeploymentAgent` based on the chosen deployment platform(s). Add the specific keys needed for your setup.

## API Endpoints

The backend provides several API endpoints, including:

*   `/api/workflows`: Manage automation workflows (GET, POST).
*   `/api/analytics`: Fetch data for the Analytics dashboard (GET).
*   `/api/insights`: Fetch data for the Insights dashboard (GET).
*   `/api/customers`: Fetch data for the Customers dashboard (GET).
*   `/api/revenue`: Fetch data for the Revenue dashboard (GET).
*   `/api/orchestrator/tasks`: Endpoint related to orchestrator tasks (details may vary).
*   WebSocket Endpoint (typically `/ws` or similar, handled by Flask-SocketIO): For real-time communication with the Orchestrator Panel.

*(Note: This list might not be exhaustive. Refer to backend route definitions for complete details.)*

## Development Status

*   **Stage:** Active Development / Functional Prototype
*   **Core Features:** Dashboard pages (Automation, Analytics, etc.), Orchestrator Panel (Gemini/WebSocket), Workflow backend.
*   **Data:** Analytics, Insights, Customers, Revenue pages currently use placeholder data from their respective API endpoints.
*   **Setup:** Docker Compose is the standard local development environment.
*   **Known Issues:** (List any known issues here, e.g., "Placeholder data needs replacing with real logic.")
*   **Roadmap:** (Outline future plans, e.g., "Implement real data fetching for dashboard pages", "Expand workflow capabilities.")

## Contribution Guidelines

Contributions are welcome. Please establish contribution guidelines (e.g., in a `CONTRIBUTING.md` file) covering coding standards, branch strategy, and the pull request process.

## License

Apache License 2.0 (Assuming, based on previous context - verify LICENSE file)
