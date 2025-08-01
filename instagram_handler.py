import os
import requests
from dotenv import load_dotenv
from gpt4_response import generate_gpt4_response
from database import db

# Load environment variables
load_dotenv()

class InstagramMessageHandler:
    def __init__(self):
        self.access_token = os.getenv('META_ACCESS_TOKEN')
        self.page_id = os.getenv('INSTAGRAM_PAGE_ID')
        self.graph_url = 'https://graph.facebook.com/v17.0'

    def send_message(self, recipient_id, message):
        """
        Send a message via Instagram
        
        :param recipient_id: Instagram user ID
        :param message: Message to send
        :return: Response from Meta API
        """
        try:
            url = f"{self.graph_url}/{self.page_id}/messages"
            payload = {
                'recipient': {'id': recipient_id},
                'message': {'text': message},
                'messaging_type': 'RESPONSE',
                'access_token': self.access_token
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            # Log outgoing message
            db.log_chat(
                phone_number=recipient_id, 
                message=message, 
                response='', 
                direction='outgoing'
            )
            
            return response.json()
        
        except Exception as e:
            print(f"Instagram Message Send Error: {e}")
            return None

    def handle_incoming_message(self, payload):
        """
        Handle incoming Instagram message
        
        :param payload: Incoming message payload
        :return: Generated response
        """
        try:
            # Extract message details
            messaging = payload.get('entry', [{}])[0].get('messaging', [{}])[0]
            sender_id = messaging.get('sender', {}).get('id')
            message_text = messaging.get('message', {}).get('text', '')
            
            # Generate AI response
            response_text = generate_gpt4_response(message_text)
            
            # Send response
            self.send_message(sender_id, response_text)
            
            # Log incoming message
            db.log_chat(
                phone_number=sender_id, 
                message=message_text, 
                response=response_text, 
                direction='incoming'
            )
            
            return response_text
        
        except Exception as e:
            print(f"Instagram Message Handling Error: {e}")
            return None

    def verify_webhook(self, hub_mode, hub_challenge, hub_verify_token):
        """
        Verify Instagram webhook
        
        :param hub_mode: Verification mode
        :param hub_challenge: Challenge string
        :param hub_verify_token: Verification token
        :return: Verification result
        """
        verify_token = os.getenv('INSTAGRAM_VERIFY_TOKEN', 'your_verify_token')
        
        if hub_mode == 'subscribe' and hub_verify_token == verify_token:
            return hub_challenge
        
        return None

# Create a global instance
instagram_handler = InstagramMessageHandler() 