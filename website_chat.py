import asyncio
import json
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from gpt4_response import generate_gpt4_response
from database import db

class WebsiteChatManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """
        Establish a new WebSocket connection
        """
        await websocket.accept()
        
        # Generate or use provided client ID
        if not client_id:
            client_id = str(uuid.uuid4())
        
        # Store the connection
        self.active_connections[client_id] = websocket
        return client_id

    async def disconnect(self, client_id: str):
        """
        Remove a WebSocket connection
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Send a message to a specific WebSocket
        """
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """
        Send a message to all connected clients
        """
        for connection in self.active_connections.values():
            await connection.send_text(message)

# Initialize chat manager
chat_manager = WebsiteChatManager()

# Create FastAPI app for WebSocket chat
app = FastAPI(title="Website Chat WebSocket")

# CORS middleware to allow all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket, client_id: str = None):
    """
    WebSocket endpoint for real-time chat
    """
    # Connect the client
    try:
        # Establish connection and get/generate client ID
        current_client_id = await chat_manager.connect(websocket, client_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                # Parse message (assuming JSON format)
                message_data = json.loads(data)
                message_text = message_data.get('message', '')
                
                # Generate AI response
                response_text = generate_gpt4_response(message_text)
                
                # Prepare response payload
                response_payload = {
                    'sender': 'ai',
                    'message': response_text
                }
                
                # Send AI response back to client
                await chat_manager.send_personal_message(
                    json.dumps(response_payload), 
                    websocket
                )
                
                # Log chat interaction
                db.log_chat(
                    phone_number=current_client_id, 
                    message=message_text, 
                    response=response_text, 
                    direction='website_chat'
                )
            
            except Exception as e:
                # Handle any processing errors
                error_response = {
                    'sender': 'system',
                    'message': f"Sorry, an error occurred: {str(e)}"
                }
                await chat_manager.send_personal_message(
                    json.dumps(error_response), 
                    websocket
                )
    
    except WebSocketDisconnect:
        # Remove the connection when client disconnects
        await chat_manager.disconnect(current_client_id)

# Standalone run configuration
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 