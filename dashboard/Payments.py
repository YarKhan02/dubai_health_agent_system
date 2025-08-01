import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
import stripe

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

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
    st.title("💳 Payment Management")
    
    # Fetch payment logs from Google Sheets
    try:
        client = get_google_sheets_client()
        payments_sheet = client.open('Payment Logs').sheet1
        payments_data = payments_sheet.get_all_records()
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(payments_data)
        
        # Filters
        st.sidebar.header("Payment Filters")
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
            (pd.to_datetime(df['Timestamp']) >= pd.to_datetime(from_date)) & 
            (pd.to_datetime(df['Timestamp']) <= pd.to_datetime(to_date))
        ]
        
        # Display payments
        st.dataframe(filtered_df)
        
        # Payment summary
        st.subheader("Payment Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Payments", 
                value=len(filtered_df)
            )
        
        with col2:
            st.metric(
                label="Total Revenue", 
                value=f"AED {filtered_df['Amount'].sum():.2f}"
            )
        
        with col3:
            st.metric(
                label="Pending Payments", 
                value=len(filtered_df[filtered_df['Status'] == 'Pending'])
            )
        
        # Detailed payment actions
        st.subheader("Payment Actions")
        selected_payment = st.selectbox(
            "Select Payment", 
            filtered_df.index
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Verify Payment"):
                # Verify Stripe payment status
                session_id = filtered_df.loc[selected_payment, 'SessionID']
                try:
                    session = stripe.checkout.Session.retrieve(session_id)
                    status = session.payment_status
                    
                    # Update status in Google Sheets
                    cell = payments_sheet.find(session_id)
                    payments_sheet.update_cell(cell.row, 6, status)
                    
                    st.success(f"Payment Status: {status}")
                except Exception as e:
                    st.error(f"Verification Error: {e}")
        
        with col2:
            if st.button("Refund Payment"):
                # Initiate Stripe refund
                session_id = filtered_df.loc[selected_payment, 'SessionID']
                try:
                    session = stripe.checkout.Session.retrieve(session_id)
                    payment_intent = session.payment_intent
                    
                    refund = stripe.Refund.create(
                        payment_intent=payment_intent
                    )
                    
                    # Update status in Google Sheets
                    cell = payments_sheet.find(session_id)
                    payments_sheet.update_cell(cell.row, 6, "Refunded")
                    
                    st.warning(f"Refund Processed: {refund.id}")
                except Exception as e:
                    st.error(f"Refund Error: {e}")
    
    except Exception as e:
        st.error(f"Error loading payments: {e}")

if __name__ == "__main__":
    main() 