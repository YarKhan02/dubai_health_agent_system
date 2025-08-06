import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from gpt4_response import generate_gpt4_response
from excel_chatbot import excel_chatbot  # Import Excel chatbot
from booking import save_appointment
from payments import create_payment_link
from utils import validate_twilio_request
from database import db
from instagram_handler import instagram_handler  # Import Instagram handler

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="WhatsApp Healthcare Assistant")

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
    Webhook endpoint for handling incoming WhatsApp messages
    """
    # Validate Twilio request (optional but recommended)
    # if not validate_twilio_request(request):
    #     raise HTTPException(status_code=403, detail="Invalid Twilio request")

    # Parse incoming form data
    form_data = await request.form()
    from_number = form_data.get('From', '')
    message_body = form_data.get('Body', '').strip()

    # Initialize Twilio response
    response = MessagingResponse()

    try:
        # Enhanced message processing with Excel chatbot integration
        response_message = ""
        
        # Detect intent and generate appropriate response
        if any(keyword in message_body.lower() for keyword in ["book", "appointment", "schedule"]):
            # Appointment booking flow
            appointment_details = save_appointment(from_number, message_body)
            response_message = f"Appointment booked: {appointment_details}"
            
        elif any(keyword in message_body.lower() for keyword in ["pay", "payment", "bill"]):
            # Payment link generation
            payment_link = create_payment_link(from_number)
            response_message = f"Complete your payment: {payment_link}"
            
        else:
            # Use enhanced GPT-4 response with Excel chatbot integration
            response_message = generate_gpt4_response(message_body)

        # Log the chat interaction
        db.log_chat(
            phone_number=from_number, 
            message=message_body, 
            response=response_message
        )

        # Add message to response
        response.message(response_message)

    except Exception as e:
        # Log error and send generic error message
        db.log_chat(
            phone_number=from_number, 
            message=message_body, 
            response=str(e),
            direction='error'
        )
        response.message("Sorry, something went wrong. Please try again later.")

    print(str(response))

    return str(response)

@app.get("/webhook/instagram")
async def instagram_webhook_verify(
    hub_mode: str = None, 
    hub_challenge: str = None, 
    hub_verify_token: str = None
):
    """
    Instagram webhook verification endpoint
    """
    challenge = instagram_handler.verify_webhook(hub_mode, hub_challenge, hub_verify_token)
    
    if challenge:
        return challenge
    
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook/instagram")
async def handle_instagram_message(request: Request):
    """
    Webhook endpoint for handling incoming Instagram messages
    """
    try:
        payload = await request.json()
        response = instagram_handler.handle_incoming_message(payload)
        return {"status": "success", "response": response}
    
    except Exception as e:
        print(f"Instagram Webhook Error: {e}")
        raise HTTPException(status_code=500, detail="Error processing message")

@app.get("/health")
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}

@app.post("/test-chatbot")
async def test_chatbot_endpoint(request: Request):
    """Test endpoint for the Excel-based chatbot"""
    try:
        data = await request.json()
        query = data.get('query', '')
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Get response from Excel chatbot
        excel_response = excel_chatbot.generate_response(query)
        
        # Get enhanced GPT-4 response
        gpt4_response = generate_gpt4_response(query)
        
        return {
            "query": query,
            "excel_response": excel_response,
            "gpt4_response": gpt4_response,
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 