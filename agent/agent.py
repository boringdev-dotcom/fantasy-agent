from typing import Dict, List, Optional
import nest_asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.openai import OpenAIProvider
import requests
from datetime import datetime


nest_asyncio.apply()

# Define Pydantic models for the API response
class PlayerProjection(BaseModel):
    id: str
    player_id: str
    player_name: str
    sport_id: int
    sport_name: str
    game_id: str
    stat_type: str
    line_score: float
    description: str
    start_time: datetime
    is_active: bool
    opponent: Optional[str] = None

class AgentDependencies(BaseModel):
    api_base_url: str = "http://localhost:8000"

# model = AnthropicModel('claude-3-7-sonnet-latest', api_key='key')

model = OpenAIModel('gpt-4o', provider=OpenAIProvider(api_key='key'))


# model = OpenAIModel(
#     'deepseek-chat',
#     provider=OpenAIProvider(
#         base_url='https://api.deepseek.com', api_key='key'
#     ),
# )

agent = Agent(
    model=model,
    deps_type=AgentDependencies,
    retries=3,
    system_prompt=(
        "You are an intelligent fantasy sports agent. You can talk about any sports but nothing else"
        "Help users analyze player projections and make informed decisions for their fantasy teams. "
        "Always greet the customer and provide a helpful response. "
        "When users ask about players, use the get_projections tool to fetch the latest data."
    ),
)

@agent.tool
def get_projections(ctx: RunContext[AgentDependencies], player_name: str) -> str:
    """Get the projections for a player by making an API call
    
    Args:
        ctx: The run context containing dependencies
        player_name: The name of the player to get projections for
    """
    
    try:
        print(f"Getting projections for {player_name}")
        api_url = f"{ctx.deps.api_base_url}/api/projections"
        response = requests.get(api_url, params={"player_name": player_name})
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        data = response.json()
        
        # Parse the response into PlayerProjection objects
        projections = [PlayerProjection(**item) for item in data]
        
        if not projections:
            return f"No projections found for {player_name}."
        
        # Format the response in a readable way
        result = f"Projections for {player_name}:\n"
        for proj in projections:
            result += f"- {proj.stat_type}: {proj.line_score} ({proj.description})\n"
            result += f"  Game starts: {proj.start_time.strftime('%Y-%m-%d %H:%M')}\n"
            if proj.opponent:
                result += f"  Opponent: {proj.opponent}\n"
        
        return result
    except Exception as e:
        return f"Error fetching projections for {player_name}: {str(e)}"

# Main function to run the agent
def run_agent(query: str, deps: Optional[AgentDependencies] = None) -> str:
    """Run the agent with the given query
    
    Args:
        query: The user's query
        deps: Optional dependencies to pass to the agent
    
    Returns:
        The agent's response
    """
    if deps is None:
        deps = AgentDependencies()
    
    response = agent.run_sync(query, deps=deps)
    return response.data