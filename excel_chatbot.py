import pandas as pd
import os
from typing import List, Dict, Optional, Union
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class ExcelBasedChatbot:
    """
    Excel-based chatbot that can answer queries from Excel files containing
    medical tests, health packages, and IV therapy services.
    """
    
    def __init__(self, excel_files_path="keys/"):
        """
        Initialize the Excel-based chatbot
        
        :param excel_files_path: Path to directory containing Excel files
        """
        self.excel_path = excel_files_path
        self.services_data = {}
        self.load_excel_data()
    
    def load_excel_data(self):
        """Load all Excel data into memory for fast querying"""
        try:
            # Load H.xlsx (Tests and Packages)
            h_file = os.path.join(self.excel_path, "H.xlsx")
            if os.path.exists(h_file):
                # Load individual tests
                tests_df = pd.read_excel(h_file, sheet_name='CREATE YOUR OWN TESTS')
                tests_df = tests_df.dropna(subset=['TEST NAME'])
                self.services_data['tests'] = tests_df.to_dict('records')
                
                # Load health packages
                packages_df = pd.read_excel(h_file, sheet_name='HEALTH PACKAGES')
                packages_df = packages_df.dropna(subset=['Package name'])
                self.services_data['packages'] = packages_df.to_dict('records')
            
            # Load IV Therap.xlsx
            iv_file = os.path.join(self.excel_path, "IV Therap.xlsx")
            if os.path.exists(iv_file):
                iv_df = pd.read_excel(iv_file, sheet_name='IV Therapy')
                iv_df = iv_df.dropna(subset=['IV Therapy'])
                self.services_data['iv_therapy'] = iv_df.to_dict('records')
            
            print(f"✅ Loaded Excel data:")
            print(f"   - Tests: {len(self.services_data.get('tests', []))}")
            print(f"   - Packages: {len(self.services_data.get('packages', []))}")
            print(f"   - IV Therapies: {len(self.services_data.get('iv_therapy', []))}")
            
        except Exception as e:
            print(f"❌ Error loading Excel data: {e}")
            self.services_data = {'tests': [], 'packages': [], 'iv_therapy': []}
    
    def search_services(self, query: str, threshold: int = 60) -> Dict:
        """
        Search for services based on user query using fuzzy matching
        
        :param query: User's search query
        :param threshold: Minimum similarity score (0-100)
        :return: Dictionary with search results
        """
        query = query.lower().strip()
        results = {
            'tests': [],
            'packages': [],
            'iv_therapy': [],
            'query': query
        }
        
        # Search in tests
        for test in self.services_data.get('tests', []):
            test_name = str(test.get('TEST NAME', '')).lower()
            score = fuzz.partial_ratio(query, test_name)
            if score >= threshold:
                results['tests'].append({
                    'name': test.get('TEST NAME'),
                    'price': test.get('Price in AED'),
                    'score': score,
                    'type': 'Individual Test'
                })
        
        # Search in packages
        for package in self.services_data.get('packages', []):
            package_name = str(package.get('Package name', '')).lower()
            score = fuzz.partial_ratio(query, package_name)
            if score >= threshold:
                results['packages'].append({
                    'name': package.get('Package name'),
                    'price': package.get('Price (AED)'),
                    'tat': package.get('TAT'),
                    'score': score,
                    'type': 'Health Package'
                })
        
        # Search in IV therapy
        for iv in self.services_data.get('iv_therapy', []):
            iv_name = str(iv.get('IV Therapy', '')).lower()
            score = fuzz.partial_ratio(query, iv_name)
            if score >= threshold:
                results['iv_therapy'].append({
                    'name': iv.get('IV Therapy'),
                    'price': iv.get('Selling Price (AED)'),
                    'score': score,
                    'type': 'IV Therapy'
                })
        
        # Sort results by score
        for category in results:
            if category != 'query' and isinstance(results[category], list):
                results[category] = sorted(results[category], key=lambda x: x.get('score', 0), reverse=True)
        
        return results
    
    def get_price_info(self, service_name: str) -> Optional[Dict]:
        """
        Get price information for a specific service
        
        :param service_name: Name of the service
        :return: Service information with price
        """
        service_name = service_name.lower().strip()
        
        # Check tests
        for test in self.services_data.get('tests', []):
            if service_name in str(test.get('TEST NAME', '')).lower():
                return {
                    'name': test.get('TEST NAME'),
                    'price': test.get('Price in AED'),
                    'type': 'Individual Test'
                }
        
        # Check packages
        for package in self.services_data.get('packages', []):
            if service_name in str(package.get('Package name', '')).lower():
                return {
                    'name': package.get('Package name'),
                    'price': package.get('Price (AED)'),
                    'tat': package.get('TAT'),
                    'type': 'Health Package'
                }
        
        # Check IV therapy
        for iv in self.services_data.get('iv_therapy', []):
            if service_name in str(iv.get('IV Therapy', '')).lower():
                return {
                    'name': iv.get('IV Therapy'),
                    'price': iv.get('Selling Price (AED)'),
                    'type': 'IV Therapy'
                }
        
        return None
    
    def get_all_services_by_category(self, category: str) -> List[Dict]:
        """
        Get all services in a specific category
        
        :param category: Category name ('tests', 'packages', 'iv_therapy')
        :return: List of services in the category
        """
        return self.services_data.get(category, [])
    
    def generate_response(self, query: str) -> str:
        """
        Generate a response based on the user's query
        
        :param query: User's query
        :return: Formatted response string
        """
        query_lower = query.lower()
        
        # Handle greeting
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return """🏥 Hello! Welcome to Dubai Health Services!

I can help you with:
📋 Medical tests and health packages
💉 IV therapy services  
💰 Price information
📅 Service details

What would you like to know about?"""
        
        # Handle price queries
        if any(word in query_lower for word in ['price', 'cost', 'how much', 'fee']):
            results = self.search_services(query)
            return self._format_price_response(results)
        
        # Handle general service search
        results = self.search_services(query)
        total_results = len(results['tests']) + len(results['packages']) + len(results['iv_therapy'])
        
        if total_results == 0:
            return f"""🔍 Sorry, I couldn't find any services matching "{query}".

Try searching for:
📋 Specific test names (e.g., "blood test", "vitamin D")
📦 Health packages (e.g., "wellness package", "cancer screening")
💉 IV therapy (e.g., "vitamin drip", "NAD therapy")

Or ask for "all tests" or "all packages" to see available options."""
        
        return self._format_search_response(results)
    
    def _format_search_response(self, results: Dict) -> str:
        """Format search results into a readable response"""
        response_parts = []
        
        # Add tests
        if results['tests']:
            response_parts.append("📋 **Individual Tests:**")
            for test in results['tests'][:5]:  # Limit to top 5
                price = test['price']
                price_text = f"AED {price}" if pd.notna(price) else "Price on request"
                response_parts.append(f"• {test['name']} - {price_text}")
        
        # Add packages
        if results['packages']:
            response_parts.append("\n📦 **Health Packages:**")
            for package in results['packages'][:5]:  # Limit to top 5
                price = package['price']
                price_text = f"AED {price}" if pd.notna(price) else "Price on request"
                tat = package.get('tat', '')
                tat_text = f" | {tat}" if tat else ""
                response_parts.append(f"• {package['name']} - {price_text}{tat_text}")
        
        # Add IV therapy
        if results['iv_therapy']:
            response_parts.append("\n💉 **IV Therapy:**")
            for iv in results['iv_therapy'][:5]:  # Limit to top 5
                price = iv['price']
                price_text = f"AED {price}" if pd.notna(price) else "Price on request"
                response_parts.append(f"• {iv['name']} - {price_text}")
        
        # Add footer
        total_results = len(results['tests']) + len(results['packages']) + len(results['iv_therapy'])
        if total_results > 15:
            response_parts.append(f"\n📞 Found {total_results} results. For complete list or booking, contact us!")
        
        response_parts.append("\n💬 Need more info? Ask about specific services!")
        
        return "\n".join(response_parts)
    
    def _format_price_response(self, results: Dict) -> str:
        """Format price-specific responses"""
        response_parts = []
        
        total_results = len(results['tests']) + len(results['packages']) + len(results['iv_therapy'])
        
        if total_results == 0:
            return "💰 Please specify which test or service you'd like pricing for."
        
        response_parts.append("💰 **Pricing Information:**\n")
        
        # Add all results with prices
        all_items = []
        all_items.extend([(item, "📋 Test") for item in results['tests']])
        all_items.extend([(item, "📦 Package") for item in results['packages']])
        all_items.extend([(item, "💉 IV Therapy") for item in results['iv_therapy']])
        
        for item, category in all_items[:8]:  # Limit to 8 items
            price = item['price']
            price_text = f"AED {price}" if pd.notna(price) else "Price on request"
            response_parts.append(f"{category} {item['name']}: {price_text}")
        
        response_parts.append("\n📞 For booking or more details, contact our team!")
        
        return "\n".join(response_parts)

# Create global instance
excel_chatbot = ExcelBasedChatbot()
