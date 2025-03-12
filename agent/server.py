from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage, ModelResponse, ModelRequest, UserPromptPart, TextPart
from typing import List, Dict, Any, Optional
import json
import uvicorn
import asyncio
from agent import agent, AgentDependencies
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.message_histories: Dict[str, List[ModelMessage]] = {}
        self.deps_store: Dict[str, AgentDependencies] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.message_histories[session_id] = []
        self.deps_store[session_id] = AgentDependencies()

    def disconnect(self, session_id: str):
        del self.active_connections[session_id]
        del self.message_histories[session_id]
        del self.deps_store[session_id]

    async def send_message(self, session_id: str, message: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Parse the received data
            try:
                data_json = json.loads(data)
                user_query = data_json.get("query", data)
            except json.JSONDecodeError:
                user_query = data

            logger.info(f"Received query: {user_query}")
            
            messages = manager.message_histories[session_id]
            deps = manager.deps_store[session_id]

            # Send initial streaming message to indicate processing has started
            initial_response = {
                "text": "...",
                "sources": [],
                "streaming": True
            }
            await manager.send_message(session_id, json.dumps(initial_response))

            # First, use streaming to show progress
            try:
                # Start a background task to run the agent with streaming for UI updates
                async with agent.run_stream(
                    user_query, 
                    deps=deps, 
                    message_history=messages
                ) as result:
                    # Stream text from the agent with debouncing to reduce UI updates
                    async for text in result.stream(debounce_by=0.05):
                        # Send the updated text to the client
                        streaming_response = {
                            "text": text,
                            "sources": [],
                            "streaming": True
                        }
                        await manager.send_message(session_id, json.dumps(streaming_response))
                
                # Now run the agent again to get the complete result with tool calls
                # This ensures we get the full response including all tool call results
                complete_result = await agent.run(
                    user_query,
                    deps=deps,
                    message_history=messages
                )
                
                final_result = complete_result.data
                logger.info(f"Final result: {final_result[:100]}...")  # Log first 100 chars
                
                # Send the final complete message
                final_response = {
                    "text": final_result,
                    "sources": [],
                    "streaming": False
                }
                await manager.send_message(session_id, json.dumps(final_response))
                
                # Update message history
                messages.append(ModelRequest(parts=[UserPromptPart(content=user_query)]))
                messages.append(ModelResponse(parts=[TextPart(content=final_result)]))
            
            except Exception as e:
                logger.error(f"Error during processing: {str(e)}")
                error_response = {
                    "text": f"An error occurred: {str(e)}",
                    "sources": [],
                    "streaming": False
                }
                await manager.send_message(session_id, json.dumps(error_response))
            
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
        manager.disconnect(session_id)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)


    
            
