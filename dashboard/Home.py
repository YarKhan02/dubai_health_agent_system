import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_google_sheets_client():
    """
    Authenticate and return Google Sheets client
    """
    try:
        credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_file(
            credentials_path, 
            scopes=scopes
        )
        
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Google Sheets Authentication Error: {e}")
        return None

def main():
    st.set_page_config(
        page_title="Healthcare Assistant Dashboard",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Healthcare Assistant Admin Dashboard")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to", 
        ["Dashboard", "Appointments", "Payments", "Services", "Chat Logs"]
    )
    
    # Authentication (simplified)
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username == "admin" and password == "healthcare2023!":
            st.sidebar.success("Logged in successfully!")
        else:
            st.sidebar.error("Invalid credentials")
    
    # Dashboard Overview
    if page == "Dashboard":
        st.header("Dashboard Overview")
        
        # Fetch data from Google Sheets
        try:
            client = get_google_sheets_client()
            
            # Appointments
            appointments_sheet = client.open('Healthcare Appointments').sheet1
            appointments_data = appointments_sheet.get_all_records()
            
            # Payments
            payments_sheet = client.open('Payment Logs').sheet1
            payments_data = payments_sheet.get_all_records()
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Total Appointments", 
                    value=len(appointments_data)
                )
            
            with col2:
                st.metric(
                    label="Total Revenue", 
                    value=f"AED {sum(float(payment['Amount']) for payment in payments_data):.2f}"
                )
            
            with col3:
                st.metric(
                    label="Pending Payments", 
                    value=len([p for p in payments_data if p['Status'] == 'Pending'])
                )
        
        except Exception as e:
            st.error(f"Error fetching dashboard data: {e}")
    
    # Add other pages (Appointments, Payments, etc.) similarly
    
if __name__ == "__main__":
    main() 