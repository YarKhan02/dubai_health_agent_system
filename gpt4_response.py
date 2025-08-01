import os
import openai
from dotenv import load_dotenv
from langdetect import detect
from services import service_manager  # Import service manager

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

def detect_language(text):
    """
    Detect the language of the input text
    """
    try:
        return detect(text)
    except:
        return 'en'  # Default to English if detection fails

def translate_response(text, target_language='en'):
    """
    Translate response using OpenAI API (simplified)
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Translate the following text to {target_language}"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def generate_gpt4_response(message, context=None):
    """
    Generate smart response using GPT-4
    
    :param message: User's input message
    :param context: Optional context from previous interactions or services
    :return: AI-generated response
    """
    # Detect input language
    input_language = detect_language(message)
    
    try:
        # Prepare context-aware prompt
        messages = [
            {"role": "system", "content": "You are a helpful healthcare assistant. Provide concise, accurate, and empathetic responses."},
        ]
        
        # Add service context if relevant
        service_query = service_manager.search_services(message)
        if service_query:
            context = f"Relevant Services: {', '.join([s['name'] for s in service_query])}"
        
        # Add context if available
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        
        # Add user message
        messages.append({"role": "user", "content": message})
        
        # Generate response using GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        # Extract response text
        response_text = response.choices[0].message.content.strip()
        
        # Translate if not in English
        if input_language != 'en':
            response_text = translate_response(response_text, input_language)
        
        return response_text
    
    except Exception as e:
        print(f"GPT-4 Response Error: {e}")
        return "I'm sorry, I couldn't process your request at the moment. Please try again later." 