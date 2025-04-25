# Decision Points AI System
![Decision Points AI Logo](https://i.imgur.com/5AVm5uo.jpeg)

## Summary/Overview

Decision Points is an AI-powered system designed to assist with various business automation and analysis tasks. It features a web-based dashboard with functional pages for Automation (Workflow creation/listing), Analytics, Insights, Customers, and Revenue. A key feature is the Orchestrator Panel, allowing direct interaction with a Google Gemini-powered agent via WebSockets. The system is built with a FastAPI backend, React frontend, and utilizes Docker for a streamlined local development setup.

## Key Features

*   **Functional Dashboard Pages:**
    *   **Automation:** Create and list automated workflows.
    *   **Analytics, Insights, Customers, Revenue:** Dedicated pages
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
*   **Communication:** REST APIs, WebSockets

## Architecture Overview

The system uses a Client-Server architecture. A React frontend communicates with a FastAPI backend API via REST calls for standard data retrieval and WebSockets for real-time interaction with the Orchestrator agent. The backend leverages Google Gemini for its AI capabilities. Docker Compose is used to manage the local development environment, running the frontend and backend services in separate containers.

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
    *   `SECRET_KEY`: Generate a unique secret key.  (see `.env.example` for command).
    *   `GEMINI_API_KEY`: Your API key from Google AI Studio.
*   **Run:**
    ```bash
    docker compose up -d
    ```
    *   Use `-d` to run in detached mode (background). Omit it to see logs directly.
    *   If you're not using Docker Compose v2, replace `docker compose` with `docker-compose`.
    *   You can use `docker compose up --build --d` to rebuild the images. This is useful after making major code changes.
*   **Access:**
    *   Frontend: `http://localhost:5173` 
    *   Backend: `http://localhost:8000`
*   **How it Works:**
    *   `docker-compose.yml` defines `frontend` and `backend` services.
*   **Stopping:**
    ```bash
    docker compose down
    ```

## Environment Variables

The environment variables that need to be configured in your `.env` file (copied from `.env.example`) will be labeled as optional or required in the `.env.example` file. (and therefore your `.env` file)


### Autonomous Income Workflow Variables:

*   This section needs analysis and updating

## API Endpoints

The backend provides several API endpoints, including:

*   `/api/workflows`: Manage automation workflows (GET, POST).
*   `/api/analytics`: Fetch data for the Analytics dashboard (GET).
*   `/api/insights`: Fetch data for the Insights dashboard (GET).
*   `/api/customers`: Fetch data for the Customers dashboard (GET).
*   `/api/revenue`: Fetch data for the Revenue dashboard (GET).
*   `/api/orchestrator/tasks`: Endpoint related to orchestrator tasks (details may vary).
*   WebSocket Endpoint (typically `/ws` or similar, handled by FastAPI): For real-time communication with the Orchestrator Panel.

*(Note: This list might not be exhaustive. Refer to backend route definitions for complete details.)*

## Development Status

*   **Stage:** polishing the docker local testing version
*   **Core Features:** Dashboard pages to access and observe the agent system 
*   **Data:** Analytics
*   **Setup:** Docker Compose is the standard local development environment.
*   **Known Issues:** decision-points-agent-web-search-1 container is constantly restarting
*   **Roadmap:** implement reddit market research agent

## Contribution Guidelines

Contributions are welcome. Please establish contribution guidelines (e.g., in a `CONTRIBUTING.md` file) covering coding standards, branch strategy, and the pull request process.

## License

Apache License 2.0
