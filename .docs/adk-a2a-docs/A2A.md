TITLE: Implementing A2A Server with Task Handler in TypeScript
DESCRIPTION: Demonstrates the setup of an A2A server with a custom task handler implementation. Shows how to handle task lifecycle, yield updates, manage cancellation, and produce artifacts. Uses async generator pattern for progressive task updates.
SOURCE: https://github.com/google/a2a/blob/main/samples/js/src/server/README.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
import {
  A2AServer,
  InMemoryTaskStore,
  TaskContext,
  TaskYieldUpdate,
} from "./index"; // Assuming imports from the server package

// 1. Define your agent's logic as a TaskHandler
async function* myAgentLogic(
  context: TaskContext
): AsyncGenerator<TaskYieldUpdate> {
  console.log(`Handling task: ${context.task.id}`);
  yield {
    state: "working",
    message: { role: "agent", parts: [{ text: "Processing..." }] },
  };

  // Simulate work...
  await new Promise((resolve) => setTimeout(resolve, 1000));

  if (context.isCancelled()) {
    console.log("Task cancelled!");
    yield { state: "canceled" };
    return;
  }

  // Yield an artifact
  yield {
    name: "result.txt",
    mimeType: "text/plain",
    parts: [{ text: `Task ${context.task.id} completed.` }],
  };

  // Yield final status
  yield {
    state: "completed",
    message: { role: "agent", parts: [{ text: "Done!" }] },
  };
}

// 2. Create and start the server
const store = new InMemoryTaskStore(); // Or new FileStore()
const server = new A2AServer(myAgentLogic, { taskStore: store });

server.start(); // Starts listening on default port 41241

console.log("A2A Server started.");
```

----------------------------------------

TITLE: Streaming Implementation with A2A Client in TypeScript
DESCRIPTION: Shows how to implement streaming task updates using A2AClient. The example demonstrates subscribing to task events, handling different event types (status updates and artifact updates), and properly processing the streaming response until the server signals completion.
SOURCE: https://github.com/google/a2a/blob/main/samples/js/src/client/README.md#2025-04-21_snippet_1

LANGUAGE: typescript
CODE:
```
import {
  A2AClient,
  TaskStatusUpdateEvent,
  TaskArtifactUpdateEvent,
  TaskSendParams, // Use params type directly
} from "./client"; // Adjust path if necessary
import { v4 as uuidv4 } from "uuid";

const client = new A2AClient("http://localhost:41241");

async function streamTask() {
  const streamingTaskId = uuidv4();
  try {
    console.log(`\n--- Starting streaming task ${streamingTaskId} ---`);
    // Construct just the params
    const streamParams: TaskSendParams = {
      id: streamingTaskId,
      message: { role: "user", parts: [{ text: "Stream me some updates!", type: "text" }] },
    };
    // Pass only params to the client method
    const stream = client.sendTaskSubscribe(streamParams);

    // Stream now yields the event payloads directly
    for await (const event of stream) {
      // Type guard to differentiate events based on structure
      if ("status" in event) {
        // It's a TaskStatusUpdateEvent
        const statusEvent = event as TaskStatusUpdateEvent; // Cast for clarity
        console.log(
          `[${streamingTaskId}] Status Update: ${statusEvent.status.state} - ${
            statusEvent.status.message?.parts[0]?.text ?? "No message"
          }`
        );
        if (statusEvent.final) {
          console.log(`[${streamingTaskId}] Stream marked as final.`);
          break; // Exit loop when server signals completion
        }
      } else if ("artifact" in event) {
        // It's a TaskArtifactUpdateEvent
        const artifactEvent = event as TaskArtifactUpdateEvent; // Cast for clarity
        console.log(
          `[${streamingTaskId}] Artifact Update: ${
            artifactEvent.artifact.name ??
            `Index ${artifactEvent.artifact.index}`
          } - Part Count: ${artifactEvent.artifact.parts.length}`
        );
        // Process artifact content (e.g., artifactEvent.artifact.parts[0].text)
      } else {
        console.warn("Received unknown event structure:", event);
      }
    }
    console.log(`--- Streaming task ${streamingTaskId} finished ---`);
  } catch (error) {
    console.error(`Error during streaming task ${streamingTaskId}:`, error);
  }
}

streamTask();
```

----------------------------------------

TITLE: Basic A2A Client Usage in TypeScript
DESCRIPTION: Demonstrates how to initialize the A2AClient and use it to send and retrieve tasks. The example shows importing necessary types, creating a client instance, sending a task with a simple text message, and querying task status using the client's methods.
SOURCE: https://github.com/google/a2a/blob/main/samples/js/src/client/README.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
import { A2AClient, Task, TaskQueryParams, TaskSendParams } from "./client"; // Import necessary types
import { v4 as uuidv4 } from "uuid"; // Example for generating task IDs

const client = new A2AClient("http://localhost:41241"); // Replace with your server URL

async function run() {
  try {
    // Send a simple task (pass only params)
    const taskId = uuidv4();
    const sendParams: TaskSendParams = {
      id: taskId,
      message: { role: "user", parts: [{ text: "Hello, agent!", type: "text" }] },
    };
    // Method now returns Task | null directly
    const taskResult: Task | null = await client.sendTask(sendParams);
    console.log("Send Task Result:", taskResult);

    // Get task status (pass only params)
    const getParams: TaskQueryParams = { id: taskId };
    // Method now returns Task | null directly
    const getTaskResult: Task | null = await client.getTask(getParams);
    console.log("Get Task Result:", getTaskResult);
  } catch (error) {
    console.error("A2A Client Error:", error);
  }
}

run();
```

----------------------------------------

TITLE: Multi-turn A2A API Conversation
DESCRIPTION: Demonstration of a multi-turn conversation using the A2A Protocol, showing how to maintain context across multiple requests using a session ID. Includes file analysis and follow-up questions.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/llama_index_file_chat/README.md#2025-04-21_snippet_5

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "tasks/send",
  "params": {
    "id": "130",
    "sessionId": "8f01f3d172cd4396a0e535ae8aec6687",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "What about thing X?"
        }
      ]
    }
  }
}
```

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 11,
  "result": {
    "id": "130",
    "status": {
      "state": "completed",
      "timestamp": "2025-04-02T16:53:29.301828"
    },
    "artifacts": [
      {
        "parts": [
          {
            "type": "text",
            "text": "Thing X is ... [1]"
          }
        ],
        "metadata": {
            "1": ["Text for citation 1"]
        }
        "index": 0,
      }
    ],
  }
}
```

----------------------------------------

TITLE: Streaming A2A API Response
DESCRIPTION: Example of streaming response handling in the A2A Protocol, showing progressive updates during document processing and analysis. Demonstrates the event-based streaming format with status updates.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/llama_index_file_chat/README.md#2025-04-21_snippet_6

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "tasks/send",
  "params": {
    "id": "129",
    "sessionId": "8f01f3d172cd4396a0e535ae8aec6687",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "What does this file talk about?"
        },
        {
            "type": "file",
            "file": {
                "bytes": "...",
                "name": "attention.pdf"
            }
        }
      ]
    }
  }
}
```

LANGUAGE: json
CODE:
```
stream event => {"jsonrpc":"2.0","id":"367d0ba9af97457890261ac29a0f6f5b","result":{"id":"373b26d64c5a4f0099fa906c6b7342d9","status":{"state":"working","message":{"role":"agent","parts":[{"type":"text","text":"Parsing document..."}]},"timestamp":"2025-04-15T16:05:18.283682"},"final":false}}

stream event => {"jsonrpc":"2.0","id":"367d0ba9af97457890261ac29a0f6f5b","result":{"id":"373b26d64c5a4f0099fa906c6b7342d9","status":{"state":"working","message":{"role":"agent","parts":[{"type":"text","text":"Document parsed successfully."}]},"timestamp":"2025-04-15T16:05:24.200133"},"final":false}}

stream event => {"jsonrpc":"2.0","id":"367d0ba9af97457890261ac29a0f6f5b","result":{"id":"373b26d64c5a4f0099fa906c6b7342d9","status":{"state":"working","message":{"role":"agent","parts":[{"type":"text","text":"Chatting with 1 initial messages."}]},"timestamp":"2025-04-15T16:05:24.204757"},"final":false}}
```

----------------------------------------

TITLE: Synchronous A2A API Request and Response
DESCRIPTION: Example of a basic synchronous request to analyze a PDF file and its corresponding response. The request includes session management and file handling parameters, while the response contains the analysis result with citations.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/llama_index_file_chat/README.md#2025-04-21_snippet_4

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "tasks/send",
  "params": {
    "id": "129",
    "sessionId": "8f01f3d172cd4396a0e535ae8aec6687",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "What does this file talk about?"
        },
        {
            "type": "file",
            "file": {
                "bytes": "...",
                "name": "attention.pdf"
            }
        }
      ]
    }
  }
}
```

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 11,
  "result": {
    "id": "129",
    "status": {
      "state": "completed",
      "timestamp": "2025-04-02T16:53:29.301828"
    },
    "artifacts": [
      {
        "parts": [
          {
            "type": "text",
            "text": "This file is about XYZ... [1]"
          }
        ],
        "metadata": {
            "1": ["Text for citation 1"]
        }
        "index": 0,
      }
    ],
  }
}
```

----------------------------------------

TITLE: A2A Streaming Request and Response for Currency Exchange
DESCRIPTION: Example of using the tasks/sendSubscribe method to enable streaming responses, showing real-time status updates during processing and the final result with incremental updates.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/langgraph/README.md#2025-04-21_snippet_4

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 12,
  "method": "tasks/sendSubscribe",
  "params": {
    "id": "131",
    "sessionId": "cebd704d0ddd4e8aa646aeb123d60614",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "How much is 100 USD in GBP?"
        }
      ]
    }
  }
}
```

LANGUAGE: json
CODE:
```
data: {"jsonrpc":"2.0","id":12,"result":{"id":"131","status":{"state":"working","message":{"role":"agent","parts":[{"type":"text","text":"Looking up the exchange rates..."}]},"timestamp":"2025-04-02T16:59:34.578939"},"final":false}}

data: {"jsonrpc":"2.0","id":12,"result":{"id":"131","status":{"state":"working","message":{"role":"agent","parts":[{"type":"text","text":"Processing the exchange rates.."}]},"timestamp":"2025-04-02T16:59:34.737052"},"final":false}}

data: {"jsonrpc":"2.0","id":12,"result":{"id":"131","artifact":{"parts":[{"type":"text","text":"Based on the current exchange rate, 1 USD is equivalent to 0.77252 GBP. Therefore, 100 USD would be approximately 77.252 GBP."}],"index":0,"append":false}}}

data: {"jsonrpc":"2.0","id":12,"result":{"id":"131","status":{"state":"completed","timestamp":"2025-04-02T16:59:35.331844"},"final":true}}
```

----------------------------------------

TITLE: A2A Multi-turn Conversation for Currency Exchange
DESCRIPTION: A sequence of JSON requests and responses demonstrating a multi-turn conversation where the agent requests additional information (target currency) before providing the exchange rate.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/langgraph/README.md#2025-04-21_snippet_3

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tasks/send",
  "params": {
    "id": "130",
    "sessionId": "a9bb617f2cd94bd585da0f88ce2ddba2",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "How much is the exchange rate for 1 USD?"
        }
      ]
    }
  }
}
```

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 10,
  "result": {
    "id": "130",
    "status": {
      "state": "input-required",
      "message": {
        "role": "agent",
        "parts": [
          {
            "type": "text",
            "text": "Which currency do you want to convert to? Also, do you want the latest exchange rate or a specific date?"
          }
        ]
      },
      "timestamp": "2025-04-02T16:57:02.336787"
    },
    "history": []
  }
}
```

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tasks/send",
  "params": {
    "id": "130",
    "sessionId": "a9bb617f2cd94bd585da0f88ce2ddba2",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "CAD"
        }
      ]
    }
  }
}
```

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 10,
  "result": {
    "id": "130",
    "status": {
      "state": "completed",
      "timestamp": "2025-04-02T16:57:40.033328"
    },
    "artifacts": [
      {
        "parts": [
          {
            "type": "text",
            "text": "The current exchange rate is 1 USD = 1.4328 CAD."
          }
        ],
        "index": 0
      }
    ],
    "history": []
  }
}
```

----------------------------------------

TITLE: A2A Synchronous Request for Currency Exchange Rate
DESCRIPTION: Example JSON request and response for a synchronous query to convert USD to INR using the A2A protocol's tasks/send method, demonstrating a complete single-turn interaction.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/langgraph/README.md#2025-04-21_snippet_2

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "tasks/send",
  "params": {
    "id": "129",
    "sessionId": "8f01f3d172cd4396a0e535ae8aec6687",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "How much is the exchange rate for 1 USD to INR?"
        }
      ]
    }
  }
}
```

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 11,
  "result": {
    "id": "129",
    "status": {
      "state": "completed",
      "timestamp": "2025-04-02T16:53:29.301828"
    },
    "artifacts": [
      {
        "parts": [
          {
            "type": "text",
            "text": "The exchange rate for 1 USD to INR is 85.49."
          }
        ],
        "index": 0
      }
    ],
    "history": []
  }
}
```

----------------------------------------

TITLE: A2A Protocol Response for Currency Conversion
DESCRIPTION: This JSON snippet shows the A2A protocol response for a currency conversion request. It includes the conversion result, status, and other metadata.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/semantickernel/README.md#2025-04-21_snippet_4

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 33,
  "result": {
    "id": "3",
    "status": {
      "state": "completed",
      "timestamp": "2025-04-01T16:53:29.301828"
    },
    "artifacts": [
      {
        "parts": [
          {
            "type": "text",
            "text": "1 USD is approximately 0.88137 EUR."
          }
        ],
        "index": 0
      }
    ],
    "history": []
  }
}
```

----------------------------------------

TITLE: A2A Protocol Request for Currency Conversion
DESCRIPTION: This JSON snippet demonstrates an A2A protocol request for currency conversion. It includes the JSON-RPC structure with method, params, and message details.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/semantickernel/README.md#2025-04-21_snippet_3

LANGUAGE: json
CODE:
```
{
  "jsonrpc": "2.0",
  "id": 33,
  "method": "tasks/send",
  "params": {
    "id": "3",
    "sessionId": "1aab49f1e85c499da48c2124f4ceee4d",
    "acceptedOutputModes": ["text"],
    "message": {
      "role": "user",
      "parts": [
        { "type": "text", "text": "How much is 1 USD to EUR?" }
      ]
    }
  }
}
```

----------------------------------------

TITLE: Defining ContactInfo data structure in Python
DESCRIPTION: Python code defining the ContactInfo class using Pydantic BaseModel. It specifies the structure of the extracted contact information, including name, email, phone, organization, and role fields.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/marvin/README.md#2025-04-21_snippet_2

LANGUAGE: python
CODE:
```
class ContactInfo(BaseModel):
    name: str = Field(description="Person's first and last name")
    email: EmailStr
    phone: str = Field(description="standardized phone number")
    organization: str | None = Field(None, description="org if mentioned")
    role: str | None = Field(None, description="title or role if mentioned")
```

----------------------------------------

TITLE: Sequence Diagram of A2A and CrewAI Integration Flow
DESCRIPTION: Mermaid sequence diagram showing the interaction flow between A2A client, server, CrewAI agent, and Gemini API for image generation process.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/crewai/README.md#2025-04-21_snippet_0

LANGUAGE: mermaid
CODE:
```
sequenceDiagram
    participant Client as A2A Client
    participant Server as A2A Server
    participant Agent as CrewAI Agent
    participant API as Gemini API

    Client->>Server: Send task with text prompt
    Server->>Agent: Forward prompt to image agent
    Note over Server,Agent: Optional: Simulated streaming updates
    Agent->>API: Generate image using Gemini
    API->>Agent: Return generated image
    Agent->>Server: Store image and return ID
    Server->>Client: Respond with image artifact
```

----------------------------------------

TITLE: Sequence Diagram for File Chat Workflow
DESCRIPTION: A mermaid sequence diagram illustrating the interaction flow between A2A Client, Server, ParseAndChat Workflow, and External APIs, showing the message handling process with file attachments, streaming updates, and response generation.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/llama_index_file_chat/README.md#2025-04-21_snippet_0

LANGUAGE: mermaid
CODE:
```
sequenceDiagram
    participant Client as A2A Client
    participant Server as A2A Server
    participant Workflow as ParseAndChat Workflow
    participant Services as External APIs

    Client->>Server: Send message (with or without attachment)
    Server->>Workflow: Forward as InputEvent

    alt Has Attachment
        Workflow-->>Server: Stream LogEvent "Parsing document..."
        Server-->>Client: Stream status update
        Workflow->>Services: Parse document
        Workflow-->>Server: Stream LogEvent "Document parsed successfully"
        Server-->>Client: Stream status update
    end

    Workflow-->>Server: Stream LogEvent about chat processing
    Server-->>Client: Stream status update
    
    Workflow->>Services: LLM Chat (with document context if available)
    Services->>Workflow: Structured LLM Response
    Workflow-->>Server: Stream LogEvent about response processing
    Server-->>Client: Stream status update
    
    Workflow->>Server: Return final ChatResponseEvent
    Server->>Client: Return response with citations (if available)

    Note over Server: Context is maintained for follow-up questions
```

----------------------------------------

TITLE: Visualizing Agent Flow with Mermaid Diagram
DESCRIPTION: A sequence diagram illustrating the interaction flow between the A2A client, server, LangGraph agent, and Frankfurter API. It shows the complete information path, incomplete information flow requiring additional input, and streaming capabilities.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/langgraph/README.md#2025-04-21_snippet_0

LANGUAGE: mermaid
CODE:
```
sequenceDiagram
    participant Client as A2A Client
    participant Server as A2A Server
    participant Agent as LangGraph Agent
    participant API as Frankfurter API

    Client->>Server: Send task with currency query
    Server->>Agent: Forward query to currency agent

    alt Complete Information
        Agent->>API: Call get_exchange_rate tool
        API->>Agent: Return exchange rate data
        Agent->>Server: Process data & return result
        Server->>Client: Respond with currency information
    else Incomplete Information
        Agent->>Server: Request additional input
        Server->>Client: Set state to "input-required"
        Client->>Server: Send additional information
        Server->>Agent: Forward additional info
        Agent->>API: Call get_exchange_rate tool
        API->>Agent: Return exchange rate data
        Agent->>Server: Process data & return result
        Server->>Client: Respond with currency information
    end

    alt With Streaming
        Note over Client,Server: Real-time status updates
        Server->>Client: "Looking up exchange rates..."
        Server->>Client: "Processing exchange rates..."
        Server->>Client: Final result
    end
```

----------------------------------------

TITLE: Setting Up and Running Movie Info Agent with TMDB and Gemini APIs
DESCRIPTION: This snippet demonstrates how to set up the required API keys as environment variables and start the Movie Info Agent. It requires a TMDB API key and a Gemini API key. The agent will be accessible at http://localhost:41241 after starting.
SOURCE: https://github.com/google/a2a/blob/main/samples/js/src/agents/movie-agent/README.md#2025-04-21_snippet_0

LANGUAGE: bash
CODE:
```
export TMDB_API_KEY=<api_key> # see https://developer.themoviedb.org/docs/getting-started
export GEMINI_API_KEY=<api_key>
npm run agents:movie-agent
```

----------------------------------------

TITLE: Starting the Coder Agent with Gemini API Key
DESCRIPTION: Commands to set up the Gemini API key and start the Coder Agent service. The agent will run on http://localhost:41241/ after successful execution.
SOURCE: https://github.com/google/a2a/blob/main/samples/js/src/agents/coder/README.md#2025-04-21_snippet_0

LANGUAGE: bash
CODE:
```
export GEMINI_API_KEY=<your_api_key>
npm run agents:coder
```

----------------------------------------

TITLE: Running Semantic Kernel Agent with A2A Protocol
DESCRIPTION: These commands demonstrate how to run the Semantic Kernel agent. It includes options for running on the default port or specifying a custom host and port.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/semantickernel/README.md#2025-04-21_snippet_1

LANGUAGE: bash
CODE:
```
# Basic run on default port 10020
uv run .
```

LANGUAGE: bash
CODE:
```
# On custom host/port
uv run . --host 0.0.0.0 --port 8080
```

----------------------------------------

TITLE: Running A2A Client for Semantic Kernel Agent
DESCRIPTION: This command shows how to run the A2A client to interact with the Semantic Kernel agent. It specifies the agent's URL as a parameter.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/semantickernel/README.md#2025-04-21_snippet_2

LANGUAGE: bash
CODE:
```
cd samples/python/hosts/cli
uv run . --agent http://localhost:10020
```

----------------------------------------

TITLE: Running the LlamaIndex File Chat Agent
DESCRIPTION: Bash commands demonstrating how to run the agent using UV, either with default settings on port 10010 or with custom host and port configurations.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/llama_index_file_chat/README.md#2025-04-21_snippet_2

LANGUAGE: bash
CODE:
```
# Basic run on default port 10010
uv run .

# On custom host/port
uv run . --host 0.0.0.0 --port 8080
```

----------------------------------------

TITLE: Running an A2A Client for Testing
DESCRIPTION: Bash commands showing how to set up and run an A2A client to test the agent, including downloading a sample PDF file and connecting to the agent at the specified URL.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/llama_index_file_chat/README.md#2025-04-21_snippet_3

LANGUAGE: bash
CODE:
```
cd samples/python/hosts/cli
uv run . --agent http://localhost:10010

# Download a sample file for testing
wget https://arxiv.org/pdf/1706.03762 -O attention.pdf
```

----------------------------------------

TITLE: Running the A2A Agent
DESCRIPTION: Commands to run the agent with different configuration options including custom host and port settings.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/crewai/README.md#2025-04-21_snippet_3

LANGUAGE: bash
CODE:
```
# Basic run
uv run .

# On custom host/port
uv run . --host 0.0.0.0 --port 8080
```

----------------------------------------

TITLE: Running the A2A Client
DESCRIPTION: Commands to run the A2A client and connect to the agent with specified URL and port.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/crewai/README.md#2025-04-21_snippet_4

LANGUAGE: bash
CODE:
```
# Connect to the agent (specify the agent URL with correct port)
cd samples/python/hosts/cli   
uv run . --agent http://localhost:10001

# If you changed the port when starting the agent, use that port instead
# uv run . --agent http://localhost:YOUR_PORT
```

----------------------------------------

TITLE: Setting up and running the Marvin agent server in Bash
DESCRIPTION: Commands for navigating to the project directory, setting up the Python environment, and running the Marvin agent server. It includes options for setting the OpenAI API key and specifying custom host/port.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/marvin/README.md#2025-04-21_snippet_0

LANGUAGE: bash
CODE:
```
cd samples/python/agents/marvin

export OPENAI_API_KEY=your_api_key_here

uv venv
source .venv/bin/activate
uv sync

# Default host/port (localhost:10030)
MARVIN_DATABASE_URL=sqlite+aiosqlite:///test.db MARVIN_LOG_LEVEL=DEBUG uv run .

# Custom host/port
# uv run . --host 0.0.0.0 --port 8080
```

----------------------------------------

TITLE: Running the A2A client CLI in Bash
DESCRIPTION: Commands for running an A2A client, specifically the sample CLI, to interact with the Marvin agent server. It assumes the Python environment is already active.
SOURCE: https://github.com/google/a2a/blob/main/samples/python/agents/marvin/README.md#2025-04-21_snippet_1

LANGUAGE: bash
CODE:
```
# Ensure the environment is active (source .venv/bin/activate)
cd samples/python/hosts/cli
uv run . --agent http://localhost:10030 # Use the correct agent URL/port
```