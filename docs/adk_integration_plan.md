# ADK and A2A Integration Architectural Plan

This document outlines the architectural plan for integrating Google's Agent Development Kit (ADK) and the Agent2Agent (A2A) protocol into the decision-points project.

## 1. High-Level Architecture

Introduce a distinct layer for AI agents, managed by the ADK framework and communicating via the A2A protocol. The existing Flask backend will serve as the interface between the frontend and the agent system, specifically the `OrchestratorAgent`.

```mermaid
graph TD
    subgraph Browser
        Frontend[React Frontend (Dashboard)]
    end

    subgraph BackendServer [Flask Backend Server]
        API[REST API Endpoints]
        WebSocket[WebSocket Server]
    end

    subgraph AgentSystem [ADK Agent System (Separate Processes/Services)]
        Orchestrator(OrchestratorAgent)
        Agent1(SpecializedAgent 1 e.g., BusinessPlanner)
        Agent2(SpecializedAgent 2 e.g., Marketing)
        AgentN(...)
        A2A((A2A Protocol Layer))
    end

    subgraph ExternalServices
        Stripe[Stripe API]
        MCP[MCP Servers]
        OtherAPIs[...]
    end

    Frontend -- HTTP Requests --> API
    API -- HTTP/WebSocket --> Frontend
    API -- Trigger/Query --> Orchestrator
    Orchestrator -- A2A Calls --> A2A
    A2A -- A2A Calls --> Agent1
    A2A -- A2A Calls --> Agent2
    A2A -- A2A Calls --> AgentN
    Agent1 -- API Calls --> ExternalServices
    Agent2 -- API Calls --> ExternalServices
    AgentN -- API Calls --> ExternalServices
    WebSocket -- Real-time Updates --> Frontend

    style AgentSystem fill:#f9f,stroke:#333,stroke-width:2px
```

## 2. Integration Strategy Details

*   **Agent Hosting:** ADK agents (`OrchestratorAgent`, `SpecializedAgent`s) will run as separate Python processes/services, managed by the ADK framework (e.g., in separate Docker containers).
*   **A2A Communication:** Communication *between* agents will strictly adhere to the A2A protocol standard (likely using HTTP/S transport), managed via ADK.
*   **Orchestrator Role (`OrchestratorAgent`):** A *new* ADK agent acting as the central coordinator. It receives tasks from the backend, breaks them down, delegates via A2A, monitors progress, and reports back. Logic from `archon_agent.py` could be refactored into specialized agents under this orchestrator.
*   **Workflow Integration (`AutomationPage.jsx`):** Start by defining high-level *goals* or *templates* in the UI (e.g., "Create Membership Site") that trigger the orchestrator. Evolve to a more complex workflow builder later if needed.
*   **Frontend-Backend Communication:** Use REST API calls from frontend to backend to trigger orchestrator tasks. Use WebSockets for real-time status updates from the backend (informed by the orchestrator) back to the frontend.

## 3. Key Components (New or Significantly Modified)

*   **Backend:**
    *   `OrchestratorAgent` (New ADK Agent)
    *   `SpecializedAgent`s (New ADK Agents - e.g., `BusinessPlannerAgent`, `MarketingAgent`)
    *   `adk_runtime` configuration
    *   `a2a_layer` configuration
    *   `routes/orchestrator.py` (New Flask blueprint)
    *   `websocket_server.py` (New/Integrated)
    *   `models/task.py` (New/Modified Task model)
*   **Frontend:**
    *   `components/OrchestratorPanel.jsx` (New UI)
    *   `services/websocketService.js` (New)
    *   `services/api.js` (Modified - add orchestrator calls)
    *   `components/AutomationPage.jsx` (Modified - adapt to goals/templates)
    *   State Management (Modified - handle WebSocket updates)

## 4. API Endpoint Definitions (Backend)

*   **`POST /api/orchestrator/tasks`**:
    *   Purpose: Initiate a new task for the `OrchestratorAgent`.
    *   Request: `{ "goal": "...", "parameters": { ... } }`
    *   Response: `{ "taskId": "...", "status": "pending", ... }`
    *   Action: Backend validates, creates task record, forwards to Orchestrator, subscribes client WebSocket.
*   **`GET /api/orchestrator/tasks/{taskId}`**:
    *   Purpose: Get task status/result (polling fallback).
    *   Response: `{ "taskId": "...", "status": "...", "result": { ... } | null, ... }`
*   **`GET /api/orchestrator/agents`** (Optional):
    *   Purpose: List available specialized agents and capabilities.
    *   Response: `[ { "agentId": "...", "name": "...", ... } ]`
*   **WebSocket Endpoint (`/ws`)**:
    *   Purpose: Real-time status updates.
    *   Server Pushes: `{ "type": "status_update", "taskId": "...", ... }` or `{ "type": "result", "taskId": "...", ... }`.

## 5. Summary Diagram (Sequence)

```mermaid
sequenceDiagram
    participant FE as Frontend (React)
    participant BE as Backend (Flask API + WS)
    participant Orch as OrchestratorAgent (ADK)
    participant SA as SpecializedAgent (ADK)
    participant Ext as External Service (e.g., Stripe)

    FE->>+BE: POST /api/orchestrator/tasks (goal: "Create Site")
    BE->>BE: Create Task Record (taskId: 123, status: pending)
    BE->>+Orch: Initiate Task (goal: "Create Site", taskId: 123)
    BE-->>-FE: Response (taskId: 123, status: pending)
    FE->>+BE: WebSocket Connect (/ws, subscribe: taskId=123)
    BE-->>-FE: WebSocket Connected

    Orch->>Orch: Break down goal
    Orch->>+SA: A2A Call (subtask: "Plan Business Model")
    SA->>SA: Process subtask
    SA-->>-Orch: A2A Response (plan details)
    Orch->>BE: Update Task Status (taskId: 123, status: running, message: "Planning complete")
    BE-->>FE: WebSocket Push (update for taskId 123)

    Orch->>+SA: A2A Call (subtask: "Integrate Stripe")
    SA->>+Ext: API Call (create Stripe product)
    Ext-->>-SA: API Response (success)
    SA-->>-Orch: A2A Response (integration complete)
    Orch->>BE: Update Task Status (taskId: 123, status: running, message: "Stripe integrated")
    BE-->>FE: WebSocket Push (update for taskId 123)

    Orch->>Orch: Aggregate results
    Orch->>BE: Update Task Status (taskId: 123, status: completed, result: { ... })
    BE-->>FE: WebSocket Push (final result for taskId 123)
    BE->>BE: Update Task Record (status: completed)