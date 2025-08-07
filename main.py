import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from gpt4_response import generate_gpt4_response
from health_package_chatbot import health_chatbot  # Import our enhanced chatbot
from booking import save_appointment
from payments import create_payment_link
from utils import validate_twilio_request
from database import db
from instagram_handler import instagram_handler
from fastapi.responses import Response
import json
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="WhatsApp Healthcare Assistant")

# In-memory conversation state storage (use Redis for production)
conversation_states = {}

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/webhook/whatsapp")
async def handle_whatsapp_message(request: Request):
    """
    Enhanced webhook endpoint with GPT-4 + Excel integration
    """
    # Parse incoming form data
    form_data = await request.form()
    from_number = form_data.get('From', '')
    message_body = form_data.get('Body', '').strip()

    # Initialize Twilio response
    response = MessagingResponse()

    try:
        # Get current conversation state
        current_state = conversation_states.get(from_number, {})
        
        # First, try health package chatbot for structured responses
        chatbot_response = health_chatbot.process_message(
            message_body, 
            from_number, 
            current_state.get('state')
        )
        
        # If it's a general query (not booking flow), enhance with GPT-4
        if chatbot_response['state'] in ['menu', 'search_results']:
            # Get Excel context for GPT-4
            excel_context = health_chatbot.get_context_for_gpt(message_body)
            
            # Generate enhanced response with GPT-4
            gpt_response = generate_gpt4_response(
                message_body, 
                context=excel_context,
                conversation_history=current_state.get('history', [])
            )
            
            # Combine structured data with AI response
            if excel_context:
                response_message = f"{chatbot_response['response']}\n\n🤖 **AI Assistant:**\n{gpt_response}"
            else:
                response_message = gpt_response
        else:
            # Use structured response for booking flow
            response_message = chatbot_response['response']
        
        # Update conversation state
        conversation_states[from_number] = {
            'state': chatbot_response['state'],
            'selected_package': chatbot_response.get('selected_package'),
            'last_message_time': str(pd.Timestamp.now()),
            'history': current_state.get('history', []) + [
                {'user': message_body, 'bot': response_message}
            ]
        }

        # Log the chat interaction
        db.log_chat(
            phone_number=from_number, 
            message=message_body, 
            response=response_message
        )

        # Add message to response
        response.message(response_message)

    except Exception as e:
        # Fallback to GPT-4 on error
        try:
            error_response = generate_gpt4_response(
                f"Error processing: {message_body}. Please help the user with healthcare queries."
            )
            response.message(error_response)
        except:
            response.message("Sorry, something went wrong. Please try again later.")
        
        print(f"Error: {e}")

    print(f"Response XML: {str(response)}")
    return Response(content=str(response), media_type="application/xml")

@app.get("/")
async def root():
    return {"message": "WhatsApp Healthcare Assistant API is running!"}

@app.get("/test-chatbot")
async def test_chatbot():
    """Test endpoint for the health chatbot"""
    test_queries = [
        "hello",
        "vitamin d test",
        "wellness packages", 
        "book appointment"
    ]
    
    results = {}
    for query in test_queries:
        result = health_chatbot.process_message(query, "test_number")
        results[query] = result['response']
    
    return results

@app.get("/appointments")
async def get_appointments():
    """Get all appointments"""
    try:
        with open('/Users/yarkhan/Tech/dubai_health_agent_system/appointments.json', 'r') as f:
            appointments = json.load(f)
        return {"appointments": appointments}
    except:
        return {"appointments": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)