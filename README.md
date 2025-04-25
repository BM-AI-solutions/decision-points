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
    *   AI: Google Generative AI (Gemini) - Direct integration without Vertex AI
    *   Database: PostgreSQL (for state persistence)
    *   ORM: SQLAlchemy with Alembic for migrations
    *   Agent Communication: A2A Protocol
*   **Frontend:**
    *   Library: React
    *   Build Tool: Vite
*   **Containerization:** Docker, Docker Compose
*   **Communication:** REST APIs, WebSockets, A2A Protocol

## Architecture Overview

The system uses a Client-Server architecture. A React frontend communicates with a FastAPI backend API via REST calls for standard data retrieval and WebSockets for real-time interaction with the Orchestrator agent. The backend leverages Google Gemini for its AI capabilities and PostgreSQL for state persistence.

The system implements a multi-agent workflow using the Agent-to-Agent (A2A) protocol, allowing specialized agents to communicate and collaborate. Each agent maintains its state in the PostgreSQL database, which provides reliable persistence and transaction support.

Docker Compose is used to manage the local development environment, running the frontend, backend, and database services in separate containers. Database migrations are automatically applied during container startup.

## Multi-Agent Architecture

The system implements a multi-agent architecture using the Agent-to-Agent (A2A) protocol and Google Gemini. Each agent is a specialized service that can be run independently and communicates with other agents through a standardized protocol.

### Agent State Persistence

All agents use PostgreSQL for state persistence, which provides several advantages:

1. **Reliability**: PostgreSQL offers ACID-compliant transactions, ensuring data integrity.
2. **Scalability**: The database can handle multiple concurrent connections from different agents.
3. **Durability**: State is persisted even if agents crash or restart.
4. **Queryability**: SQL queries can be used to analyze agent state and workflow progress.

The database schema includes tables for:
- `workflows`: Stores workflow metadata and status
- `workflow_steps`: Tracks individual steps within a workflow
- `agent_states`: Stores agent-specific state data
- `agent_tasks`: Tracks tasks assigned to agents

### Autonomous Income Generation Workflow

This system includes an autonomous workflow designed to generate income by identifying a market need, creating/improving a simple digital product or service, branding it, and deploying it. This workflow is orchestrated by the `WorkflowManagerAgent` and involves the following specialized agents:

1.  **Market Research Agent:** Scans the web, analyzes trends, and identifies potential niches or product ideas with low competition and high demand.
2.  **Improvement Agent:** Takes the initial idea or existing simple product and refines it, potentially adding features, improving code quality, or enhancing its value proposition based on research.
3.  **Branding Agent:** Develops a simple brand identity, including name suggestions, logos (potentially placeholder/simple generation), and marketing copy for the product.
4.  **Deployment Agent:** Takes the finalized product and branding assets and deploys them to a suitable platform (e.g., Vercel, Netlify, Cloudflare Pages, simple web hosting).
5.  **Marketing Agent:** Promotes the product/service through various channels.
6.  **Lead Generation Agent:** Identifies potential customers and generates leads.
7.  **Freelance Task Agent:** Monitors freelance platforms for relevant tasks.

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
    *   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Database credentials.
*   **Run:**
    ```bash
    docker compose up -d
    ```
    *   Use `-d` to run in detached mode (background). Omit it to see logs directly.
    *   If you're not using Docker Compose v2, replace `docker compose` with `docker-compose`.
    *   You can use `docker compose up --build --d` to rebuild the images. This is useful after making major code changes.
    *   Database migrations are automatically applied during container startup.
*   **Access:**
    *   Frontend: `http://localhost:5173`
    *   Backend: `http://localhost:8000`
    *   Database: `localhost:5432` (accessible with the credentials from your `.env` file)
*   **How it Works:**
    *   `docker-compose.yml` defines `frontend`, `backend`, and `db` services.
    *   The `db` service runs PostgreSQL and stores all agent state and workflow data.
    *   The `backend` service depends on the `db` service and waits for it to be healthy before starting.
*   **Stopping:**
    ```bash
    docker compose down
    ```
*   **Database Management:**
    *   Database migrations are managed with Alembic.
    *   To create a new migration:
        ```bash
        docker compose exec backend alembic revision --autogenerate -m "Description of changes"
        ```
    *   To apply migrations manually:
        ```bash
        docker compose exec backend alembic upgrade head
        ```

*   **Starting Agents:**
    *   To start all agents:
        ```bash
        docker compose exec backend python scripts/start_all_agents.py
        ```
    *   To start a specific agent:
        ```bash
        docker compose exec backend python scripts/start_agent.py --agent <agent_name> --port <port>
        ```
        Where `<agent_name>` is one of: `market_research`, `improvement`, `branding`, `code_generation`, `deployment`, `marketing`, `lead_generation`, `freelance_tasker`, `workflow_manager`, `content_generation`
    *   Example:
        ```bash
        docker compose exec backend python scripts/start_agent.py --agent market_research --port 8004
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
