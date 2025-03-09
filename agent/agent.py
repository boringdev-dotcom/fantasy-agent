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
import traceback

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

class PlayerDetailsForStats(BaseModel):
    class Team(BaseModel):
        id: int
        conference: str
        division: str
        city: str
        name: str
        full_name: str
        abbreviation: str
    
    id: int
    first_name: str
    last_name: str
    position: str
    height: str
    weight: str
    jersey_number: str
    college: str
    country: str
    draft_year: int
    draft_round: int
    draft_number: int
    team: Optional[Team] = None
    team_id: Optional[int] = None

class Game(BaseModel):
    id: int
    date: str
    season: int
    status: str
    period: int
    time: str
    postseason: bool
    home_team_score: int
    visitor_team_score: int
    datetime: str
    home_team_id: int
    visitor_team_id: int

class PlayerStatsResponse(BaseModel):
    id: int
    min: str
    fgm: int
    fga: int
    fg_pct: float = 0.0
    fg3m: int
    fg3a: int
    fg3_pct: Optional[float] = 0.0
    ftm: int
    fta: int
    ft_pct: Optional[float] = 0.0
    oreb: int
    dreb: int
    reb: int
    ast: int
    stl: int
    blk: int
    turnover: int
    pf: int
    pts: int
    player: PlayerDetailsForStats
    team: Optional[PlayerDetailsForStats.Team] = None
    game: Game

class AgentDependencies(BaseModel):
    api_base_url: str = "http://localhost:8000"
    nba_api: str = "https://api.balldontlie.io/v1"

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
    "When users ask about player details or statistics, follow these steps:\n"
        "1. First use the get_player_details_for_stats tool with the player's first and last name to find their information and ID\n"
        "2. Then use the get_player_stats tool with that ID to fetch their detailed statistics for the current season\n"
        "3. If either tool returns an error, clearly explain what happened and provide the information you were able to retrieve\n"
        "4. Always include the player ID in your response when available, as it's needed for fetching stats\n"
        "5. If the stats API returns an error, suggest trying again or checking if the player is active in the current season"
)

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
        
        # Format the response in a more readable and visually appealing way
        result = f"📊 PROJECTIONS FOR {player_name.upper()} 📊\n"
        result += f"{'=' * 40}\n\n"
        
        # Group projections by stat type for better organization
        stat_projections = {}
        for proj in projections:
            if proj.stat_type not in stat_projections:
                stat_projections[proj.stat_type] = []
            stat_projections[proj.stat_type].append(proj)
        
        # Display game information once if all projections are for the same game
        if len(set(p.game_id for p in projections)) == 1:
            game_info = projections[0]
            result += f"🏀 GAME INFO:\n"
            result += f"   Date: {game_info.start_time.strftime('%A, %B %d, %Y')}\n"
            result += f"   Time: {game_info.start_time.strftime('%I:%M %p')}\n"
            if game_info.opponent:
                result += f"   Opponent: {game_info.opponent}\n"
            result += f"   Status: {'Active' if game_info.is_active else 'Inactive'}\n\n"
        
        result += f"📈 PROJECTED STATS:\n"
        
        # Display projections by category
        for stat_type, projs in stat_projections.items():
            result += f"\n   {stat_type.upper()}:\n"
            for proj in projs:
                result += f"   • {proj.line_score:.1f} - {proj.description}\n"
                
                # Only show game info if we have multiple games
                if len(set(p.game_id for p in projections)) > 1:
                    result += f"     Game: {proj.start_time.strftime('%a, %b %d')} at {proj.start_time.strftime('%I:%M %p')}"
                    if proj.opponent:
                        result += f" vs {proj.opponent}"
                    result += f" ({'Active' if proj.is_active else 'Inactive'})\n"
        return result
    except Exception as e:       
        return f"Error fetching projections for {filter_str}: {str(e)}"
    
@agent.tool 
def get_player_details_for_stats(ctx: RunContext[AgentDependencies], first_name: str, last_name: str) -> str:
    """Get the player details for stats by making an API call
    
    Args:
        ctx: The run context containing dependencies
        first_name: The first name of the player to get details for
        last_name: The last name of the player to get details for
    """

    try:
        print(f"Getting player details for {first_name} {last_name}")
        api_url = f"{ctx.deps.nba_api}/players"
        
        params = {
            "first_name": first_name,
            "last_name": last_name
        }
        
        headers = {
            "Authorization": f"{os.getenv('STATS_API_KEY')}"
        }
        
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        print(f"API Response Status Code: {response.status_code}")
        data = response.json()
        print(f"Data structure: {list(data.keys())}")
        
        if not data.get("data") or len(data["data"]) == 0:
            return f"No player details found for {first_name} {last_name}."
        
        print(f"Number of player entries: {len(data['data'])}")
        
        # Parse the first player from the response
        player_data = data["data"][0]
        player = PlayerDetailsForStats(**player_data)
        
        # Format the response in a readable way
        result = f"Player Details for {player.first_name} {player.last_name}:\n"
        result += f"Position: {player.position}\n"
        result += f"Height: {player.height}\n"
        result += f"Weight: {player.weight}\n"
        result += f"Jersey Number: {player.jersey_number}\n"
        result += f"College: {player.college}\n"
        result += f"Country: {player.country}\n"
        result += f"Draft: {player.draft_year} Round {player.draft_round} Pick {player.draft_number}\n"
        result += f"Team: {player.team.full_name} ({player.team.abbreviation})\n"
        result += f"Conference: {player.team.conference}, Division: {player.team.division}\n"
        result += f"\nPlayer ID: {player.id}\n"
        result += f"\nTo get detailed statistics for this player, use the get_player_stats tool with the player ID: {player.id}\n"
        result += f"Example: get_player_stats({player.id})\n"
        
        return result
    except Exception as e:
        print(f"Error in get_player_details_for_stats: {str(e)}")
        traceback_str = traceback.format_exc()
        print(f"Traceback: {traceback_str}")
        return f"Error fetching player details for {first_name} {last_name}: {str(e)}"
    
        
@agent.tool 
def get_player_stats(ctx: RunContext[AgentDependencies], player_id: int) -> str:
    """Get the player stats by making an API call
    
    Args:
        ctx: The run context containing dependencies
        player_id: The ID of the player to get stats for
    """
    
    try:
        print(f"Getting player stats for player ID: {player_id}")
        api_url = f"{ctx.deps.nba_api}/stats"
        
        # Hardcoding seasons and per_page as requested
        params = {
            "player_ids[]": player_id,
            "seasons[]": 2024,
            "per_page": 82
        }

        headers = {
            "Authorization": f"{os.getenv('STATS_API_KEY')}"
        }
        
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        print(f"API Response Status Code: {response.status_code}")
        data = response.json()
        
        if not data.get("data") or len(data["data"]) == 0:
            return f"No stats found for player ID {player_id}."
        
        print(f"Number of stat entries: {len(data['data'])}")
        
        # Extract data from the API response
        stats_list = []
        for item in data["data"]:
            try:
                # Extract player info
                player_info = item.get("player", {})
                player_name = f"{player_info.get('first_name', '')} {player_info.get('last_name', '')}"
                
                # Extract team info - it's at the same level as player, not inside it
                team_info = item.get("team", {})
                team_name = team_info.get("full_name", "")
                team_abbr = team_info.get("abbreviation", "")
                
                # Extract game info
                game_info = item.get("game", {})
                game_date = game_info.get("date", "")
                home_team_id = game_info.get("home_team_id")
                visitor_team_id = game_info.get("visitor_team_id")
                home_score = game_info.get("home_team_score", 0)
                visitor_score = game_info.get("visitor_team_score", 0)
                
                # Extract stat values with defaults for missing data
                minutes = item.get("min", "0")
                points = item.get("pts", 0)
                rebounds = item.get("reb", 0)
                assists = item.get("ast", 0)
                steals = item.get("stl", 0)
                blocks = item.get("blk", 0)
                
                # Only add entries with valid minutes
                if minutes and minutes != "00" and minutes != "0":
                    stats_list.append({
                        "player_name": player_name,
                        "team_id": team_info.get("id"),
                        "team_name": team_name,
                        "team_abbr": team_abbr,
                        "game_date": game_date,
                        "home_team_id": home_team_id,
                        "visitor_team_id": visitor_team_id,
                        "home_score": home_score,
                        "visitor_score": visitor_score,
                        "minutes": minutes,
                        "points": points,
                        "rebounds": rebounds,
                        "assists": assists,
                        "steals": steals,
                        "blocks": blocks,
                        "fg_pct": item.get("fg_pct", 0) or 0,
                        "fg3_pct": item.get("fg3_pct", 0) or 0,
                        "ft_pct": item.get("ft_pct", 0) or 0,
                        "fga": item.get("fga", 0),
                        "fg3a": item.get("fg3a", 0),
                        "fta": item.get("fta", 0)
                    })
            except Exception as e:
                print(f"Error processing stat item: {e}")
                continue
        
        if not stats_list:
            return f"No valid stats found for player ID {player_id}."
        
        # Get player name and team from the first stat entry
        player_name = stats_list[0]["player_name"]
        team_name = stats_list[0]["team_name"]
        
        # Calculate averages
        games_played = len(stats_list)
        
        if games_played == 0:
            return f"Stats found for {player_name}, but no games with recorded minutes."
        
        total_pts = sum(stat["points"] for stat in stats_list)
        total_reb = sum(stat["rebounds"] for stat in stats_list)
        total_ast = sum(stat["assists"] for stat in stats_list)
        total_stl = sum(stat["steals"] for stat in stats_list)
        total_blk = sum(stat["blocks"] for stat in stats_list)
        
        # Only count games with attempts for percentages
        fg_games = sum(1 for stat in stats_list if stat["fga"] > 0)
        fg3_games = sum(1 for stat in stats_list if stat["fg3a"] > 0)
        ft_games = sum(1 for stat in stats_list if stat["fta"] > 0)
        
        # Format the response in a readable way
        result = f"Stats for {player_name} ({team_name}) - 2024 Season:\n"
        result += f"Games Played: {games_played}\n\n"
        
        result += f"Season Averages:\n"
        result += f"Points: {total_pts / games_played:.1f}\n"
        result += f"Rebounds: {total_reb / games_played:.1f}\n"
        result += f"Assists: {total_ast / games_played:.1f}\n"
        result += f"Steals: {total_stl / games_played:.1f}\n"
        result += f"Blocks: {total_blk / games_played:.1f}\n"
        
        # Only include percentages if there are games with attempts
        if fg_games > 0:
            total_fg_pct = sum(stat["fg_pct"] for stat in stats_list if stat["fga"] > 0)
            result += f"FG%: {(total_fg_pct / fg_games) * 100:.1f}%\n"
        
        if fg3_games > 0:
            total_fg3_pct = sum(stat["fg3_pct"] for stat in stats_list if stat["fg3a"] > 0)
            result += f"3PT%: {(total_fg3_pct / fg3_games) * 100:.1f}%\n"
        
        if ft_games > 0:
            total_ft_pct = sum(stat["ft_pct"] for stat in stats_list if stat["fta"] > 0)
            result += f"FT%: {(total_ft_pct / ft_games) * 100:.1f}%\n"
        
        # Add recent game performances (last 3 games)
        recent_games = stats_list[-3:]
        if recent_games:
            result += "\nRecent Performances:\n"
            for game in recent_games:
                game_date = game["game_date"]
                
                # Handle home vs away game display
                if game["home_team_id"] == game["team_id"]:
                    result += f"{game_date} vs. {game['team_abbr']} (Home, {game['home_score']}-{game['visitor_score']}): "
                else:
                    result += f"{game_date} @ {game['team_abbr']} (Away, {game['visitor_score']}-{game['home_score']}): "
                
                result += f"{game['points']} PTS, {game['rebounds']} REB, {game['assists']} AST, {game['steals']} STL, {game['blocks']} BLK\n"
        
        return result
    except Exception as e:
        print(f"Error in get_player_stats: {str(e)}")
        traceback_str = traceback.format_exc()
        print(f"Traceback: {traceback_str}")
        return f"Error fetching stats for player ID {player_id}: {str(e)}"
    
