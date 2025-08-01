import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List

class HealthcareDatabase:
    def __init__(self, db_path='healthcare.db'):
        """
        Initialize database connection
        
        :param db_path: Path to SQLite database file
        """
        # Ensure the database is in the project directory
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.conn = None
        self.cursor = None
        self._create_tables()

    def _connect(self):
        """
        Establish database connection
        """
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

    def _close(self):
        """
        Close database connection
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def _create_tables(self):
        """
        Create necessary tables if they don't exist
        """
        self._connect()
        
        # Appointments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT,
                service TEXT,
                date TEXT,
                time TEXT,
                status TEXT DEFAULT 'Pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Payments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT,
                service TEXT,
                amount REAL,
                status TEXT DEFAULT 'Pending',
                session_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chat logs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT,
                message TEXT,
                response TEXT,
                direction TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self._close()

    def save_appointment(self, phone_number: str, service: str, date: str, time: str) -> int:
        """
        Save an appointment to the database
        
        :param phone_number: User's phone number
        :param service: Service type
        :param date: Appointment date
        :param time: Appointment time
        :return: Appointment ID
        """
        self._connect()
        
        try:
            self.cursor.execute('''
                INSERT INTO appointments 
                (phone_number, service, date, time) 
                VALUES (?, ?, ?, ?)
            ''', (phone_number, service, date, time))
            
            self.conn.commit()
            appointment_id = self.cursor.lastrowid
            return appointment_id
        
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        
        finally:
            self._close()

    def save_payment(self, phone_number: str, service: str, amount: float, session_id: str) -> int:
        """
        Save a payment to the database
        
        :param phone_number: User's phone number
        :param service: Service paid for
        :param amount: Payment amount
        :param session_id: Stripe session ID
        :return: Payment ID
        """
        self._connect()
        
        try:
            self.cursor.execute('''
                INSERT INTO payments 
                (phone_number, service, amount, session_id) 
                VALUES (?, ?, ?, ?)
            ''', (phone_number, service, amount, session_id))
            
            self.conn.commit()
            payment_id = self.cursor.lastrowid
            return payment_id
        
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        
        finally:
            self._close()

    def log_chat(self, phone_number: str, message: str, response: str, direction: str = 'incoming') -> int:
        """
        Log chat interactions
        
        :param phone_number: User's phone number
        :param message: User's message
        :param response: Bot's response
        :param direction: Message direction (incoming/outgoing)
        :return: Chat log ID
        """
        self._connect()
        
        try:
            self.cursor.execute('''
                INSERT INTO chat_logs 
                (phone_number, message, response, direction) 
                VALUES (?, ?, ?, ?)
            ''', (phone_number, message, response, direction))
            
            self.conn.commit()
            log_id = self.cursor.lastrowid
            return log_id
        
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        
        finally:
            self._close()

    def get_appointments(self, phone_number: str = None, status: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve appointments with optional filtering
        
        :param phone_number: Optional phone number to filter
        :param status: Optional status to filter
        :return: List of appointments
        """
        self._connect()
        
        try:
            query = "SELECT * FROM appointments WHERE 1=1"
            params = []
            
            if phone_number:
                query += " AND phone_number = ?"
                params.append(phone_number)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            self.cursor.execute(query, params)
            columns = [column[0] for column in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        
        finally:
            self._close()

    def update_appointment_status(self, appointment_id: int, status: str) -> bool:
        """
        Update appointment status
        
        :param appointment_id: ID of the appointment
        :param status: New status
        :return: Success status
        """
        self._connect()
        
        try:
            self.cursor.execute('''
                UPDATE appointments 
                SET status = ? 
                WHERE id = ?
            ''', (status, appointment_id))
            
            self.conn.commit()
            return self.cursor.rowcount > 0
        
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        
        finally:
            self._close()

# Create a global database instance
db = HealthcareDatabase() 