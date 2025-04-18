from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import sys
import os
import httpx
import json
from ai_agent import ai_agent, Deps

from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    UserPromptPart,
    TextPart,
    ToolReturnPart)
# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()
security = HTTPBearer()

# Supabase setup
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class AgentRequest(BaseModel):
    query: str
    user_id: str
    request_id: str
    session_id: str

class AgentResponse(BaseModel):
    success: bool

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """Verify the bearer token against environment variable."""
    expected_token = os.getenv("API_BEARER_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="API_BEARER_TOKEN environment variable not set"
        )
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return True

async def fetch_conversation_history(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch the most recent conversation history for a session."""
    try:
        response = supabase.table("messages") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        # Convert to list and reverse to get chronological order
        messages = response.data[::-1]
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch conversation history: {str(e)}")

async def store_message(session_id: str, message_type: str, content: str, data: Optional[Dict] = None):
    """Store a message in the Supabase messages table."""
    message_obj = {
        "type": message_type,
        "content": content
    }
    if data:
        message_obj["data"] = data

    try:
        supabase.table("messages").insert({
            "session_id": session_id,
            "message": message_obj
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store message: {str(e)}")

@app.post("/api/ask-reddit-agent", response_model=AgentResponse)
async def sample_supabase_agent(
    request: AgentRequest,
    authenticated: bool = Depends(verify_token)
):
    try:
        # Fetch conversation history from the DB
        conversation_history = await fetch_conversation_history(request.session_id)
        
        # Convert conversation history to format expected by agent
        # This will be different depending on your framework (Pydantic AI, LangChain, etc.)
        messages = []
        for msg in conversation_history:
            msg_data = msg["message"]
            msg_type = msg_data["type"]
            msg_content = msg_data["content"]
            msg = ModelRequest(parts=[UserPromptPart(content=msg_content)]) if msg_type == "human" else ModelResponse(parts=[TextPart(content=msg_content)])
            messages.append(msg)

        # Store user's query
        await store_message(
            session_id=request.session_id,
            message_type="human",
            content=request.query
        )            

        # Initialize agent dependencies
        async with httpx.AsyncClient() as client:
            deps = Deps(
                client=client,
                reddit_client_id=os.getenv("REDDIT_CLIENT_ID", None),
                reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET", None),
                brave_api_key=os.getenv("BRAVE_API_KEY", None),
            )

            """
            This is where you insert the custom logic to get the response from your agent.
            Your agent can also insert more records into the database to communicate
            actions/status as it is handling the user's question/request.
            Additionally:
                - Use the 'messages' array defined about for the chat history. This won't include the latest message from the user.
                - Use request.query for the user's prompt.
                - Use request.session_id if you need to insert more messages into the DB in the agent logic.
            """
            # Run the agent with conversation history
            result = await ai_agent.run(
                "use Reddit to answer this query: " + request.query,
                message_history=messages,
                deps=deps
            )

            tool_results = {}

            for msg in result._all_messages:
                for part in msg.parts:
                    if part.part_kind == "tool-return":
                        tool_call_id = part.tool_call_id
                        tool_results[tool_call_id] = {
                            **tool_results.get(tool_call_id, {}),  # Preserve existing 'args'
                            'result': part.content,
                        }
                    elif part.part_kind == "tool-call":
                        tool_call_id = part.tool_call_id
                        tool_results[tool_call_id] = {
                            'args': json.loads(part.args.args_json),
                            'tool_name': part.tool_name,
                            **tool_results.get(tool_call_id, {}),  # Preserve existing 'result'
                        }
        # Store agent's response
        await store_message(
            session_id=request.session_id,
            message_type="ai",
            content=result.data,
            data={"tool_results": tool_results} # TODO add the data from the tool call
        )

        return AgentResponse(success=True)

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        # Store error message in conversation
        await store_message(
            session_id=request.session_id,
            message_type="ai",
            content="I apologize, but I encountered an error processing your request.",
            data={"error": str(e), "request_id": request.request_id}
        )
        return AgentResponse(success=False)

if __name__ == "__main__":
    import uvicorn
    # Feel free to change the port here if you need
    uvicorn.run(app, host="0.0.0.0", port=8001)