import pandas as pd
import os
from fuzzywuzzy import fuzz, process
from datetime import datetime, timedelta
import json

class HealthPackageChatbot:
    def __init__(self):
        self.excel_path = '/Users/yarkhan/Tech/dubai_health_agent_system/keys/H.xlsx'
        self.appointments_file = '/Users/yarkhan/Tech/dubai_health_agent_system/appointments.json'
        self.packages_data = self.load_excel_data()
        
    def load_excel_data(self):
        """Load all data from H.xlsx"""
        try:
            # Read both sheets
            tests_df = pd.read_excel(self.excel_path, sheet_name='CREATE YOUR OWN TESTS')
            packages_df = pd.read_excel(self.excel_path, sheet_name='HEALTH PACKAGES')
            
            # Clean and prepare data
            tests_df = tests_df.dropna(subset=['Test Name', 'Selling Price'])
            packages_df = packages_df.dropna(subset=['Package Name', 'Selling Price'])
            
            return {
                'tests': tests_df,
                'packages': packages_df
            }
        except Exception as e:
            print(f"Error loading Excel data: {e}")
            return {'tests': pd.DataFrame(), 'packages': pd.DataFrame()}
    
    def search_health_items(self, query, threshold=60):
        """Search for health tests and packages based on user query"""
        results = {'tests': [], 'packages': []}
        
        # Search in tests
        if not self.packages_data['tests'].empty:
            test_names = self.packages_data['tests']['Test Name'].astype(str).tolist()
            test_matches = process.extract(query, test_names, limit=5, scorer=fuzz.partial_ratio)
            
            for match, score in test_matches:
                if score >= threshold:
                    test_info = self.packages_data['tests'][
                        self.packages_data['tests']['Test Name'].astype(str) == match
                    ].iloc[0]
                    results['tests'].append({
                        'name': test_info['Test Name'],
                        'price': test_info['Selling Price'],
                        'score': score
                    })
        
        # Search in packages
        if not self.packages_data['packages'].empty:
            package_names = self.packages_data['packages']['Package Name'].astype(str).tolist()
            package_matches = process.extract(query, package_names, limit=5, scorer=fuzz.partial_ratio)
            
            for match, score in package_matches:
                if score >= threshold:
                    package_info = self.packages_data['packages'][
                        self.packages_data['packages']['Package Name'].astype(str) == match
                    ].iloc[0]
                    results['packages'].append({
                        'name': package_info['Package Name'],
                        'price': package_info['Selling Price'],
                        'turnaround': package_info.get('Turn Around Time', 'N/A'),
                        'score': score
                    })
        
        return results
    
    def get_all_packages_summary(self):
        """Get a summary of all available packages"""
        if self.packages_data['packages'].empty:
            return "No packages available at the moment."
        
        packages = self.packages_data['packages'].head(10)  # Show top 10 packages
        summary = "**Available Health Packages:**\n\n"
        
        for _, package in packages.iterrows():
            summary += f"**{package['Package Name']}**\n"
            summary += f"Price: AED {package['Selling Price']}\n"
            if pd.notna(package.get('Turn Around Time')):
                summary += f"⏱Duration: {package['Turn Around Time']}\n"
            summary += "\n"
        
        summary += "\n💬 *Send me a specific test name or package you're interested in for more details!*"
        return summary
    
    def generate_time_slots(self):
        """Generate available appointment time slots"""
        today = datetime.now()
        slots = []
        
        # Generate slots for next 3 days (excluding today)
        for day in range(1, 4):
            date = today + timedelta(days=day)
            day_name = date.strftime("%A")
            date_str = date.strftime("%Y-%m-%d")
            
            # Morning slots
            slots.append(f"{day_name} ({date_str}) - 9:00 AM")
            slots.append(f"{day_name} ({date_str}) - 11:00 AM")
            
            # Afternoon slots
            slots.append(f"{day_name} ({date_str}) - 2:00 PM")
            slots.append(f"{day_name} ({date_str}) - 4:00 PM")
        
        return slots[:4]  # Return only 4 slots
    
    def save_appointment(self, phone_number, package_name, time_slot):
        """Save appointment to JSON file"""
        appointment_data = {
            'phone_number': phone_number,
            'package_name': package_name,
            'time_slot': time_slot,
            'booking_time': datetime.now().isoformat(),
            'status': 'confirmed'
        }
        
        # Load existing appointments
        appointments = []
        if os.path.exists(self.appointments_file):
            try:
                with open(self.appointments_file, 'r') as f:
                    appointments = json.load(f)
            except:
                appointments = []
        
        # Add new appointment
        appointments.append(appointment_data)
        
        # Save back to file
        with open(self.appointments_file, 'w') as f:
            json.dump(appointments, f, indent=2)
        
        return appointment_data
    
    def process_message(self, message, phone_number, conversation_state=None):
        """Process incoming WhatsApp message and return appropriate response"""
        message = message.lower().strip()
        
        # Handle greeting messages
        if any(greeting in message for greeting in ['hello', 'hi', 'hey', 'start', 'مرحبا']):
            return {
                'response': self.get_welcome_message(),
                'state': 'menu'
            }
        
        # Handle appointment booking keywords
        if any(keyword in message for keyword in ['book', 'appointment', 'schedule', 'حجز']):
            return {
                'response': self.get_appointment_booking_message(),
                'state': 'selecting_package'
            }
        
        # If user is in package selection state
        if conversation_state == 'selecting_package':
            return self.handle_package_selection(message, phone_number)
        
        # If user is in time slot selection state
        if conversation_state == 'selecting_time':
            return self.handle_time_selection(message, phone_number)
        
        # Search for specific health items
        search_results = self.search_health_items(message)
        
        if search_results['tests'] or search_results['packages']:
            return {
                'response': self.format_search_results(search_results, message),
                'state': 'search_results'
            }
        
        # Default: show all packages
        return {
            'response': self.get_all_packages_summary(),
            'state': 'menu'
        }
    
    def get_welcome_message(self):
        """Get welcome message"""
        return """**Welcome to Our Healthcare Center!**
                I'm here to help you with:
                • Medical tests and health packages
                • Appointment booking
                • Pricing information

                You can:
                1. Ask about specific tests (e.g., "blood test", "vitamin D")
                2. Request health packages
                3. Book an appointment
                4. Get pricing information

                How can I assist you today?"""
    
    def get_appointment_booking_message(self):
        """Get appointment booking message with available packages"""
        packages = self.packages_data['packages'].head(8)
        message = "**Book Your Appointment**\n\n"
        message += "Please select a package from our available options:\n\n"
        
        for i, (_, package) in enumerate(packages.iterrows(), 1):
            message += f"{i}. **{package['Package Name']}** - AED {package['Selling Price']}\n"
        
        message += "\n*Reply with the package number or name you want to book.*"
        return message
    
    def handle_package_selection(self, message, phone_number):
        """Handle package selection for appointment"""
        packages = self.packages_data['packages'].head(8)
        
        # Try to match by number
        try:
            selection_num = int(message.strip())
            if 1 <= selection_num <= len(packages):
                selected_package = packages.iloc[selection_num - 1]
                time_slots = self.generate_time_slots()
                
                response = f"**Package Selected:** {selected_package['Package Name']}\n"
                response += f"**Price:** AED {selected_package['Selling Price']}\n\n"
                response += "**Available Time Slots:**\n\n"
                
                for i, slot in enumerate(time_slots, 1):
                    response += f"{i}. {slot}\n"
                
                response += "\n*Reply with the time slot number to confirm your appointment.*"
                
                return {
                    'response': response,
                    'state': 'selecting_time',
                    'selected_package': selected_package['Package Name']
                }
        except:
            pass
        
        # Try to match by name
        search_results = self.search_health_items(message)
        if search_results['packages']:
            selected_package = search_results['packages'][0]
            time_slots = self.generate_time_slots()
            
            response = f"**Package Selected:** {selected_package['name']}\n"
            response += f"**Price:** AED {selected_package['price']}\n\n"
            response += "**Available Time Slots:**\n\n"
            
            for i, slot in enumerate(time_slots, 1):
                response += f"{i}. {slot}\n"
            
            response += "\n*Reply with the time slot number to confirm your appointment.*"
            
            return {
                'response': response,
                'state': 'selecting_time',
                'selected_package': selected_package['name']
            }
        
        return {
            'response': "Sorry, I couldn't find that package. Please try again or type 'menu' to see all options.",
            'state': 'selecting_package'
        }
    
    def handle_time_selection(self, message, phone_number, selected_package=None):
        """Handle time slot selection"""
        time_slots = self.generate_time_slots()
        
        try:
            slot_num = int(message.strip())
            if 1 <= slot_num <= len(time_slots):
                selected_slot = time_slots[slot_num - 1]
                
                # Save appointment
                appointment = self.save_appointment(phone_number, selected_package, selected_slot)
                
                response = "**Appointment Confirmed!**\n\n"
                response += f"**Phone:** {phone_number}\n"
                response += f"**Package:** {selected_package}\n"
                response += f"**Time:** {selected_slot}\n"
                response += f"**Booking ID:** {appointment['booking_time'][:10]}\n\n"
                response += "Your appointment has been successfully booked!\n"
                response += "We'll contact you shortly to confirm the details.\n\n"
                response += "*Type 'menu' for more options or 'book' for another appointment.*"
                
                return {
                    'response': response,
                    'state': 'menu'
                }
        except:
            pass
        
        return {
            'response': "Invalid time slot. Please select a number from the available options.",
            'state': 'selecting_time'
        }
    
    def format_search_results(self, results, query):
        """Format search results for display"""
        response = f"🔍 **Search Results for '{query}':**\n\n"
        
        if results['packages']:
            response += "**Health Packages:**\n"
            for package in results['packages'][:3]:
                response += f"• **{package['name']}** - AED {package['price']}\n"
                if package.get('turnaround') != 'N/A':
                    response += f"Duration: {package['turnaround']}\n"
                response += "\n"
        
        if results['tests']:
            response += "**Individual Tests:**\n"
            for test in results['tests'][:3]:
                response += f"• **{test['name']}** - AED {test['price']}\n"
            response += "\n"
        
        response += "*Type 'book' to schedule an appointment or ask for more specific information!*"
        return response

# Initialize the chatbot
health_chatbot = HealthPackageChatbot()