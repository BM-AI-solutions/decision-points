<!DOCTYPE html>
<html lang="en"><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
  <meta charset="UTF-8">
  <title>Technical Documentation</title>
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
  <meta name="description" content="An open protocol enabling communication and interoperability between opaque agentic applications.">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
  <link rel="stylesheet" href="a2aDocumentation_files/vue.css">
  <link rel="stylesheet" href="a2aDocumentation_files/dark.css" media="(prefers-color-scheme: dark)">
  <!-- index.html -->
<style>
.sidebar {
  padding-top: 0;
}

.search {
  margin-bottom: 20px;
  padding: 6px;
  border-bottom: 1px solid #eee;
}

.search .input-wrap {
  display: flex;
  align-items: center;
}

.search .results-panel {
  display: none;
}

.search .results-panel.show {
  display: block;
}

.search input {
  outline: none;
  border: none;
  width: 100%;
  padding: 0.6em 7px;
  font-size: inherit;
  border: 1px solid transparent;
}

.search input:focus {
  box-shadow: 0 0 5px var(--theme-color, #42b983);
  border: 1px solid var(--theme-color, #42b983);
}

.search input::-webkit-search-decoration,
.search input::-webkit-search-cancel-button,
.search input {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.search input::-ms-clear {
  display: none;
  height: 0;
  width: 0;
}

.search .clear-button {
  cursor: pointer;
  width: 36px;
  text-align: right;
  display: none;
}

.search .clear-button.show {
  display: block;
}

.search .clear-button svg {
  transform: scale(.5);
}

.search h2 {
  font-size: 17px;
  margin: 10px 0;
}

.search a {
  text-decoration: none;
  color: inherit;
}

.search .matching-post {
  border-bottom: 1px solid #eee;
}

.search .matching-post:last-child {
  border-bottom: 0;
}

.search p {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.search p.empty {
  text-align: center;
}

.app-name.hide, .sidebar-nav.hide {
  display: none;
}</style></head>
<body data-page="documentation.md" class="ready sticky close">
  <nav class="app-nav no-badge"><ul><li><a href="https://github.com/google/A2A" target="_blank" rel="noopener" title="Github repo">Github repo</a></li><li><a href="https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/" target="_blank" rel="noopener" title="Blog">Blog</a></li><li><a href="https://github.com/google/A2A/tree/main/samples" target="_blank" rel="noopener" title="Sample Agents">Sample Agents</a><ul><li><a href="https://github.com/google/A2A/tree/main/samples/python/agents/google_adk/README.md" target="_blank" rel="noopener" title="Google Agent Developer Kit (ADK)">Google Agent Developer Kit (ADK)</a></li><li><a href="https://github.com/google/A2A/tree/main/samples/python/agents/crewai/README.md" target="_blank" rel="noopener" title="CrewAI">CrewAI</a></li><li><a href="https://github.com/google/A2A/tree/main/samples/python/agents/langgraph/README.md" target="_blank" rel="noopener" title="LangGraph">LangGraph</a></li><li><a href="https://github.com/google/A2A/tree/main/samples/js/src/agents/README.md" target="_blank" rel="noopener" title="Genkit">Genkit</a></li></ul></li></ul></nav><main><button class="sidebar-toggle" aria-label="Menu"><div class="sidebar-toggle-button"><span></span><span></span><span></span></div></button><aside class="sidebar"><div class="search"><div class="input-wrap">
      <input type="search" aria-label="Search text" placeholder="Type to search">
      <div class="clear-button">
        <svg width="26" height="24">
          <circle cx="12" cy="12" r="11" fill="#ccc"></circle>
          <path stroke="white" stroke-width="2" d="M8.25,8.25,15.75,15.75"></path>
          <path stroke="white" stroke-width="2" d="M8.25,15.75,15.75,8.25"></path>
        </svg>
      </div>
    </div>
    <div class="results-panel"></div>
    </div><div class="sidebar-nav"><!-- docs/_sidebar.md -->

<ul><li><a href="#/" title="Home">Home</a></li><li><a href="https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/" target="_blank" rel="noopener" title="Blog Post">Blog Post</a></li><li class=""><a href="#/documentation" title="Technical Documentation">Technical Documentation</a><ul class="app-sub-sidebar"><li class="active"><a class="section-link" href="#/documentation?id=feedback-and-changes" title="Feedback and Changes">Feedback and Changes</a></li><li class=""><a class="section-link" href="#/documentation?id=key-principles" title="Key Principles">Key Principles</a></li><li class=""><a class="section-link" href="#/documentation?id=overview" title="Overview">Overview</a></li><li class=""><a class="section-link" href="#/documentation?id=agent-card" title="Agent Card">Agent Card</a></li><li class=""><a class="section-link" href="#/documentation?id=agent-to-agent-communication" title="Agent-to-Agent Communication">Agent-to-Agent Communication</a></li><li class=""><a class="section-link" href="#/documentation?id=core-objects" title="Core Objects">Core Objects</a></li><li><a class="section-link" href="#/documentation?id=sample-methods-and-json-responses" title="Sample Methods and JSON Responses">Sample Methods and JSON Responses</a></li><ul class="app-sub-sidebar"><li class=""><a class="section-link" href="#/documentation?id=agent-card-1" title="Agent Card">Agent Card</a></li><li class=""><a class="section-link" href="#/documentation?id=send-a-task" title="Send a Task">Send a Task</a></li><li class=""><a class="section-link" href="#/documentation?id=get-a-task" title="Get a Task">Get a Task</a></li><li class=""><a class="section-link" href="#/documentation?id=cancel-a-task" title="Cancel a Task">Cancel a Task</a></li><li class=""><a class="section-link" href="#/documentation?id=set-task-push-notification-config" title="Set Task Push Notification Config">Set Task Push Notification Config</a></li><li class=""><a class="section-link" href="#/documentation?id=get-task-push-notification-config" title="Get Task Push Notification Config">Get Task Push Notification Config</a></li><li class=""><a class="section-link" href="#/documentation?id=multi-turn-conversations" title="Multi-turn Conversations">Multi-turn Conversations</a></li><li class=""><a class="section-link" href="#/documentation?id=streaming-support" title="Streaming Support">Streaming Support</a></li><li class=""><a class="section-link" href="#/documentation?id=non-textual-media" title="Non-textual Media">Non-textual Media</a></li><li class=""><a class="section-link" href="#/documentation?id=structured-output" title="Structured output">Structured output</a></li><li><a class="section-link" href="#/documentation?id=error-handling" title="Error Handling">Error Handling</a></li></ul></ul></li><li>Review Key Topics<ul><li><a href="#/topics/a2a_and_mcp" title="A2A and MCP">A2A and MCP</a></li><li><a href="#/topics/agent_discovery" title="Agent Discovery">Agent Discovery</a></li><li><a href="#/topics/enterprise_ready" title="Enterprise Ready">Enterprise Ready</a></li><li><a href="#/topics/push_notifications" title="Push Notifications">Push Notifications</a></li></ul></li><li><a href="https://github.com/google/A2A/tree/main/specification/json" target="_blank" rel="noopener" title="Json Specification">Json Specification</a></li><li><a href="https://github.com/google/A2A/tree/main/samples" target="_blank" rel="noopener" title="Samples to see A2A in action">Samples to see A2A in action</a><ul><li><a href="https://github.com/google/A2A/tree/main/samples/python/common" target="_blank" rel="noopener" title="Sample A2A Client/Server">Sample A2A Client/Server</a></li><li><a href="https://github.com/google/A2A/tree/main/demo/README.md" target="_blank" rel="noopener" title="Multi-Agent Web App">Multi-Agent Web App</a></li><li><a href="https://github.com/google/A2A/blob/main/samples/python/hosts/cli/README.md" target="_blank" rel="noopener" title="CLI">CLI</a></li></ul></li><li><a href="https://github.com/google/A2A/tree/main/samples" target="_blank" rel="noopener" title="Sample Agents">Sample Agents</a><ul><li><a href="https://github.com/google/A2A/tree/main/samples/python/agents/google_adk/README.md" target="_blank" rel="noopener" title="Google Agent Developer Kit (ADK)">Google Agent Developer Kit (ADK)</a></li><li><a href="https://github.com/google/A2A/tree/main/samples/python/agents/crewai/README.md" target="_blank" rel="noopener" title="CrewAI">CrewAI</a></li><li><a href="https://github.com/google/A2A/tree/main/samples/python/agents/langgraph/README.md" target="_blank" rel="noopener" title="LangGraph">LangGraph</a></li><li><a href="https://github.com/google/A2A/tree/main/samples/js/src/agents/README.md" target="_blank" rel="noopener" title="Genkit">Genkit</a></li></ul></li></ul></div></aside><section class="content"><article class="markdown-section" id="main"><h1 id="agent2agent-protocol-a2a"><a href="#/documentation?id=agent2agent-protocol-a2a" data-id="agent2agent-protocol-a2a" class="anchor"><span>Agent2Agent Protocol (A2A)</span></a></h1><p>An open protocol enabling Agent-to-Agent interoperability, bridging the gap between <strong>opaque</strong> agentic systems.
<img src="a2aDocumentation_files/a2a_actors.png" width="70%" style="margin:20px auto;display:block;"></p><!-- TOC -->

<ul><li><a href="#/documentation?id=agent2agent-protocol-a2a">Agent2Agent Protocol A2A</a><ul><li><a href="#/documentation?id=feedback-and-changes">Feedback and Changes</a></li><li><a href="#/documentation?id=key-principles">Key Principles</a></li><li><a href="#/documentation?id=more-detailed-discussions">More Detailed Discussions</a></li><li><a href="#/documentation?id=overview">Overview</a><ul><li><a href="#/documentation?id=actors">Actors</a></li><li><a href="#/documentation?id=transport">Transport</a></li><li><a href="#/documentation?id=authentication-and-authorization">Authentication and Authorization</a></li></ul></li><li><a href="#/documentation?id=agent-card">Agent Card</a><ul><li><a href="#/documentation?id=discovery">Discovery</a></li><li><a href="#/documentation?id=representation">Representation</a></li></ul></li><li><a href="#/documentation?id=agent-to-agent-communication">Agent-to-Agent Communication</a></li><li><a href="#/documentation?id=core-objects">Core Objects</a><ul><li><a href="#/documentation?id=task">Task</a></li><li><a href="#/documentation?id=artifact">Artifact</a></li><li><a href="#/documentation?id=message">Message</a></li><li><a href="#/documentation?id=part">Part</a></li><li><a href="#/documentation?id=push-notifications">Push Notifications</a></li></ul></li></ul></li><li><a href="#/documentation?id=sample-methods-and-json-responses">Sample Methods and JSON Responses</a><ul><li><a href="#/documentation?id=agent-card">Agent Card</a></li><li><a href="#/documentation?id=send-a-task">Send a Task</a></li><li><a href="#/documentation?id=get-a-task">Get a Task</a></li><li><a href="#/documentation?id=cancel-a-task">Cancel a Task</a></li><li><a href="#/documentation?id=set-task-push-notifications">Set Task Push Notifications</a></li><li><a href="#/documentation?id=get-task-push-notifications">Get Task Push Notifications</a></li><li><a href="#/documentation?id=multi-turn-conversations">Multi-turn Conversations</a></li><li><a href="#/documentation?id=streaming-support">Streaming Support</a><ul><li><a href="#/documentation?id=resubscribe-to-task">Resubscribe to Task</a></li></ul></li><li><a href="#/documentation?id=non-textual-media">Non-textual Media</a></li><li><a href="#/documentation?id=structured-output">Structured output</a></li><li><a href="#/documentation?id=error-handling">Error Handling</a></li></ul></li></ul><!-- /TOC -->

<h2 id="feedback-and-changes"><a href="#/documentation?id=feedback-and-changes" data-id="feedback-and-changes" class="anchor"><span>Feedback and Changes</span></a></h2><p>A2A
 is a work in progress and is expected to change based on community 
feedback. This repo contains the initial specification, documentation, 
and <a href="https://github.com/google/A2A/tree/main/samples" target="_blank" rel="noopener">sample code</a>.
 We will continue to update this repo with more features, more examples,
 specs, and libraries as they become available. When the spec and 
samples can graduate to a production quality SDK, we will declare 
version 1.0 and maintain stable releases.</p><h2 id="key-principles"><a href="#/documentation?id=key-principles" data-id="key-principles" class="anchor"><span>Key Principles</span></a></h2><p>Using
 A2A, agents accomplish tasks for end-users without sharing memory, 
thoughts, or tools. Instead the agents exchange context, status, 
instructions, and data in their native modalities.</p><ul><li><strong>Simple</strong>: Reuse existing standards</li><li><strong>Enterprise Ready</strong>: Auth, Security, Privacy, Tracing, Monitoring</li><li><strong>Async First</strong>: (Very) Long running-tasks and human-in-the-loop</li><li><strong>Modality Agnostic</strong>: text, audio/video, forms, iframe, etc.</li><li><strong>Opaque Execution</strong>: Agents do not have to share thoughts, plans, or tools.</li></ul><h3 id="more-detailed-discussions"><a href="#/documentation?id=more-detailed-discussions" data-id="more-detailed-discussions" class="anchor"><span>More Detailed Discussions</span></a></h3><ul><li><a href="#/topics/a2a_and_mcp?id=a2a-%e2%9d%a4%ef%b8%8f-mcp">A2A and MCP</a></li><li><a href="#/topics/enterprise_ready?id=enterprise-readiness">Enterprise Ready</a></li><li><a href="#/topics/push_notifications?id=remote-agent-to-client-updates">Push Notifications</a></li><li><a href="#/topics/agent_discovery?id=discovering-agent-cards">Agent Discovery</a></li></ul><h2 id="overview"><a href="#/documentation?id=overview" data-id="overview" class="anchor"><span>Overview</span></a></h2><h3 id="actors"><a href="#/documentation?id=actors" data-id="actors" class="anchor"><span>Actors</span></a></h3><p>The A2A protocol has three actors:</p><ul><li><strong>User</strong><br>The end-user (human or service) that is using an agentic system to accomplish tasks.</li><li><strong>Client</strong><br>The entity (service, agent, application) that is requesting an action from an opaque agent on behalf of the user.</li><li><strong>Remote Agent (Server)</strong><br>The opaque ("blackbox") agent which is the A2A server.</li></ul><h3 id="transport"><a href="#/documentation?id=transport" data-id="transport" class="anchor"><span>Transport</span></a></h3><p>The
 protocol leverages HTTP for transport between the client and the remote
 agent. Depending on the capabilities of the client and the remote 
agent, they may leverage SSE for supporting streaming for receiving 
updates from the server.</p><p>A2A leverages <a href="https://www.jsonrpc.org/specification" target="_blank" rel="noopener">JSON-RPC 2.0</a> as the data exchange format for communication between a Client and a Remote Agent.</p><h3 id="async"><a href="#/documentation?id=async" data-id="async" class="anchor"><span>Async</span></a></h3><p>A2A
 clients and servers can use standard request/response patterns and poll
 for updates. However, A2A also supports streaming updates through SSE 
(while connected) and receiving <a href="#/topics/push_notifications?id=remote-agent-to-client-updates">push notifications</a> while disconnected.</p><h3 id="authentication-and-authorization"><a href="#/documentation?id=authentication-and-authorization" data-id="authentication-and-authorization" class="anchor"><span>Authentication and Authorization</span></a></h3><p>A2A
 models agents as enterprise applications (and can do so because A2A 
agents are opaque and do not share tools and resources). This quickly 
brings enterprise-readiness to agentic interop.</p><p>A2A follows <a href="https://swagger.io/docs/specification/v3_0/authentication/" target="_blank" rel="noopener">OpenAPI’s Authentication specification</a>
 for authentication. Importantly, A2A agents do not exchange identity 
information within the A2A protocol. Instead, they obtain materials 
(such as tokens) out of band and transmit materials in HTTP headers and 
not in A2A payloads.</p><p>While A2A does not transmit identity in-band,
 servers do send authentication requirements in A2A payloads. At 
minimum, servers are expected to publish their requirements in their <a href="#/documentation?id=agent-card">Agent Card</a>. Thoughts about discovering agent cards are in <a href="#/topics/agent_discovery?id=discovering-agent-cards">this topic</a>.</p><p>Clients
 should use one of the servers published authentication protocols to 
authenticate their identity and obtain credential material. A2A servers 
should authenticate <strong>every</strong> request and reject or 
challenge requests with standard HTTP response codes (401, 403), and 
authentication-protocol-specific headers and bodies (such as a HTTP 401 
response with a <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/WWW-Authenticate" target="_blank" rel="noopener">WWW-Authenticate</a>
 header indicating the required authentication schema, or OIDC discovery
 document at a well-known path). More details discussed in <a href="#/topics/enterprise_ready">Enterprise Ready</a>.</p><blockquote>
<p>Note: If an agent requires that the client/user provide additional 
credentials during execution of a task (for example, to use a specific 
tool), the agent should return a task status of <code>Input-Required</code> with the payload being an Authentication structure. The client should, again, obtain credential material out of band to A2A.</p></blockquote>
<h2 id="agent-card"><a href="#/documentation?id=agent-card" data-id="agent-card" class="anchor"><span>Agent Card</span></a></h2><p>Remote Agents that support A2A are required to publish an <strong>Agent Card</strong>
 in JSON format describing the agent’s capabilities/skills and 
authentication mechanism. Clients use the Agent Card information to 
identify the best agent that can perform a task and leverage A2A to 
communicate with that remote agent.</p><h3 id="discovery"><a href="#/documentation?id=discovery" data-id="discovery" class="anchor"><span>Discovery</span></a></h3><p>We recommend agents host their Agent Card at https://<code>base url</code>/.well-
known/agent.json. This is compatible with a DNS approach where the 
client finds the server IP via DNS and sends an HTTP GET to retrieve the
 agent card. We also anticipate that systems will maintain private 
registries (e.g. an ‘Agent Catalog’ or private marketplace, etc). More 
discussion can be found in <a href="#/topics/agent_discovery?id=discovering-agent-cards">this document</a>.</p><h3 id="representation"><a href="#/documentation?id=representation" data-id="representation" class="anchor"><span>Representation</span></a></h3><p>Following is the proposed representation of an Agent Card</p><pre v-pre="" data-lang="typescript"><code class="lang-typescript"><span class="token comment">// An AgentCard conveys key information:</span>
<span class="token comment">// - Overall details (version, name, description, uses)</span>
<span class="token comment">// - Skills: A set of capabilities the agent can perform</span>
<span class="token comment">// - Default modalities/content types supported by the agent.</span>
<span class="token comment">// - Authentication requirements</span>
<span class="token keyword">interface</span> <span class="token class-name">AgentCard</span> <span class="token punctuation">{</span>
  <span class="token comment">// Human readable name of the agent.</span>
  <span class="token comment">// (e.g. "Recipe Agent")</span>
  name<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  <span class="token comment">// A human-readable description of the agent. Used to assist users and</span>
  <span class="token comment">// other agents in understanding what the agent can do.</span>
  <span class="token comment">// (e.g. "Agent that helps users with recipes and cooking.")</span>
  description<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  <span class="token comment">// A URL to the address the agent is hosted at.</span>
  url<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  <span class="token comment">// The service provider of the agent</span>
  provider<span class="token operator">?</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    organization<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
    url<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  <span class="token punctuation">}</span><span class="token punctuation">;</span>
  <span class="token comment">// The version of the agent - format is up to the provider. (e.g. "1.0.0")</span>
  version<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  <span class="token comment">// A URL to documentation for the agent.</span>
  documentationUrl<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  <span class="token comment">// Optional capabilities supported by the agent.</span>
  capabilities<span class="token operator">:</span> <span class="token punctuation">{</span>
    streaming<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">boolean</span><span class="token punctuation">;</span> <span class="token comment">// true if the agent supports SSE</span>
    pushNotifications<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">boolean</span><span class="token punctuation">;</span> <span class="token comment">// true if the agent can notify updates to client</span>
    stateTransitionHistory<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">boolean</span><span class="token punctuation">;</span> <span class="token comment">//true if the agent exposes status change history for tasks</span>
  <span class="token punctuation">}</span><span class="token punctuation">;</span>
  <span class="token comment">// Authentication requirements for the agent.</span>
  <span class="token comment">// Intended to match OpenAPI authentication structure.</span>
  authentication<span class="token operator">:</span> <span class="token punctuation">{</span>
    schemes<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span> <span class="token comment">// e.g. Basic, Bearer</span>
    credentials<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span> <span class="token comment">//credentials a client should use for private cards</span>
  <span class="token punctuation">}</span><span class="token punctuation">;</span>
  <span class="token comment">// The set of interaction modes that the agent</span>
  <span class="token comment">// supports across all skills. This can be overridden per-skill.</span>
  defaultInputModes<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span> <span class="token comment">// supported mime types for input</span>
  defaultOutputModes<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span> <span class="token comment">// supported mime types for output</span>
  <span class="token comment">// Skills are a unit of capability that an agent can perform.</span>
  skills<span class="token operator">:</span> <span class="token punctuation">{</span>
    id<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span> <span class="token comment">// unique identifier for the agent's skill</span>
    name<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span> <span class="token comment">//human readable name of the skill</span>
    <span class="token comment">// description of the skill - will be used by the client or a human</span>
    <span class="token comment">// as a hint to understand what the skill does.</span>
    description<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
    <span class="token comment">// Set of tagwords describing classes of capabilities for this specific</span>
    <span class="token comment">// skill (e.g. "cooking", "customer support", "billing")</span>
    tags<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span>
    <span class="token comment">// The set of example scenarios that the skill can perform.</span>
    <span class="token comment">// Will be used by the client as a hint to understand how the skill can be</span>
    <span class="token comment">// used. (e.g. "I need a recipe for bread")</span>
    examples<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span> <span class="token comment">// example prompts for tasks</span>
    <span class="token comment">// The set of interaction modes that the skill supports</span>
    <span class="token comment">// (if different than the default)</span>
    inputModes<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span> <span class="token comment">// supported mime types for input</span>
    outputModes<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span> <span class="token comment">// supported mime types for output</span>
  <span class="token punctuation">}</span><span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span>
<span class="token punctuation">}</span></code></pre><h2 id="agent-to-agent-communication"><a href="#/documentation?id=agent-to-agent-communication" data-id="agent-to-agent-communication" class="anchor"><span>Agent-to-Agent Communication</span></a></h2><p>The communication between a Client and a Remote Agent is oriented towards <strong><em>task completion</em></strong>
 where agents collaboratively fulfill an end-user’s request. A Task 
object allows a Client and a Remote Agent to collaborate for completing 
the submitted task.</p><p>A task can be completed by a remote agent 
immediately or it can be long-running. For long-running tasks, the 
client may poll the agent for fetching the latest status. Agents can 
also push notifications to the client via SSE (if connected) or through 
an external notification service.</p><h2 id="core-objects"><a href="#/documentation?id=core-objects" data-id="core-objects" class="anchor"><span>Core Objects</span></a></h2><h3 id="task"><a href="#/documentation?id=task" data-id="task" class="anchor"><span>Task</span></a></h3><p>A
 Task is a stateful entity that allows Clients and Remote Agents to 
achieve a specific outcome and generate results. Clients and Remote 
Agents exchange Messages within a Task. Remote Agents generate results 
as Artifacts.</p><p>A Task is always created by a Client and the status 
is always determined by the Remote Agent. Multiple Tasks may be part of a
 common session (denoted by optional sessionId) if required by the 
client. To do so, the Client sets an optional sessionId when creating 
the Task.</p><p>The agent may:</p><ul><li>fulfill the request immediately</li><li>schedule work for later</li><li>reject the request</li><li>negotiate a different modality</li><li>ask the client for more information</li><li>delegate to other agents and systems</li></ul><p>Even
 after fulfilling the goal, the client can request more information or a
 change in the context of that same Task. (For example client: "draw a 
picture of a rabbit", agent: "&lt;picture&gt;", client: "make it red").</p><p>Tasks are used to transmit <a href="#/documentation?id=artifact">Artifacts</a> (results) and <a href="#/documentation?id=message">Messages</a> (thoughts, instructions, anything else). Tasks maintain a status and an optional history of status and Messages.</p><pre v-pre="" data-lang="typescript"><code class="lang-typescript"><span class="token keyword">interface</span> <span class="token class-name">Task</span> <span class="token punctuation">{</span>
  id<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span> <span class="token comment">// unique identifier for the task</span>
  sessionId<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span> <span class="token comment">// client-generated id for the session holding the task.</span>
  status<span class="token operator">:</span> TaskStatus<span class="token punctuation">;</span> <span class="token comment">// current status of the task</span>
  history<span class="token operator">?</span><span class="token operator">:</span> Message<span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span>
  artifacts<span class="token operator">?</span><span class="token operator">:</span> Artifact<span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span> <span class="token comment">// collection of artifacts created by the agent.</span>
  metadata<span class="token operator">?</span><span class="token operator">:</span> Record<span class="token operator">&lt;</span><span class="token builtin">string</span><span class="token punctuation">,</span> <span class="token builtin">any</span><span class="token operator">&gt;</span><span class="token punctuation">;</span> <span class="token comment">// extension metadata</span>
<span class="token punctuation">}</span>
<span class="token comment">// TaskState and accompanying message.</span>
<span class="token keyword">interface</span> <span class="token class-name">TaskStatus</span> <span class="token punctuation">{</span>
  state<span class="token operator">:</span> TaskState<span class="token punctuation">;</span>
  message<span class="token operator">?</span><span class="token operator">:</span> Message<span class="token punctuation">;</span> <span class="token comment">//additional status updates for client</span>
  timestamp<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span> <span class="token comment">// ISO datetime value</span>
<span class="token punctuation">}</span>
<span class="token comment">// sent by server during sendSubscribe or subscribe requests</span>
<span class="token keyword">interface</span> <span class="token class-name">TaskStatusUpdateEvent</span> <span class="token punctuation">{</span>
  id<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  status<span class="token operator">:</span> TaskStatus<span class="token punctuation">;</span>
  final<span class="token operator">:</span> <span class="token builtin">boolean</span><span class="token punctuation">;</span> <span class="token comment">//indicates the end of the event stream</span>
  metadata<span class="token operator">?</span><span class="token operator">:</span> Record<span class="token operator">&lt;</span><span class="token builtin">string</span><span class="token punctuation">,</span> <span class="token builtin">any</span><span class="token operator">&gt;</span><span class="token punctuation">;</span>
<span class="token punctuation">}</span>
<span class="token comment">// sent by server during sendSubscribe or subscribe requests</span>
<span class="token keyword">interface</span> <span class="token class-name">TaskArtifactUpdateEvent</span> <span class="token punctuation">{</span>
  id<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  artifact<span class="token operator">:</span> Artifact<span class="token punctuation">;</span>
  metadata<span class="token operator">?</span><span class="token operator">:</span> Record<span class="token operator">&lt;</span><span class="token builtin">string</span><span class="token punctuation">,</span> <span class="token builtin">any</span><span class="token operator">&gt;</span><span class="token punctuation">;</span>
<span class="token punctuation">}</span>
<span class="token comment">// Sent by the client to the agent to create, continue, or restart a task.</span>
<span class="token keyword">interface</span> <span class="token class-name">TaskSendParams</span> <span class="token punctuation">{</span>
  id<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  sessionId<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span> <span class="token comment">//server creates a new sessionId for new tasks if not set</span>
  message<span class="token operator">:</span> Message<span class="token punctuation">;</span>
  historyLength<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">number</span><span class="token punctuation">;</span> <span class="token comment">//number of recent messages to be retrieved</span>
  <span class="token comment">// where the server should send notifications when disconnected.</span>
  pushNotification<span class="token operator">?</span><span class="token operator">:</span> PushNotificationConfig<span class="token punctuation">;</span>
  metadata<span class="token operator">?</span><span class="token operator">:</span> Record<span class="token operator">&lt;</span><span class="token builtin">string</span><span class="token punctuation">,</span> <span class="token builtin">any</span><span class="token operator">&gt;</span><span class="token punctuation">;</span> <span class="token comment">// extension metadata</span>
<span class="token punctuation">}</span>
<span class="token keyword">type</span> <span class="token class-name">TaskState</span> <span class="token operator">=</span>
  <span class="token operator">|</span> <span class="token string">"submitted"</span>
  <span class="token operator">|</span> <span class="token string">"working"</span>
  <span class="token operator">|</span> <span class="token string">"input-required"</span>
  <span class="token operator">|</span> <span class="token string">"completed"</span>
  <span class="token operator">|</span> <span class="token string">"canceled"</span>
  <span class="token operator">|</span> <span class="token string">"failed"</span>
  <span class="token operator">|</span> <span class="token string">"unknown"</span><span class="token punctuation">;</span></code></pre><h3 id="artifact"><a href="#/documentation?id=artifact" data-id="artifact" class="anchor"><span>Artifact</span></a></h3><p>Agents
 generate Artifacts as an end result of a Task. Artifacts are immutable,
 can be named, and can have multiple parts. A streaming response can 
append parts to existing Artifacts.</p><p>A single Task can generate many Artifacts. For example, "create a webpage" could create separate HTML and image Artifacts.</p><pre v-pre="" data-lang="typescript"><code class="lang-typescript"><span class="token keyword">interface</span> <span class="token class-name">Artifact</span> <span class="token punctuation">{</span>
  name<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  description<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  parts<span class="token operator">:</span> Part<span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span>
  metadata<span class="token operator">?</span><span class="token operator">:</span> Record<span class="token operator">&lt;</span><span class="token builtin">string</span><span class="token punctuation">,</span> <span class="token builtin">any</span><span class="token operator">&gt;</span><span class="token punctuation">;</span>
  index<span class="token operator">:</span> <span class="token builtin">number</span><span class="token punctuation">;</span>
  append<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">boolean</span><span class="token punctuation">;</span>
  lastChunk<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">boolean</span><span class="token punctuation">;</span>
<span class="token punctuation">}</span></code></pre><h3 id="message"><a href="#/documentation?id=message" data-id="message" class="anchor"><span>Message</span></a></h3><p>A
 Message contains any content that is not an Artifact. This can include 
things like agent thoughts, user context, instructions, errors, status, 
or metadata.</p><p>All content from a client comes in the form of a 
Message. Agents send Messages to communicate status or to provide 
instructions (whereas generated results are sent as Artifacts).</p><p>A 
Message can have multiple parts to denote different pieces of content. 
For example, a user request could include a textual description from a 
user and then multiple files used as context from the client.</p><pre v-pre="" data-lang="typescript"><code class="lang-typescript"><span class="token keyword">interface</span> <span class="token class-name">Message</span> <span class="token punctuation">{</span>
  role<span class="token operator">:</span> <span class="token string">"user"</span> <span class="token operator">|</span> <span class="token string">"agent"</span><span class="token punctuation">;</span>
  parts<span class="token operator">:</span> Part<span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span>
  metadata<span class="token operator">?</span><span class="token operator">:</span> Record<span class="token operator">&lt;</span><span class="token builtin">string</span><span class="token punctuation">,</span> <span class="token builtin">any</span><span class="token operator">&gt;</span><span class="token punctuation">;</span>
<span class="token punctuation">}</span></code></pre><h3 id="part"><a href="#/documentation?id=part" data-id="part" class="anchor"><span>Part</span></a></h3><p>A
 fully formed piece of content exchanged between a client and a remote 
agent as part of a Message or an Artifact. Each Part has its own content
 type and metadata.</p><pre v-pre="" data-lang="typescript"><code class="lang-typescript"><span class="token keyword">interface</span> <span class="token class-name">TextPart</span> <span class="token punctuation">{</span>
  type<span class="token operator">:</span> <span class="token string">"text"</span><span class="token punctuation">;</span>
  text<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
<span class="token punctuation">}</span>
<span class="token keyword">interface</span> <span class="token class-name">FilePart</span> <span class="token punctuation">{</span>
  type<span class="token operator">:</span> <span class="token string">"file"</span><span class="token punctuation">;</span>
  file<span class="token operator">:</span> <span class="token punctuation">{</span>
    name<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
    mimeType<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
    <span class="token comment">// oneof {</span>
    bytes<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span> <span class="token comment">//base64 encoded content</span>
    uri<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
    <span class="token comment">//}</span>
  <span class="token punctuation">}</span><span class="token punctuation">;</span>
<span class="token punctuation">}</span>
<span class="token keyword">interface</span> <span class="token class-name">DataPart</span> <span class="token punctuation">{</span>
  type<span class="token operator">:</span> <span class="token string">"data"</span><span class="token punctuation">;</span>
  data<span class="token operator">:</span> Record<span class="token operator">&lt;</span><span class="token builtin">string</span><span class="token punctuation">,</span> <span class="token builtin">any</span><span class="token operator">&gt;</span><span class="token punctuation">;</span>
<span class="token punctuation">}</span>
<span class="token keyword">type</span> <span class="token class-name">Part</span> <span class="token operator">=</span> <span class="token punctuation">(</span>TextPart <span class="token operator">|</span> FilePart <span class="token operator">|</span> DataPart<span class="token punctuation">)</span> <span class="token operator">&amp;</span> <span class="token punctuation">{</span>
  metadata<span class="token operator">:</span> Record<span class="token operator">&lt;</span><span class="token builtin">string</span><span class="token punctuation">,</span> <span class="token builtin">any</span><span class="token operator">&gt;</span><span class="token punctuation">;</span>
<span class="token punctuation">}</span><span class="token punctuation">;</span></code></pre><h3 id="push-notifications"><a href="#/documentation?id=push-notifications" data-id="push-notifications" class="anchor"><span>Push Notifications</span></a></h3><p>A2A
 supports a secure notification mechanism whereby an agent can notify a 
client of an update outside of a connected session via a 
PushNotificationService. Within and across enterprises, it is critical 
that the agent verifies the identity of the notification service, 
authenticates itself with the service, and presents an identifier that 
ties the notification to the executing Task.</p><p>The target server of 
the PushNotificationService should be considered a separate service, and
 is not guaranteed (or even expected) to be the client directly. This 
PushNotificationService is responsible for authenticating and 
authorizing the agent and for proxying the verified notification to the 
appropriate endpoint (which could be anything from a pub/sub queue, to 
an email inbox or other service, etc).</p><p>For contrived scenarios 
with isolated client-agent pairs (e.g. local service mesh in a contained
 VPC, etc.) or isolated environments without enterprise security 
concerns, the client may choose to simply open a port and act as its own
 PushNotificationService. Any enterprise implementation will likely have
 a centralized service that authenticates the remote agents with trusted
 notification credentials and can handle online/offline scenarios. (This
 should be thought of similarly to a mobile Push Notification Service).</p><pre v-pre="" data-lang="typescript"><code class="lang-typescript"><span class="token keyword">interface</span> <span class="token class-name">PushNotificationConfig</span> <span class="token punctuation">{</span>
  url<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  token<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span> <span class="token comment">// token unique to this task/session</span>
  authentication<span class="token operator">?</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    schemes<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">[</span><span class="token punctuation">]</span><span class="token punctuation">;</span>
    credentials<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  <span class="token punctuation">}</span><span class="token punctuation">;</span>
<span class="token punctuation">}</span>
<span class="token keyword">interface</span> <span class="token class-name">TaskPushNotificationConfig</span> <span class="token punctuation">{</span>
  id<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span> <span class="token comment">//task id</span>
  pushNotificationConfig<span class="token operator">:</span> PushNotificationConfig<span class="token punctuation">;</span>
<span class="token punctuation">}</span></code></pre><h1 id="sample-methods-and-json-responses"><a href="#/documentation?id=sample-methods-and-json-responses" data-id="sample-methods-and-json-responses" class="anchor"><span>Sample Methods and JSON Responses</span></a></h1><h2 id="agent-card-1"><a href="#/documentation?id=agent-card-1" data-id="agent-card-1" class="anchor"><span>Agent Card</span></a></h2><pre v-pre="" data-lang="json"><code class="lang-json"><span class="token comment">//agent card</span>
<span class="token punctuation">{</span>
  <span class="token property">"name"</span><span class="token operator">:</span> <span class="token string">"Google Maps Agent"</span><span class="token punctuation">,</span>
  <span class="token property">"description"</span><span class="token operator">:</span> <span class="token string">"Plan routes, remember places, and generate directions"</span><span class="token punctuation">,</span>
  <span class="token property">"url"</span><span class="token operator">:</span> <span class="token string">"https://maps-agent.google.com"</span><span class="token punctuation">,</span>
  <span class="token property">"provider"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"organization"</span><span class="token operator">:</span> <span class="token string">"Google"</span><span class="token punctuation">,</span>
    <span class="token property">"url"</span><span class="token operator">:</span> <span class="token string">"https://google.com"</span>
  <span class="token punctuation">}</span><span class="token punctuation">,</span>
  <span class="token property">"version"</span><span class="token operator">:</span> <span class="token string">"1.0.0"</span><span class="token punctuation">,</span>
  <span class="token property">"authentication"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"schemes"</span><span class="token operator">:</span> <span class="token string">"OAuth2"</span>
  <span class="token punctuation">}</span><span class="token punctuation">,</span>
  <span class="token property">"defaultInputModes"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token string">"text/plain"</span><span class="token punctuation">]</span><span class="token punctuation">,</span>
  <span class="token property">"defaultOutputModes"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token string">"text/plain"</span><span class="token punctuation">,</span> <span class="token string">"application/html"</span><span class="token punctuation">]</span><span class="token punctuation">,</span>
  <span class="token property">"capabilities"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"streaming"</span><span class="token operator">:</span> <span class="token boolean">true</span><span class="token punctuation">,</span>
    <span class="token property">"pushNotifications"</span><span class="token operator">:</span> <span class="token boolean">false</span>
  <span class="token punctuation">}</span><span class="token punctuation">,</span>
  <span class="token property">"skills"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
    <span class="token punctuation">{</span>
      <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"route-planner"</span><span class="token punctuation">,</span>
      <span class="token property">"name"</span><span class="token operator">:</span> <span class="token string">"Route planning"</span><span class="token punctuation">,</span>
      <span class="token property">"description"</span><span class="token operator">:</span> <span class="token string">"Helps plan routing between two locations"</span><span class="token punctuation">,</span>
      <span class="token property">"tags"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token string">"maps"</span><span class="token punctuation">,</span> <span class="token string">"routing"</span><span class="token punctuation">,</span> <span class="token string">"navigation"</span><span class="token punctuation">]</span><span class="token punctuation">,</span>
      <span class="token property">"examples"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
        <span class="token string">"plan my route from Sunnyvale to Mountain View"</span><span class="token punctuation">,</span>
        <span class="token string">"what's the commute time from Sunnyvale to San Francisco at 9AM"</span><span class="token punctuation">,</span>
        <span class="token string">"create turn by turn directions from Sunnyvale to Mountain View"</span>
      <span class="token punctuation">]</span><span class="token punctuation">,</span>
      <span class="token comment">// can return a video of the route</span>
      <span class="token property">"outputModes"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token string">"application/html"</span><span class="token punctuation">,</span> <span class="token string">"video/mp4"</span><span class="token punctuation">]</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token punctuation">{</span>
      <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"custom-map"</span><span class="token punctuation">,</span>
      <span class="token property">"name"</span><span class="token operator">:</span> <span class="token string">"My Map"</span><span class="token punctuation">,</span>
      <span class="token property">"description"</span><span class="token operator">:</span> <span class="token string">"Manage a custom map with your own saved places"</span><span class="token punctuation">,</span>
      <span class="token property">"tags"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token string">"custom-map"</span><span class="token punctuation">,</span> <span class="token string">"saved-places"</span><span class="token punctuation">]</span><span class="token punctuation">,</span>
      <span class="token property">"examples"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
        <span class="token string">"show me my favorite restaurants on the map"</span><span class="token punctuation">,</span>
        <span class="token string">"create a visual of all places I've visited in the past year"</span>
      <span class="token punctuation">]</span><span class="token punctuation">,</span>
      <span class="token property">"outputModes"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token string">"application/html"</span><span class="token punctuation">]</span>
    <span class="token punctuation">}</span>
  <span class="token punctuation">]</span>
<span class="token punctuation">}</span></code></pre><h2 id="send-a-task"><a href="#/documentation?id=send-a-task" data-id="send-a-task" class="anchor"><span>Send a Task</span></a></h2><p>Allows
 a client to send content to a remote agent to start a new Task, resume 
an interrupted Task or reopen a completed Task. A Task interrupt may be 
caused due to an agent requiring additional user input or a runtime 
error.</p><pre v-pre="" data-lang="json"><code class="lang-json"><span class="token comment">//Request</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/send"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"message"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"role"</span><span class="token operator">:</span><span class="token string">"user"</span><span class="token punctuation">,</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
        <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
        <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"tell me a joke"</span>
      <span class="token punctuation">}</span><span class="token punctuation">]</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Response</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"status"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"state"</span><span class="token operator">:</span> <span class="token string">"completed"</span><span class="token punctuation">,</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"artifacts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
      <span class="token property">"name"</span><span class="token operator">:</span><span class="token string">"joke"</span><span class="token punctuation">,</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
          <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
          <span class="token property">"text"</span><span class="token operator">:</span><span class="token string">"Why did the chicken cross the road? To get to the other side!"</span>
        <span class="token punctuation">}</span><span class="token punctuation">]</span>
      <span class="token punctuation">}</span><span class="token punctuation">]</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span></code></pre><h2 id="get-a-task"><a href="#/documentation?id=get-a-task" data-id="get-a-task" class="anchor"><span>Get a Task</span></a></h2><p>Clients
 may use this method to retrieve the generated Artifacts for a Task. The
 agent determines the retention window for Tasks previously submitted to
 it. An agent may return an error code for Tasks that were past the 
retention window for an agent or for Tasks that are short-lived and not 
persisted by the agent.</p><p>The client may also request the last N 
items of history of the Task which will include all Messages, in order, 
sent by client and server. By default this is 0 (no history).</p><pre v-pre="" data-lang="json"><code class="lang-json"><span class="token comment">//Request</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/get"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"historyLength"</span><span class="token operator">:</span> <span class="token number">10</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Response</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"status"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"state"</span><span class="token operator">:</span> <span class="token string">"completed"</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"artifacts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
        <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
        <span class="token property">"text"</span><span class="token operator">:</span><span class="token string">"Why did the chicken cross the road? To get to the other side!"</span>
      <span class="token punctuation">}</span><span class="token punctuation">]</span>
    <span class="token punctuation">}</span><span class="token punctuation">]</span><span class="token punctuation">,</span>
    <span class="token property">"history"</span><span class="token operator">:</span><span class="token punctuation">[</span>
      <span class="token punctuation">{</span>
        <span class="token property">"role"</span><span class="token operator">:</span> <span class="token string">"user"</span><span class="token punctuation">,</span>
        <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
          <span class="token punctuation">{</span>
            <span class="token property">"type"</span><span class="token operator">:</span> <span class="token string">"text"</span><span class="token punctuation">,</span>
            <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"tell me a joke"</span>
          <span class="token punctuation">}</span>
        <span class="token punctuation">]</span>
      <span class="token punctuation">}</span>
    <span class="token punctuation">]</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span></code></pre><h2 id="cancel-a-task"><a href="#/documentation?id=cancel-a-task" data-id="cancel-a-task" class="anchor"><span>Cancel a Task</span></a></h2><p>A client may choose to cancel previously submitted Tasks as shown below.</p><pre v-pre="" data-lang="json"><code class="lang-json"><span class="token comment">//Request</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/cancel"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Response</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"status"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"state"</span><span class="token operator">:</span> <span class="token string">"canceled"</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span></code></pre><h2 id="set-task-push-notification-config"><a href="#/documentation?id=set-task-push-notification-config" data-id="set-task-push-notification-config" class="anchor"><span>Set Task Push Notification Config</span></a></h2><p>Clients may configure a push notification URL for receiving an update on Task status change.</p><pre v-pre="" data-lang="json"><code class="lang-json"><span class="token comment">//Request</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/pushNotification/set"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"pushNotificationConfig"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"url"</span><span class="token operator">:</span> <span class="token string">"https://example.com/callback"</span><span class="token punctuation">,</span>
      <span class="token property">"authentication"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
        <span class="token property">"schemes"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token string">"jwt"</span><span class="token punctuation">]</span>
      <span class="token punctuation">}</span>
    <span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Response</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"pushNotificationConfig"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"url"</span><span class="token operator">:</span> <span class="token string">"https://example.com/callback"</span><span class="token punctuation">,</span>
      <span class="token property">"authentication"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
        <span class="token property">"schemes"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token string">"jwt"</span><span class="token punctuation">]</span>
      <span class="token punctuation">}</span>
    <span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span></code></pre><h2 id="get-task-push-notification-config"><a href="#/documentation?id=get-task-push-notification-config" data-id="get-task-push-notification-config" class="anchor"><span>Get Task Push Notification Config</span></a></h2><p>Clients may retrieve the currently configured push notification configuration for a Task using this method.</p><pre v-pre="" data-lang="json"><code class="lang-json"><span class="token comment">//Request</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/pushNotification/get"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Response</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"pushNotificationConfig"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"url"</span><span class="token operator">:</span> <span class="token string">"https://example.com/callback"</span><span class="token punctuation">,</span>
      <span class="token property">"authentication"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
        <span class="token property">"schemes"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token string">"jwt"</span><span class="token punctuation">]</span>
      <span class="token punctuation">}</span>
    <span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span></code></pre><h2 id="multi-turn-conversations"><a href="#/documentation?id=multi-turn-conversations" data-id="multi-turn-conversations" class="anchor"><span>Multi-turn Conversations</span></a></h2><p>A Task may pause to be executed on the remote agent if it requires additional user input. When a Task is in <code>input-required</code> state, the client is required to provide additional input for the Task to resume processing on the remote agent.</p><p>The Message included in the <code>input-required</code>
 state must include the details indicating what the client must do. For 
example "fill out a form" or "log into SaaS service foo". If this 
includes structured data, the instruction should be sent as one <code>Part</code> and the structured data as a second <code>Part</code>.</p><pre v-pre="" data-lang="json"><code class="lang-json"><span class="token comment">//Request - seq 1</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/send"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"message"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"role"</span><span class="token operator">:</span><span class="token string">"user"</span><span class="token punctuation">,</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
        <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
        <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"request a new phone for me"</span>
      <span class="token punctuation">}</span><span class="token punctuation">]</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Response - seq 2</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"status"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"state"</span><span class="token operator">:</span> <span class="token string">"input-required"</span><span class="token punctuation">,</span>
      <span class="token property">"message"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
        <span class="token property">"role"</span><span class="token operator">:</span><span class="token string">"agent"</span><span class="token punctuation">,</span>
        <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
          <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
          <span class="token property">"text"</span><span class="token operator">:</span><span class="token string">"Select a phone type (iPhone/Android)"</span>
        <span class="token punctuation">}</span><span class="token punctuation">]</span>
      <span class="token punctuation">}</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Request - seq 3</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">2</span><span class="token punctuation">,</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/send"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"message"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"role"</span><span class="token operator">:</span><span class="token string">"user"</span><span class="token punctuation">,</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
        <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
        <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"Android"</span>
      <span class="token punctuation">}</span><span class="token punctuation">]</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Response - seq 4</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">2</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"status"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"state"</span><span class="token operator">:</span> <span class="token string">"completed"</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"artifacts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
      <span class="token property">"name"</span><span class="token operator">:</span> <span class="token string">"order-confirmation"</span><span class="token punctuation">,</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
          <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
          <span class="token property">"text"</span><span class="token operator">:</span><span class="token string">"I have ordered a new Android device for you. Your request number is R12443"</span>
        <span class="token punctuation">}</span><span class="token punctuation">]</span><span class="token punctuation">,</span>
      <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
    <span class="token punctuation">}</span><span class="token punctuation">]</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span></code></pre><h2 id="streaming-support"><a href="#/documentation?id=streaming-support" data-id="streaming-support" class="anchor"><span>Streaming Support</span></a></h2><p>For clients and remote agents capable of communicating over HTTP with SSE, clients can send the RPC request with method <code>tasks/sendSubscribe</code>
 when creating a new Task. The remote agent can respond with a stream of
 TaskStatusUpdateEvents (to communicate status changes or 
instructions/requests) and TaskArtifactUpdateEvents (to stream generated
 results).
Note that TaskArtifactUpdateEvents can append new parts to existing 
Artifacts. Clients
can use <code>task/get</code> to retrieve the entire Artifact outside of the streaming.
Agents must set final: true attribute at the end of the stream or if the agent is interrupted and require additional user input.</p><pre v-pre="" data-lang="json"><code class="lang-json"><span class="token comment">//Request</span>
<span class="token punctuation">{</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/sendSubscribe"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"message"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"role"</span><span class="token operator">:</span><span class="token string">"user"</span><span class="token punctuation">,</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
        <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
        <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"write a long paper describing the attached pictures"</span>
      <span class="token punctuation">}</span><span class="token punctuation">,</span><span class="token punctuation">{</span>
        <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"file"</span><span class="token punctuation">,</span>
        <span class="token property">"file"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
           <span class="token property">"mimeType"</span><span class="token operator">:</span> <span class="token string">"image/png"</span><span class="token punctuation">,</span>
           <span class="token property">"data"</span><span class="token operator">:</span><span class="token string">"&lt;base64-encoded-content&gt;"</span>
        <span class="token punctuation">}</span>
      <span class="token punctuation">}</span><span class="token punctuation">]</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>

<span class="token comment">//Response</span>
data<span class="token operator">:</span> <span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
    <span class="token property">"status"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"state"</span><span class="token operator">:</span> <span class="token string">"working"</span><span class="token punctuation">,</span>
      <span class="token property">"timestamp"</span><span class="token operator">:</span><span class="token string">"2025-04-02T16:59:25.331844"</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"final"</span><span class="token operator">:</span> <span class="token boolean">false</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>

data<span class="token operator">:</span> <span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>    
    <span class="token property">"artifact"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
        <span class="token punctuation">{</span><span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span> <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"&lt;section 1...&gt;"</span><span class="token punctuation">}</span>
      <span class="token punctuation">]</span><span class="token punctuation">,</span>
      <span class="token property">"index"</span><span class="token operator">:</span> <span class="token number">0</span><span class="token punctuation">,</span>
      <span class="token property">"append"</span><span class="token operator">:</span> <span class="token boolean">false</span><span class="token punctuation">,</span>      
      <span class="token property">"lastChunk"</span><span class="token operator">:</span> <span class="token boolean">false</span>
    <span class="token punctuation">]</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
data<span class="token operator">:</span> <span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>  
    <span class="token property">"artifact"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
        <span class="token punctuation">{</span><span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span> <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"&lt;section 2...&gt;"</span><span class="token punctuation">}</span>
      <span class="token punctuation">]</span><span class="token punctuation">,</span>
      <span class="token property">"index"</span><span class="token operator">:</span> <span class="token number">0</span><span class="token punctuation">,</span>
      <span class="token property">"append"</span><span class="token operator">:</span> <span class="token boolean">true</span><span class="token punctuation">,</span>      
      <span class="token property">"lastChunk"</span><span class="token operator">:</span> <span class="token boolean">false</span>
    <span class="token punctuation">]</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
data<span class="token operator">:</span> <span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>    
    <span class="token property">"artifact"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
        <span class="token punctuation">{</span><span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span> <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"&lt;section 3...&gt;"</span><span class="token punctuation">}</span>
      <span class="token punctuation">]</span><span class="token punctuation">,</span>
      <span class="token property">"index"</span><span class="token operator">:</span> <span class="token number">0</span><span class="token punctuation">,</span>
      <span class="token property">"append"</span><span class="token operator">:</span> <span class="token boolean">true</span><span class="token punctuation">,</span>
      <span class="token property">"lastChunk"</span><span class="token operator">:</span> <span class="token boolean">true</span>
    <span class="token punctuation">]</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>

data<span class="token operator">:</span> <span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
    <span class="token property">"status"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"state"</span><span class="token operator">:</span> <span class="token string">"completed"</span><span class="token punctuation">,</span>
      <span class="token property">"timestamp"</span><span class="token operator">:</span><span class="token string">"2025-04-02T16:59:35.331844"</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"final"</span><span class="token operator">:</span> <span class="token boolean">true</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span></code></pre><h3 id="resubscribe-to-task"><a href="#/documentation?id=resubscribe-to-task" data-id="resubscribe-to-task" class="anchor"><span>Resubscribe to Task</span></a></h3><p>A disconnected client may resubscribe to a remote agent that supports streaming to receive Task updates via SSE.</p><pre v-pre="" data-lang="json"><code class="lang-json"><span class="token comment">//Request</span>
<span class="token punctuation">{</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/resubscribe"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Response</span>
data<span class="token operator">:</span> <span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"artifact"</span><span class="token operator">:</span><span class="token punctuation">[</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
        <span class="token punctuation">{</span><span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span> <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"&lt;section 2...&gt;"</span><span class="token punctuation">}</span>
      <span class="token punctuation">]</span><span class="token punctuation">,</span>
      <span class="token property">"index"</span><span class="token operator">:</span> <span class="token number">0</span><span class="token punctuation">,</span>
      <span class="token property">"append"</span><span class="token operator">:</span> <span class="token boolean">true</span><span class="token punctuation">,</span>
      <span class="token property">"lastChunk"</span><span class="token operator">:</span><span class="token boolean">false</span>
    <span class="token punctuation">]</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
data<span class="token operator">:</span> <span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"artifact"</span><span class="token operator">:</span><span class="token punctuation">[</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
        <span class="token punctuation">{</span><span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span> <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"&lt;section 3...&gt;"</span><span class="token punctuation">}</span>
      <span class="token punctuation">]</span><span class="token punctuation">,</span>
      <span class="token property">"index"</span><span class="token operator">:</span> <span class="token number">0</span><span class="token punctuation">,</span>
      <span class="token property">"append"</span><span class="token operator">:</span> <span class="token boolean">true</span><span class="token punctuation">,</span>
      <span class="token property">"lastChunk"</span><span class="token operator">:</span> <span class="token boolean">true</span>
    <span class="token punctuation">]</span>   
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>

data<span class="token operator">:</span> <span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">1</span><span class="token punctuation">,</span>
    <span class="token property">"status"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"state"</span><span class="token operator">:</span> <span class="token string">"completed"</span><span class="token punctuation">,</span>
      <span class="token property">"timestamp"</span><span class="token operator">:</span><span class="token string">"2025-04-02T16:59:35.331844"</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"final"</span><span class="token operator">:</span> <span class="token boolean">true</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span></code></pre><h2 id="non-textual-media"><a href="#/documentation?id=non-textual-media" data-id="non-textual-media" class="anchor"><span>Non-textual Media</span></a></h2><p>Following is an example interaction between a client and an agent with non-textual data.</p><pre v-pre="" data-lang="json"><code class="lang-json"><span class="token comment">//Request - seq 1</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">9</span><span class="token punctuation">,</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/send"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"message"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"role"</span><span class="token operator">:</span><span class="token string">"user"</span><span class="token punctuation">,</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
        <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
        <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"Analyze the attached report and generate high level overview"</span>
      <span class="token punctuation">}</span><span class="token punctuation">,</span><span class="token punctuation">{</span>
        <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"file"</span><span class="token punctuation">,</span>
        <span class="token property">"file"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
           <span class="token property">"mimeType"</span><span class="token operator">:</span> <span class="token string">"application/pdf"</span><span class="token punctuation">,</span>
           <span class="token property">"data"</span><span class="token operator">:</span><span class="token string">"&lt;base64-encoded-content&gt;"</span>
        <span class="token punctuation">}</span>
      <span class="token punctuation">}</span><span class="token punctuation">]</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Response - seq 2</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">9</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"status"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"state"</span><span class="token operator">:</span> <span class="token string">"working"</span><span class="token punctuation">,</span>
      <span class="token property">"message"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
        <span class="token property">"role"</span><span class="token operator">:</span> <span class="token string">"agent"</span><span class="token punctuation">,</span>
        <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
          <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
          <span class="token property">"text"</span><span class="token operator">:</span><span class="token string">"analysis in progress, please wait"</span>
        <span class="token punctuation">}</span><span class="token punctuation">]</span><span class="token punctuation">,</span>
        <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
       <span class="token punctuation">}</span>
     <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Request - seq 3</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">10</span><span class="token punctuation">,</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/get"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Response - seq 4</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">9</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"status"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"state"</span><span class="token operator">:</span> <span class="token string">"completed"</span>
     <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"artifacts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
        <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
        <span class="token property">"text"</span><span class="token operator">:</span><span class="token string">"&lt;generated analysis content&gt;"</span>
       <span class="token punctuation">}</span><span class="token punctuation">]</span><span class="token punctuation">,</span>
       <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
     <span class="token punctuation">}</span><span class="token punctuation">]</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span></code></pre><h2 id="structured-output"><a href="#/documentation?id=structured-output" data-id="structured-output" class="anchor"><span>Structured output</span></a></h2><p>Both the client or the agent can request structured output from the other party.</p><pre v-pre="" data-lang="json"><code class="lang-json"><span class="token comment">//Request</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">9</span><span class="token punctuation">,</span>
  <span class="token property">"method"</span><span class="token operator">:</span><span class="token string">"tasks/send"</span><span class="token punctuation">,</span>
  <span class="token property">"params"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"message"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"role"</span><span class="token operator">:</span><span class="token string">"user"</span><span class="token punctuation">,</span>
      <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span><span class="token punctuation">{</span>
        <span class="token property">"type"</span><span class="token operator">:</span><span class="token string">"text"</span><span class="token punctuation">,</span>
        <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"Show me a list of my open IT tickets"</span><span class="token punctuation">,</span>
        <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
          <span class="token property">"mimeType"</span><span class="token operator">:</span> <span class="token string">"application/json"</span><span class="token punctuation">,</span>
          <span class="token property">"schema"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
            <span class="token property">"type"</span><span class="token operator">:</span> <span class="token string">"array"</span><span class="token punctuation">,</span>
            <span class="token property">"items"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
              <span class="token property">"type"</span><span class="token operator">:</span> <span class="token string">"object"</span><span class="token punctuation">,</span>
              <span class="token property">"properties"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
                <span class="token property">"ticketNumber"</span><span class="token operator">:</span> <span class="token punctuation">{</span> <span class="token property">"type"</span><span class="token operator">:</span> <span class="token string">"string"</span> <span class="token punctuation">}</span><span class="token punctuation">,</span>
                <span class="token property">"description"</span><span class="token operator">:</span> <span class="token punctuation">{</span> <span class="token property">"type"</span><span class="token operator">:</span> <span class="token string">"string"</span> <span class="token punctuation">}</span>
              <span class="token punctuation">}</span>
            <span class="token punctuation">}</span>
          <span class="token punctuation">}</span>
        <span class="token punctuation">}</span>
      <span class="token punctuation">}</span><span class="token punctuation">]</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"metadata"</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span>
<span class="token comment">//Response</span>
<span class="token punctuation">{</span>
  <span class="token property">"jsonrpc"</span><span class="token operator">:</span> <span class="token string">"2.0"</span><span class="token punctuation">,</span>
  <span class="token property">"id"</span><span class="token operator">:</span> <span class="token number">9</span><span class="token punctuation">,</span>
  <span class="token property">"result"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
    <span class="token property">"id"</span><span class="token operator">:</span> <span class="token string">"de38c76d-d54c-436c-8b9f-4c2703648d64"</span><span class="token punctuation">,</span>
    <span class="token property">"sessionId"</span><span class="token operator">:</span> <span class="token string">"c295ea44-7543-4f78-b524-7a38915ad6e4"</span><span class="token punctuation">,</span>
    <span class="token property">"status"</span><span class="token operator">:</span> <span class="token punctuation">{</span>
      <span class="token property">"state"</span><span class="token operator">:</span> <span class="token string">"completed"</span><span class="token punctuation">,</span>
      <span class="token property">"timestamp"</span><span class="token operator">:</span> <span class="token string">"2025-04-17T17:47:09.680794"</span>
    <span class="token punctuation">}</span><span class="token punctuation">,</span>
    <span class="token property">"artifacts"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
      <span class="token punctuation">{</span>
        <span class="token property">"parts"</span><span class="token operator">:</span> <span class="token punctuation">[</span>
          <span class="token punctuation">{</span>
            <span class="token property">"type"</span><span class="token operator">:</span> <span class="token string">"text"</span><span class="token punctuation">,</span>
            <span class="token property">"text"</span><span class="token operator">:</span> <span class="token string">"[{\"ticketNumber\":\"REQ12312\",\"description\":\"request for VPN access\"},{\"ticketNumber\":\"REQ23422\",\"description\":\"Add to DL - team-gcp-onboarding\"}]"</span>
          <span class="token punctuation">}</span>
        <span class="token punctuation">]</span><span class="token punctuation">,</span>
        <span class="token property">"index"</span><span class="token operator">:</span> <span class="token number">0</span>
      <span class="token punctuation">}</span>
    <span class="token punctuation">]</span>
  <span class="token punctuation">}</span>
<span class="token punctuation">}</span></code></pre><h2 id="error-handling"><a href="#/documentation?id=error-handling" data-id="error-handling" class="anchor"><span>Error Handling</span></a></h2><p>Following
 is the ErrorMessage format for the server to respond to the client when
 it encounters an error processing the client request.</p><pre v-pre="" data-lang="typescript"><code class="lang-typescript"><span class="token keyword">interface</span> <span class="token class-name">ErrorMessage</span> <span class="token punctuation">{</span>
  code<span class="token operator">:</span> <span class="token builtin">number</span><span class="token punctuation">;</span>
  message<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span>
  data<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">any</span><span class="token punctuation">;</span>
<span class="token punctuation">}</span></code></pre><p>The following are the standard JSON-RPC error codes that the server can respond with for error scenarios:</p><table>
<thead>
<tr>
<th align="left">Error Code</th>
<th align="left">Message</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody><tr>
<td align="left">-32700</td>
<td align="left">JSON parse error</td>
<td align="left">Invalid JSON was sent</td>
</tr>
<tr>
<td align="left">-32600</td>
<td align="left">Invalid Request</td>
<td align="left">Request payload validation error</td>
</tr>
<tr>
<td align="left">-32601</td>
<td align="left">Method not found</td>
<td align="left">Not a valid method</td>
</tr>
<tr>
<td align="left">-32602</td>
<td align="left">Invalid params</td>
<td align="left">Invalid method parameters</td>
</tr>
<tr>
<td align="left">-32603</td>
<td align="left">Internal error</td>
<td align="left">Internal JSON-RPC error</td>
</tr>
<tr>
<td align="left">-32000 to -32099</td>
<td align="left">Server error</td>
<td align="left">Reserved for implementation specific error codes</td>
</tr>
<tr>
<td align="left">-32001</td>
<td align="left">Task not found</td>
<td align="left">Task not found with the provided id</td>
</tr>
<tr>
<td align="left">-32002</td>
<td align="left">Task cannot be canceled</td>
<td align="left">Task cannot be canceled by the remote agent</td>
</tr>
<tr>
<td align="left">-32003</td>
<td align="left">Push notifications not supported</td>
<td align="left">Push Notification is not supported by the agent</td>
</tr>
<tr>
<td align="left">-32004</td>
<td align="left">Unsupported operation</td>
<td align="left">Operation is not supported</td>
</tr>
<tr>
<td align="left">-32005</td>
<td align="left">Incompatible content types</td>
<td align="left">Incompatible content types between client and an agent</td>
</tr>
</tbody></table>
</article></section></main>
  <script>
    window.$docsify = {
      loadSidebar: true,
      loadNavbar: true,  
      logo: '/images/a2a_logo.png',
      nameLink: "/docs/slug",
      name: '',
      repo: '',
      subMaxLevel: 2,
    }
  </script>
  <!-- Docsify v4 -->
  <script src="a2aDocumentation_files/docsify@4"></script>
  <script src="a2aDocumentation_files/search.min.js"></script>
  <script src="a2aDocumentation_files/prism-bash.min.js"></script>
  <script src="a2aDocumentation_files/prism-python.min.js"></script>
  <script src="a2aDocumentation_files/prism-typescript.min.js"></script>
  <script src="a2aDocumentation_files/prism-json.min.js"></script>


<div class="progress" style="opacity: 0; width: 0%;"></div></body></html>