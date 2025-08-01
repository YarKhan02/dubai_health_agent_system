import os
from datetime import datetime
from dotenv import load_dotenv
from database import db  # Import the database module

# Load environment variables
load_dotenv()

def save_appointment(phone_number, message):
    """
    Save appointment details to SQLite database
    
    :param phone_number: User's phone number
    :param message: Message containing appointment details
    :return: Appointment confirmation details
    """
    try:
        # Simplified parsing - you'd want more robust parsing in production
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M")
        service = "General Consultation"  # Default service
        
        # Save to database
        appointment_id = db.save_appointment(
            phone_number=phone_number, 
            service=service, 
            date=date, 
            time=time
        )
        
        if appointment_id:
            return f"Appointment booked for {date} at {time} (ID: {appointment_id})"
        else:
            return "Unable to book appointment. Please try again."
    
    except Exception as e:
        print(f"Appointment Booking Error: {e}")
        return "Unable to book appointment. Please try again."

def get_available_appointments(phone_number=None):
    """
    Retrieve available appointments from database
    
    :param phone_number: Optional phone number to filter
    :return: List of available appointments
    """
    try:
        # Fetch appointments with optional filtering
        appointments = db.get_appointments(
            phone_number=phone_number, 
            status='Pending'
        )
        
        return appointments
    
    except Exception as e:
        print(f"Fetching Available Appointments Error: {e}")
        return []

def update_appointment_status(appointment_id, status):
    """
    Update appointment status in the database
    
    :param appointment_id: ID of the appointment
    :param status: New status
    :return: Success status
    """
    try:
        return db.update_appointment_status(appointment_id, status)
    
    except Exception as e:
        print(f"Updating Appointment Status Error: {e}")
        return False 