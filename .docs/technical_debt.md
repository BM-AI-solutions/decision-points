# Technical Debt & Future Enhancements

This document tracks known temporary fixes that should be addressed for production readiness and potential areas for future enhancement.

## Temporary Fixes (Require Refactoring)

*   **Workflow Resumption Signaling:**
    *   **Issue:** The current mechanism where the `/a2a/workflow/<workflow_run_id>/resume` API endpoint signals the paused `WorkflowManagerAgent` relies on finding and setting an in-memory `asyncio.Event` object stored in a global dictionary (`workflow_approval_events` in `app.py`).
    *   **Problem:** This approach is fragile. It will break if the application runs with multiple worker processes (common in production) or if the server restarts, as the in-memory event object will be lost or inaccessible across processes.
    *   **Required Fix:** Refactor the resume mechanism. The API endpoint should likely *only* update the workflow status in Firestore (e.g., to 'approved_resuming'). A separate, robust mechanism is needed to detect this status change and trigger the `WorkflowManagerAgent`'s resumption logic. Options include:
        *   A background task scheduler (like Celery, APScheduler, or Arq) that periodically polls Firestore for workflows needing resumption.
        *   Modifying the `OrchestratorAgent` or API endpoint to trigger a *new* invocation of the `WorkflowManagerAgent` specifically for resumption, passing the `workflow_run_id`.
        *   Using Firestore listeners (if feasible in the deployment environment) to trigger resumption logic.

## Areas for Future Enhancement

*   **Agent Sophistication:**
    *   **DeploymentAgent:** Implement deployment to more platforms (Cloud Run, AWS, etc.) and handle more complex application types (e.g., backends, databases). Add automated configuration for build steps on platforms like Netlify.
    *   **BrandingAgent:** Use availability check results to directly influence the LLM's final `selected_brand_name` recommendation, not just provide notes. Integrate domain checking APIs or image generation for logos.
    *   **CodeGenerationAgent:** Improve the quality and complexity of generated code. Add support for different frameworks or backend generation. Implement dynamic insertion of real Analytics/AdSense IDs based on user configuration.
    *   **ImprovementAgent:** Enhance feasibility analysis, potentially using more tools or structured data.
    *   **MarketResearchAgent:** Improve data synthesis and add more diverse data sources/tools.
    *   **Tool Integration:** Increase inter-agent tool usage (e.g., `ImprovementAgent` using `ContentGenerationAgent` for descriptions).
*   **Workflow Robustness:**
    *   Implement more granular user feedback loops (e.g., approval after Branding).
    *   Add more sophisticated conditional logic within the `WorkflowManagerAgent`.
    *   Explore alternative A2A communication (e.g., message queues) for scalability.
*   **Monitoring & Logging:** Implement comprehensive observability across agents and workflows.
*   **Monetization:** Move beyond placeholder AdSense to integrate other methods or allow configuration.
*   **Security:** Perform thorough security reviews, especially around API key handling and external API interactions.