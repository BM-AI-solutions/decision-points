from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai import Agent
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

def get_model():
    llm = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')
    base_url = os.getenv('BASE_URL', 'https://api.openai.com/v1')
    api_key = os.getenv('LLM_API_KEY', 'no-api-key-provided')

    return OpenAIModel(llm, provider=OpenAIProvider(base_url=base_url, api_key=api_key))

server = MCPServerStdio(
    'npx', 
    ['-y', '@modelcontextprotocol/server-brave-search', 'stdio'], 
    env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")}
)
agent = Agent(get_model(), mcp_servers=[server])


async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('What is new with Gemini 2.5 Pro?')
    print(result.data)
    user_input = input("Press enter to quit...")

if __name__ == '__main__':
    asyncio.run(main())