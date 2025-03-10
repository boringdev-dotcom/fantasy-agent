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

            messages = manager.message_histories[session_id]
            deps = manager.deps_store[session_id]

            result = await agent.run(
                data, 
                deps=deps, 
                message_history=messages
            )

            messages.append(ModelRequest(parts=[UserPromptPart(content=data)]))
            response = {
                "text": result.data,
                "sources": []
              }
            
            await manager.send_message(session_id, json.dumps(response))
            messages.append(ModelResponse(parts=[TextPart(content=result.data)]))
    except WebSocketDisconnect:
        manager.disconnect(session_id)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    uvicorn.run(app, host="0.0.0.0", port=port)


    
            
