import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db

def main():
    st.title("💬 Chat Logs")
    
    # Fetch chat logs from SQLite database
    try:
        # Connect to database and fetch logs
        conn = db._connect()
        cursor = db.cursor
        
        # Fetch chat logs
        cursor.execute("SELECT * FROM chat_logs ORDER BY created_at DESC")
        columns = [column[0] for column in cursor.description]
        chat_logs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Convert to DataFrame
        df = pd.DataFrame(chat_logs)
        
        # Filters
        st.sidebar.header("Chat Log Filters")
        
        # Phone number filter
        phone_numbers = df['phone_number'].unique()
        selected_phone = st.sidebar.selectbox(
            "Filter by Phone Number", 
            options=['All'] + list(phone_numbers)
        )
        
        # Direction filter
        direction_filter = st.sidebar.multiselect(
            "Filter by Direction", 
            options=df['direction'].unique(),
            default=df['direction'].unique()
        )
        
        # Apply filters
        filtered_df = df[
            ((selected_phone == 'All') or (df['phone_number'] == selected_phone)) &
            (df['direction'].isin(direction_filter))
        ]
        
        # Display filtered logs
        st.dataframe(filtered_df)
        
        # Detailed log view
        st.subheader("Detailed Chat Log")
        selected_log = st.selectbox(
            "Select a Chat Log", 
            filtered_df.index
        )
        
        # Display selected log details
        if selected_log is not None:
            log_details = filtered_df.loc[selected_log]
            st.json(log_details.to_dict())
    
    except Exception as e:
        st.error(f"Error loading chat logs: {e}")
    
    finally:
        # Close database connection
        db._close()

if __name__ == "__main__":
    main() 