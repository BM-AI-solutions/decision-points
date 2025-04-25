+++
id = "PLAN-SAAS-REFACTOR-20250420"
title = "Plan: Refactoring for Dockerized AI Agent SAAS Platform (A2A/ADK)"
status = "Draft"
created_date = "2025-04-20"
updated_date = "2025-04-20"
author = "core-architect"
related_tasks = ["TASK-ARCH-20250420-225348", "TASK-CMD-20250420-225200"]
tags = ["planning", "architecture", "refactor", "saas", "docker", "a2a", "adk"]
+++

# Planning Document: Refactoring for Dockerized AI Agent SAAS Platform

## 1. Introduction & Goals

This document outlines the plan for refactoring the `decision-points` project into a scalable, maintainable, and robust Dockerized Software-as-a-Service (SAAS) platform centered around AI agents communicating via Google's Agent-to-Agent (A2A) protocol and utilizing the Agent Development Kit (ADK).

**Key Goals:**

*   Establish a production-ready Dockerized architecture.
*   Refine the existing agent system for SAAS suitability, adhering to A2A/ADK best practices.
*   Improve scalability, maintainability, security, and observability.
*   Define a clear refactoring roadmap.

## 2. Current State Assessment

### 2.1. Stack Assessment

*   **Backend:** Python 3.10 / FastAPI / SQLAlchemy / Alembic / PostgreSQL.
    *   **Suitability:** Excellent choice for a modern SAAS backend. FastAPI provides high performance and async capabilities suitable for I/O-bound agent interactions. SQLAlchemy/Alembic offer robust ORM and migration support.
    *   **Recommendations:** No major stack changes recommended. Focus on configuration, optimization, and potential library upgrades.
*   **Frontend:** React / Vite / Plain CSS.
    *   **Suitability:** Solid foundation for a dynamic web application. Vite provides a fast development experience.
    *   **Recommendations:** Consider adopting a UI component library (e.g., MUI, Ant Design, Shadcn UI) for faster development and consistency as the SAAS UI grows. Evaluate state management solutions (e.g., Zustand, Redux Toolkit) if complexity increases significantly.
*   **AI Agents:** Google ADK / Gemini / Exa / Firecrawl / Various APIs.
    *   **Suitability:** Aligned with the target A2A/ADK direction. Leverages modern AI tooling.
    *   **Recommendations:** Requires significant refactoring for SAAS (see Agent System Evaluation).
*   **Infrastructure:** Docker / Docker Compose (Dev/Prod).
    *   **Suitability:** Good starting point for containerization.
    *   **Recommendations:** Refine Dockerfiles and Compose setup for production best practices (see Dockerization Plan). Consider Kubernetes or similar orchestrators for future scaling beyond single-node Compose deployments.

### 2.2. Agent System Evaluation (`backend/agents`)

*   **Structure:** Agents are individual Python files within `backend/agents`. Orchestrator and Workflow Manager handle coordination.
*   **A2A/ADK Implementation:**
    *   `OrchestratorAgent` uses `invoke_skill` for basic delegation based on LLM classification.
    *   `WorkflowManagerAgent` uses `invoke_skill` for multi-step, stateful workflows managed via Firestore. Includes retry logic.
    *   Communication relies on ADK's mechanisms. SocketIO is used separately for frontend updates.
*   **Strengths:**
    *   Leverages ADK framework.
    *   Clear separation between orchestration/workflow and specialized agents.
    *   Stateful workflow management implemented (`WorkflowManagerAgent`).
    *   Basic A2A communication (`invoke_skill`) is present.
*   **Weaknesses & Refactoring Areas:**
    *   **Configuration/Secrets:** Agents (e.g., `OrchestratorAgent`, `WorkflowManagerAgent`) appear to load API keys/config directly from environment variables or pass them during invocation. This is not secure or scalable for SAAS. Secrets management needs centralization (e.g., Vault, Cloud Secret Manager integration accessible via a secure configuration service).
    *   **Agent Discovery/Registration:** Agent IDs seem hardcoded or passed during initialization. A dynamic registration/discovery mechanism is needed for SAAS where agents might be added/updated independently.
    *   **A2A Communication:** While `invoke_skill` is used, the presence of `_invoke_a2a_agent` in `WorkflowManagerAgent` suggests potential inconsistency or legacy code. Standardize on ADK's `invoke_skill`. The underlying transport (HTTP, gRPC?) and its scalability need review.
    *   **Multi-Tenancy:** Current implementation doesn't explicitly address multi-tenancy. State management (Firestore), agent invocation, and data isolation need to be designed with tenant separation in mind. Firestore rules or alternative state stores might be needed.
    *   **Error Handling:** While `WorkflowManagerAgent` has retry logic, cross-agent error propagation and monitoring need standardization.
    *   **Observability:** Logging exists, but structured logging, tracing across agent calls (OpenTelemetry), and metrics are crucial for SAAS monitoring and debugging.
    *   **Testing:** Lack of apparent unit/integration tests for agents. This is critical for reliability.
    *   **Scalability:** Running all agents within the main backend container (implied by current structure) won't scale. Agents likely need to run as separate services/processes.

### 2.3. Docker Implementation Assessment

*   **Backend Dockerfile:**
    *   Uses multi-stage builds (Good).
    *   `prod` CMD needs correction (`app:app` -> `app.main:app`). (Action Item)
    *   `prod` stage copies entire context (`COPY . .`); can be optimized. (Action Item)
    *   Consider running as non-root user in `prod`. (Action Item)
*   **Frontend Dockerfile:**
    *   Standard multi-stage build using Node/Nginx (Good).
*   **Docker Compose:**
    *   Separate `dev` and `prod` files (Good).
    *   `dev` uses volumes and dev servers (Standard).
    *   `prod` uses baked images (Standard).
    *   Missing services: PostgreSQL DB, potentially Redis (for caching/queuing), and dedicated agent services. (Action Item)

## 3. Target Architecture

### 3.1. High-Level Overview

The target architecture will be a containerized microservices-based system deployed via Docker (initially Compose, potentially K8s later).

*   **Core API (FastAPI):** Handles user authentication, API requests, basic CRUD, and potentially acts as the initial entry point for agent tasks.
*   **Frontend (React/Nginx):** Serves the user interface.
*   **Database (PostgreSQL):** Persistent storage for core application data (users, tenants, etc.).
*   **Agent Runtime/Orchestration Service:** A dedicated service responsible for:
    *   Receiving agent task requests (from Core API or message queue).
    *   Managing agent lifecycles (scaling up/down based on load).
    *   Discovering and routing requests to appropriate agent services using A2A.
    *   Handling A2A communication infrastructure (potentially abstracting `invoke_skill`).
    *   Managing shared agent state/context if needed (securely).
*   **Specialized Agent Services:** Each agent (or logical groups of agents) runs as a separate Docker service. They register with the Orchestration Service and expose skills via ADK.
*   **Workflow State Store (Firestore/Alternative):** Manages state for long-running workflows (consider multi-tenant implications).
*   **Message Queue (e.g., Kafka, RabbitMQ, Google Pub/Sub):** For decoupling services, handling asynchronous tasks, and potentially agent communication/eventing.
*   **Configuration Service:** Centralized, secure management of configuration and secrets.
*   **Observability Stack:** Logging aggregation (e.g., ELK/Loki), metrics (Prometheus/Grafana), tracing (Jaeger/Tempo).

### 3.2. Dockerization Plan

*   **Services:**
    *   `backend` (FastAPI Core API)
    *   `frontend` (Nginx serving React build)
    *   `postgres` (PostgreSQL Database)
    *   `redis` (Optional: Caching/Session Store/Queue)
    *   `agent-runtime` (Dedicated service for orchestration/A2A routing)
    *   `agent-<name>` (Individual services for each specialized agent or agent group, e.g., `agent-market-research`, `agent-branding`)
    *   `workflow-manager` (Dedicated service for the Workflow Manager agent, interacting with state store)
    *   (Optional) `kafka` / `zookeeper` or other message queue broker.
    *   (Optional) Observability services (Prometheus, Grafana, Loki, etc.)
*   **Networking:** Define clear Docker networks (e.g., `frontend-net`, `backend-net`, `agent-net`) to control communication between services.
*   **Volumes:** Use named volumes for persistent data (Postgres, potentially state stores, message queues).
*   **Build Process:**
    *   Optimize backend Dockerfile (`prod` stage `COPY`, non-root user, correct `CMD`).
    *   Create Dockerfiles for `agent-runtime`, `workflow-manager`, and individual agent services. These should leverage ADK's agent serving capabilities.
    *   Ensure consistent base images and dependency management across Python services.
*   **Compose Files:**
    *   Refactor `docker-compose.prod.yml` to include all necessary services (DB, Redis, agents, etc.).
    *   Refactor `docker-compose.dev.yml` for the new service structure, potentially using profiles to manage optional services. Use volumes for code mounting during development for relevant services.

### 3.3. A2A/ADK Integration Strategy

*   **Standardize on `invoke_skill`:** Remove the `_invoke_a2a_agent` HTTP method from `WorkflowManagerAgent`.
*   **Agent Runtime Service:** This service acts as the central hub for A2A.
    *   Agents register their ID, address (internal Docker DNS name), and available skills upon startup.
    *   The runtime service receives invocation requests (e.g., from the Core API or Workflow Manager) specifying the target agent *type* or *capability* rather than a hardcoded ID.
    *   It looks up a suitable, available agent instance and uses `invoke_skill` (or the underlying ADK mechanism) to call it.
    *   This abstracts the direct agent-to-agent call logic from the Workflow Manager and Orchestrator.
*   **Agent Services:** Each agent runs as a standalone ADK agent server (using `adk serve` or similar).
*   **Configuration:** Agent-specific configurations (models, prompts, external API keys) are managed centrally and securely injected via the Configuration Service, not environment variables directly within the agent code.
*   **State Management:** Firestore remains an option for workflow state, but needs careful design for multi-tenancy (e.g., tenant ID prefix in document IDs, Firestore rules). Evaluate alternatives like a tenant-sharded database or Redis streams if Firestore costs/scalability become a concern.

## 4. Refactoring Plan (High-Level Roadmap)

**Phase 1: Foundational Docker & Backend Refactoring**

1.  **Correct & Optimize Dockerfiles:** Fix backend `prod` CMD, optimize `COPY`, implement non-root user execution.
2.  **Refactor Docker Compose:** Introduce `postgres` service in both `dev` and `prod`. Update service configurations. Ensure basic backend/frontend/db setup works reliably.
3.  **Centralize Configuration:** Implement basic configuration loading (e.g., using Pydantic Settings) separate from agent code. Introduce `.env` handling at the Compose level. (Defer full secret management service for now).
4.  **Basic Agent Service Separation (Proof of Concept):**
    *   Create a Dockerfile for one simple agent (e.g., `WebSearchAgent`).
    *   Add it as a separate service (`agent-web-search`) in Compose.
    *   Modify `OrchestratorAgent` to use `invoke_skill` targeting the new service's internal DNS name (requires basic service discovery/registration placeholder).

**Phase 2: Agent Runtime & A2A Enhancement**

1.  **Develop Agent Runtime Service:** Implement the core logic for agent registration, discovery, and `invoke_skill` routing.
2.  **Refactor Orchestrator/Workflow Manager:** Modify these agents to interact with the Agent Runtime Service instead of calling `invoke_skill` directly or managing agent IDs.
3.  **Migrate Agents to Services:** Containerize remaining agents (`Branding`, `MarketResearch`, etc.) as separate services registering with the Agent Runtime.
4.  **Standardize A2A:** Ensure all inter-agent communication goes through the Agent Runtime Service using ADK patterns. Remove legacy HTTP invocation code.
5.  **Implement Secure Configuration Injection:** Integrate a proper secrets management solution (e.g., Vault injector, Cloud Secret Manager client in a dedicated config loader) accessed by agents at startup.

**Phase 3: SAAS Enablement & Advanced Features**

1.  **Implement Multi-Tenancy:**
    *   Introduce tenant context in API requests and agent invocations.
    *   Adapt database schemas and queries for tenant isolation.
    *   Refine Firestore usage (or alternative) for tenant-specific workflow state.
2.  **Implement User Authentication/Authorization:** Integrate robust auth across Core API and potentially agent interactions.
3.  **Enhance Observability:** Implement structured logging, distributed tracing (OpenTelemetry) across API and agent services, and expose key metrics (Prometheus).
4.  **Develop Testing Strategy:** Implement unit and integration tests for Core API and individual agents. Develop end-to-end tests for key workflows.
5.  **Refine Frontend:** Implement UI library, improve state management, build SAAS-specific features (tenant dashboards, user management, billing integration).
6.  **Introduce Message Queue:** Evaluate and implement Kafka/RabbitMQ/PubSub for asynchronous task processing and potentially agent eventing to improve resilience and scalability.

## 5. Key Decisions & Potential ADRs

*   **Agent Service Granularity:** Run each agent as a separate service vs. grouping related agents? (Initial plan: separate services for flexibility).
*   **A2A Communication Transport:** Rely solely on ADK's default (likely HTTP) or explore alternatives like gRPC if performance becomes critical?
*   **Workflow State Store:** Continue with Firestore or migrate to SQL/Redis/other based on multi-tenancy/cost/performance needs?
*   **Secrets Management Solution:** Vault vs. Cloud Provider specific (e.g., GCP Secret Manager, AWS Secrets Manager)?
*   **Service Discovery Mechanism:** How exactly do agents register with the Agent Runtime (e.g., simple API call on startup, Consul, Kubernetes service discovery)?
*   **Message Queue Choice:** Kafka vs. RabbitMQ vs. Google Pub/Sub vs. Redis Streams?
*   **Observability Stack:** Specific tools for logging, metrics, tracing (ELK, Loki, Prometheus, Grafana, Jaeger, Tempo, etc.).
*   **Frontend UI Library:** Which library to adopt (MUI, AntD, Shadcn, etc.)?

## 6. Next Steps

*   Review and refine this plan.
*   Create specific sub-tasks for Phase 1 items.
*   Start implementing Phase 1, beginning with Dockerfile/Compose corrections.
*   Initiate ADRs for key decisions identified above.