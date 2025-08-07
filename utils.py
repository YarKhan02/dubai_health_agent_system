import os
import re
from twilio.request_validator import RequestValidator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_phone_number(phone_number):
    """
    Validate and standardize phone number format
    
    :param phone_number: Phone number to validate
    :return: Standardized phone number or None
    """
    # Remove all non-digit characters
    cleaned_number = re.sub(r'\D', '', phone_number)
    
    # Check for valid UAE phone number formats
    if cleaned_number.startswith('971') and len(cleaned_number) == 12:
        return f"+{cleaned_number}"
    elif cleaned_number.startswith('0') and len(cleaned_number) == 10:
        return f"+971{cleaned_number[1:]}"
    elif len(cleaned_number) == 9:
        return f"+971{cleaned_number}"
    
    return None

def validate_twilio_request(request, form_data):
    """
    Validate incoming Twilio webhook request
    
    :param request: FastAPI request object
    :return: Boolean indicating request validity
    """
    try:
        # Get Twilio signature and URL
        signature = request.headers.get('X-Twilio-Signature', '')
        url = request.url._url
        
        # Get form data
        # form_data = request.form()
        
        # Initialize Twilio validator
        validator = RequestValidator(os.getenv('TWILIO_AUTH_TOKEN'))
        
        # Validate request
        return validator.validate(url, dict(form_data), signature)
    
    except Exception as e:
        print(f"Twilio Request Validation Error: {e}")
        return False

def sanitize_message(message):
    """
    Sanitize and clean user input message
    
    :param message: Raw user input message
    :return: Cleaned message
    """
    # Remove extra whitespaces
    message = ' '.join(message.split())
    
    # Remove potentially harmful characters/scripts
    message = re.sub(r'[<>]', '', message)
    
    # Limit message length
    return message[:500]

def generate_unique_id(prefix=''):
    """
    Generate a unique identifier
    
    :param prefix: Optional prefix for the ID
    :return: Unique identifier string
    """
    import uuid
    
    unique_id = str(uuid.uuid4()).replace('-', '')[:12]
    return f"{prefix}{unique_id}" if prefix else unique_id

def log_interaction(phone_number, message_type, content):
    """
    Log user interactions
    
    :param phone_number: User's phone number
    :param message_type: Type of interaction (e.g., 'incoming', 'outgoing')
    :param content: Message content
    """
    try:
        import json
        from datetime import datetime
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'phone_number': phone_number,
            'type': message_type,
            'content': content
        }
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Append to log file
        with open('logs/whatsapp_log.json', 'a') as log_file:
            json.dump(log_entry, log_file)
            log_file.write('\n')
    
    except Exception as e:
        print(f"Interaction Logging Error: {e}") 