# Consolidation Plan for Unified Local Setup with A2A

This plan outlines the steps required to refactor the project for a unified local development setup using Docker Compose and implement Agent-to-Agent (A2A) communication based on the ADK documentation.

**Goal:** Consolidate the local development environment into a single `docker-compose.yml` file, simplify Dockerfiles, and refactor agent communication to use the A2A protocol.

**Current State:**
*   Separate `docker-compose.dev.yml` and `docker-compose.prod.yml`.
*   Backend uses FastAPI.
*   Agents are located in `backend/agents/`.
*   Agent communication mechanism needs to be replaced with A2A.

**Desired State:**
*   Single `docker-compose.yml` for local development.
*   Simplified, single-stage Dockerfiles for local development.
*   Agents refactored as ADK agents acting as A2A servers.
*   FastAPI backend acting as an A2A client.
*   A2A communication configured within Docker Compose.

**Detailed Plan:**

**Step 1: Simplify Docker Compose (`docker-compose.yml`)**

*   **Action:** Modify the existing `docker-compose.yml` to serve as the single configuration for local development.
*   **Details:**
    *   Remove all `profiles` sections.
    *   Define services for `backend`, `frontend`, `db`, and each individual agent (e.g., `web_search_agent`, `branding_agent`, etc.). Each agent will run as a separate service.
    *   Configure the `backend` service to use `uvicorn --reload` for hot-reloading Python code.
    *   Configure the `frontend` service to use the Vite development server.
    *   Ensure necessary ports are exposed for the `backend` (e.g., 8000) and `frontend` (e.g., 3000).
    *   Define a Docker network (e.g., `a2a_network`) for internal communication between services. All services should join this network.
    *   For each agent service, define a port for its A2A server to listen on within the `a2a_network`. These ports should be unique for each agent.
    *   Mount local code volumes for the `backend`, `frontend`, and each agent service to enable live code updates without rebuilding Docker images.
    *   Configure dependencies between services (e.g., `backend` depends on `db`, agents might depend on `db` or other services if needed).
*   **Mermaid Diagram (Conceptual Docker Compose Structure):**
    ```mermaid
    graph TD
        subgraph Docker Host
            Browser(User Browser) --> Frontend(Frontend Service: 3000)
            Browser --> Backend(Backend Service: 8000)
        end

        subgraph Docker Network (a2a_network)
            Frontend --> Backend
            Backend --> Agent1(Agent Service 1: Port X)
            Backend --> Agent2(Agent Service 2: Port Y)
            Backend --> ...
            Backend --> DB(Database Service)
            Agent1 --> DB
            Agent2 --> DB
            Agent1 <--> Agent2 %% If agents need to communicate directly
        end
    ```

**Step 2: Simplify Dockerfiles**

*   **Action:** Modify `backend/Dockerfile`, `frontend/Dockerfile`, and each agent's Dockerfile (e.g., `backend/agents/web_search.Dockerfile`) to create single-stage builds optimized for local development.
*   **Details:**
    *   Remove multi-stage build targets (e.g., `builder`, `dev`, `prod`).
    *   Use a single base image suitable for the application (e.g., `python:3.9-slim` for backend/agents, a Node.js image for frontend).
    *   Copy application code into the image.
    *   Install dependencies.
    *   Define the entry point command to run the application/agent in development mode (e.g., `uvicorn --reload` for backend, Vite dev server for frontend, ADK server command for agents).
    *   Ensure the agent Dockerfiles install the ADK Python package and any agent-specific dependencies.

**Step 3: Refactor Backend Agents to ADK A2A Servers**

*   **Action:** Convert the existing agent logic in `backend/agents/` into ADK agents that function as A2A servers.
*   **Details:**
    *   For each agent file (e.g., `backend/agents/web_search_agent.py`), refactor the core logic to fit the ADK `Agent` or `LlmAgent` structure.
    *   Implement the agent's task handling logic within the ADK framework, potentially using the `_run_async_impl` method for custom agents or defining tools for LLM agents.
    *   Integrate necessary tools (e.g., web search, database interaction) into the ADK agent definition.
    *   Set up each agent to run an A2A server, listening on the unique port defined in `docker-compose.yml`. This will likely involve using ADK's server capabilities or a simple FastAPI/Uvicorn server that hosts the ADK agent and exposes the A2A protocol.
    *   Ensure agents can access necessary resources (e.g., database) within the Docker network.

**Step 4: Update Backend API to be an A2A Client**

*   **Action:** Modify the FastAPI backend (`backend/app/`) to communicate with the refactored agents using the A2A protocol.
*   **Details:**
    *   Identify the API endpoints in `backend/app/api/v1/endpoints/` that interact with agents.
    *   Replace the existing agent communication logic with calls to A2A clients.
    *   Use an A2A client library (likely in Python, compatible with ADK) to send tasks to the agent services running in Docker. The client will need to address the agents using their service names and A2A ports defined in `docker-compose.yml` (e.g., `http://web_search_agent:port_x`).
    *   Handle synchronous and/or streaming responses from the agents as required by the application's functionality.
    *   Update any data models or interfaces in `backend/app/schemas/` or `backend/app/services/` to align with the A2A protocol's message and artifact structures.

**Step 5: Update Frontend (if necessary)**

*   **Action:** Review and update the frontend code (`frontend/`) if the changes in the backend API (Step 4) necessitate modifications to how the frontend interacts with the backend or displays information.
*   **Details:**
    *   Check `frontend/src/services/api.js` and other relevant files for changes in API endpoint paths, request/response formats, or data structures.
    *   Adjust frontend components (`frontend/src/components/`) to handle any changes in the data received from the backend, particularly regarding agent responses or status updates.
    *   If the interaction model shifts significantly (e.g., from polling to streaming), update the frontend to handle streaming responses from the backend.

**Step 6: Cleanup**

*   **Action:** Remove obsolete files.
*   **Details:**
    *   Delete `docker-compose.dev.yml`.
    *   Delete `docker-compose.prod.yml`.

**Implementation Notes:**

*   The specific implementation of the A2A server within each agent service (Step 3) will depend on the chosen ADK server implementation method (e.g., using ADK's built-in server capabilities if available, or wrapping the ADK agent in a minimal FastAPI application).
*   The A2A client implementation in the backend (Step 4) will require using an A2A client library compatible with the ADK A2A server implementation.
*   Careful consideration should be given to error handling and timeouts for A2A communication between services.
*   Environment variables for API keys and other configurations should be managed consistently across services, likely using a shared `.env` file and Docker Compose's environment variable loading.