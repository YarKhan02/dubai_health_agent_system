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
    st.title("📅 Appointments Management")
    
    # Fetch appointments from Google Sheets
    try:
        client = get_google_sheets_client()
        appointments_sheet = client.open('Healthcare Appointments').sheet1
        appointments_data = appointments_sheet.get_all_records()
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(appointments_data)
        
        # Filters
        st.sidebar.header("Appointment Filters")
        status_filter = st.sidebar.multiselect(
            "Filter by Status", 
            options=df['Status'].unique(),
            default=df['Status'].unique()
        )
        
        # Date range filter
        from_date = st.sidebar.date_input("From Date")
        to_date = st.sidebar.date_input("To Date")
        
        # Apply filters
        filtered_df = df[
            (df['Status'].isin(status_filter)) & 
            (pd.to_datetime(df['Date']) >= pd.to_datetime(from_date)) & 
            (pd.to_datetime(df['Date']) <= pd.to_datetime(to_date))
        ]
        
        # Display appointments
        st.dataframe(filtered_df)
        
        # Appointment actions
        st.subheader("Appointment Actions")
        selected_appointment = st.selectbox(
            "Select Appointment", 
            filtered_df.index
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Confirm Appointment"):
                # Update status in Google Sheets
                cell = appointments_sheet.find(str(selected_appointment))
                appointments_sheet.update_cell(cell.row, 5, "Confirmed")
                st.success("Appointment Confirmed!")
        
        with col2:
            if st.button("Cancel Appointment"):
                # Update status in Google Sheets
                cell = appointments_sheet.find(str(selected_appointment))
                appointments_sheet.update_cell(cell.row, 5, "Cancelled")
                st.warning("Appointment Cancelled!")
    
    except Exception as e:
        st.error(f"Error loading appointments: {e}")

if __name__ == "__main__":
    main() 