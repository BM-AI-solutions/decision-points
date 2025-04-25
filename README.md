# Decision Points AI System
![Decision Points AI Logo](https://i.imgur.com/5AVm5uo.jpeg)

## Summary/Overview

Decision Points is an AI-powered system designed to assist with various business automation and analysis tasks. It features a web-based dashboard with functional pages for Automation (Workflow creation/listing), Analytics, Insights, Customers, and Revenue (currently using placeholder data for the latter four). A key feature is the Orchestrator Panel, allowing direct interaction with a Google Gemini-powered agent via WebSockets. The system is built with a fastapi backend, React frontend, and utilizes Docker for a streamlined local development setup.

## Key Features

*   **Functional Dashboard Pages:**
    *   **Automation:** Create and list automated workflows.
*   **Orchestrator Panel:** Interact directly with a Gemini-powered AI agent via a WebSocket connection for real-time task execution and feedback.
*   **Workflow Management:** Backend support for defining and managing automated workflows.
*   **API Endpoints:** Provides backend APIs for dashboard data and orchestrator tasks.
*   **Dockerized Local Setup:** Easy-to-use local development environment using Docker Compose.
*   **Autonomous Income Workflow:** An integrated workflow utilizing specialized agents (Market Research, Improvement, Branding, Deployment) orchestrated by a `WorkflowManagerAgent` to identify, refine, brand, and deploy simple digital products or services.

## Technology Stack

*   **Backend:**
    *   Language: Python 3.0
    *   Framework: FastAPI
    *   AI: Google Generative AI (Gemini)
*   **Frontend:**
    *   Library: React
    *   Build Tool: Vite
*   **Containerization:** Docker, Docker Compose

## Architecture Overview

The system uses a Client-Server architecture. A React frontend communicates with a FastAPI backend. The backend leverages Google Gemini for its AI capabilities. Docker Compose is used to manage the local environment, running the frontend and backend services in separate containers.

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
    *   **Crucially, edit the new `.env` file and fill in *all* required values.**
*   **Run:**
    ```bash
    docker compose up -d
    ```
    *   Use `-d` to run in detached mode (background). Omit it to see logs directly.
    *   The `--build` flag ensures images are rebuilt if Dockerfiles or contexts change. It's good practice to include it, especially after pulling code changes.
*   **Access:**
    *   Frontend: `http://localhost:` (update this)
    *   Backend API: `http://localhost:` (update this)
*   **Stopping:**
    ```bash
    docker compose down
    ```

## Environment Variables

The necessary environment variables need to be configured in your `.env` file (copied from `.env.example`):

### Autonomous Income Workflow Variables: (update these i needed)

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

## Development Status

*   **Stage:** Active Development / Functional Prototype
*   **Core Features:** Dashboard pages (Automation, Analytics, etc.), Orchestrator Panel (Gemini/WebSocket), Workflow backend.
*   **Setup:** Docker Compose is the standard local environment.
*   **Known Issues:** finish refactoring the backend to fastapi, and the agents to ADK and A2A
*   **Roadmap:** implement the reddit search agent and plan from startup idea notes to business improvement workflow. create trading workflow. flesh out freelance workflow

## Contribution Guidelines

Contributions are welcome. Please establish contribution guidelines (e.g., in a `CONTRIBUTING.md` file) covering coding standards, branch strategy, and the pull request process.

## License

Apache License 2.0
