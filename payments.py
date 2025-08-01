import os
import stripe
from dotenv import load_dotenv
from database import db  # Import the database module
from services import service_manager  # Import service manager

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_payment_link(phone_number, service_name=None):
    """
    Create a dynamic Stripe payment link
    
    :param phone_number: User's phone number
    :param service_name: Optional service name to fetch price
    :return: Payment link URL
    """
    try:
        # Find service price using service manager
        if not service_name:
            service_name = "Basic Health Check Up"  # Default service
        
        service = service_manager.find_service_by_name(service_name)
        
        if not service:
            return "Unable to find the specified service."
        
        service_price = service['price']
        
        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'aed',
                    'unit_amount': service_price * 100,  # Convert to cents
                    'product_data': {
                        'name': service_name,
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://yourdomain.com/payment/success',
            cancel_url='https://yourdomain.com/payment/cancel',
            metadata={
                'phone_number': phone_number,
                'service': service_name
            }
        )
        
        # Log payment attempt in database
        payment_id = db.save_payment(
            phone_number=phone_number, 
            service=service_name, 
            amount=service_price, 
            session_id=checkout_session.id
        )
        
        return checkout_session.url
    
    except Exception as e:
        print(f"Payment Link Creation Error: {e}")
        return "Unable to generate payment link. Please try again."

def verify_payment(session_id):
    """
    Verify payment status
    
    :param session_id: Stripe Checkout Session ID
    :return: Payment status
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Update payment status in database
        # This is a placeholder - implement based on your database schema
        
        return session.payment_status == 'paid'
    
    except Exception as e:
        print(f"Payment Verification Error: {e}")
        return False 