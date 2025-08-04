import os
from twilio.rest import Client
from dotenv import load_dotenv
from utils import validate_phone_number, sanitize_message, generate_unique_conversation_id
from gpt4_response import generate_gpt4_response
from booking import save_appointment
from payments import create_payment_link
from database import db

# Load environment variables
load_dotenv()

class WhatsAppHandler:
    def __init__(self):
        """
        Initialize Twilio WhatsApp client
        """
        # Twilio credentials
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        # Validate credentials
        if not all([account_sid, auth_token]):
            raise ValueError("Twilio credentials are missing. Please check your .env file.")
        
        # Initialize Twilio client
        self.client = Client(account_sid, auth_token)
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

    def send_whatsapp_message(self, to_number, message):
        """
        Send a WhatsApp message
        
        :param to_number: Recipient's phone number
        :param message: Message content
        :return: Message SID or None
        """
        try:
            # Validate and standardize phone number
            validated_number = validate_phone_number(to_number)
            
            if not validated_number:
                print(f"Invalid phone number: {to_number}")
                return None
            
            # Prefix with 'whatsapp:' for Twilio
            to_number = f'whatsapp:{validated_number}'
            
            # Send message
            message = self.client.messages.create(
                from_=self.whatsapp_number,
                body=message,
                to=to_number
            )
            
            # Log the outgoing message
            db.log_chat(
                phone_number=validated_number, 
                message=message.body, 
                response='', 
                direction='outgoing'
            )
            
            return message.sid
        
        except Exception as e:
            print(f"WhatsApp Message Send Error: {e}")
            return None

    def handle_incoming_message(self, from_number, message_body):
        """
        Process incoming WhatsApp message
        
        :param from_number: Sender's phone number
        :param message_body: Message content
        :return: Response message
        """
        try:
            # Validate and standardize phone number
            validated_number = validate_phone_number(from_number)
            
            if not validated_number:
                return "Invalid phone number format."
            
            # Sanitize message
            message_body = sanitize_message(message_body)
            
            # Generate unique conversation ID
            conversation_id = generate_unique_conversation_id(validated_number)
            
            # Detect intent and generate response
            if "book" in message_body.lower():
                # Appointment booking flow
                appointment_details = save_appointment(validated_number, message_body)
                response_message = f"✅ Appointment booked: {appointment_details}"
            
            elif "pay" in message_body.lower():
                # Payment link generation
                payment_link = create_payment_link(validated_number)
                response_message = f"💳 Complete your payment: {payment_link}"
            
            else:
                # Default to GPT-4 response
                response_message = generate_gpt4_response(message_body)
            
            # Log the chat interaction
            db.log_chat(
                phone_number=validated_number, 
                message=message_body, 
                response=response_message,
                direction='incoming'
            )
            
            # Send response via WhatsApp
            self.send_whatsapp_message(validated_number, response_message)
            
            return response_message
        
        except Exception as e:
            error_message = f"Sorry, an error occurred: {str(e)}"
            
            # Log error
            db.log_chat(
                phone_number=validated_number, 
                message=message_body, 
                response=error_message,
                direction='error'
            )
            
            return error_message

# Create a global WhatsApp handler instance
whatsapp_handler = WhatsAppHandler() 