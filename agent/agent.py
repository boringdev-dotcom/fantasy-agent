import os
from typing import Dict, List, Optional
import nest_asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.openai import OpenAIProvider
import requests
from datetime import datetime
from dotenv import load_dotenv

nest_asyncio.apply()
load_dotenv()

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

model = AnthropicModel('claude-3-7-sonnet-latest', api_key=os.getenv('ANTHROPIC_API_KEY'))

# model = OpenAIModel('gpt-4o', provider=OpenAIProvider(api_key='key'))


# model = OpenAIModel(
#     'deepseek-chat',
#     provider=OpenAIProvider(
#         base_url='https://api.deepseek.com', api_key='key'
#     ),
# )

prompt = (
    "You are an intelligent fantasy sports agent. You can talk about any sports but nothing else. "
    "Help users analyze player projections and make informed decisions for their fantasy teams. "
    "Always greet the customer and provide a helpful response. "
    "You can fetch projections using the get_projections tool with any of these parameters: "
    "player_name, stat_type (e.g., 'points', 'rebounds', 'shots', 'assists'), or sport_id (e.g., 7 for NBA, 82 for Soccer). "
    "At least one parameter must be provided. For example, you can get all NBA projections, all projections for a specific player, or all 'points' projections across sports."
)

print(prompt)

agent = Agent(
    model=model,
    deps_type=AgentDependencies,
    retries=3,
    system_prompt=prompt
)

@agent.tool
def get_projections(
    ctx: RunContext[AgentDependencies], 
    player_name: Optional[str] = None,
    stat_type: Optional[str] = None,
    sport_id: Optional[int] = None
) -> str:
    """Get the projections for players by making an API call
    
    Args:
        ctx: The run context containing dependencies
        player_name: Optional name of the player to get projections for
        stat_type: Optional filter for specific stat type (e.g., "points", "rebounds", "assists", "shots")
        sport_id: Optional filter for specific sport ID (e.g., 7 for NBA, 82 for Soccer)
        
    Note: At least one parameter (player_name, stat_type, or sport_id) must be provided.
    Important: Use the exact sport_id values provided by the user. NBA is sport_id 7, and Soccer is sport_id 82. Do not substitute these values.
    """
    
    # Validate that at least one parameter is provided
    if player_name is None and stat_type is None and sport_id is None:
        return "Error: At least one parameter (player_name, stat_type, or sport_id) must be provided."
    
    filter_msg = []
    if player_name:
       filter_msg.append(f"player '{player_name}'")
    if stat_type:
        filter_msg.append(f"stat type '{stat_type}'")
    if sport_id:
        filter_msg.append(f"sport ID {sport_id}")
    filter_str = ", ".join(filter_msg)

    try:
        # Build query parameters including only the provided filters
        params = {}
        if player_name is not None:
            params["player_name"] = player_name
        if stat_type is not None:
            params["stat_type"] = stat_type
        if sport_id is not None:
            params["sport_id"] = sport_id
            
        print(f"Getting projections with params: {params}")
        api_url = f"{ctx.deps.api_base_url}/api/projections"
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        data = response.json()
        print(f"Response data: {data}")
        
        # Parse the response into PlayerProjection objects
        projections = [PlayerProjection(**item) for item in data]
        
        if not projections:
            return f"No projections found for {filter_str}."
        
        # Format the response in a readable way
        # Construct a title based on the provided parameters
        result_title = "Projections"
        filter_parts = []
        if player_name:
            filter_parts.append(f"player: {player_name}")
        if stat_type:
            filter_parts.append(f"stat type: {stat_type}")
        if sport_id:
            filter_parts.append(f"sport ID: {sport_id}")
        
        if filter_parts:
            result_title += f" for {', '.join(filter_parts)}"
        result = f"{result_title}:\n"
        
        for proj in projections:
            result += f"- {proj.player_name}: {proj.stat_type} = {proj.line_score} ({proj.description})\n"
            result += f"  Game starts: {proj.start_time.strftime('%Y-%m-%d %H:%M')}\n"
            if proj.opponent:
                result += f"  Opponent: {proj.opponent}\n"
            result += "\n"
        
        return result
    except Exception as e:       
        return f"Error fetching projections for {filter_str}: {str(e)}"