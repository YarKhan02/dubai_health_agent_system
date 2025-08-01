import json
import os
from typing import List, Dict, Optional

class ServiceManager:
    def __init__(self, config_path='config/services.json'):
        """
        Initialize ServiceManager with services configuration
        
        :param config_path: Path to services configuration JSON
        """
        config_path = os.path.join(os.path.dirname(__file__), config_path)
        
        try:
            with open(config_path, 'r') as f:
                self.services_config = json.load(f)
        except FileNotFoundError:
            print(f"Services configuration not found at {config_path}")
            self.services_config = {
                "categories": [], 
                "wellness_packages": [], 
                "individual_tests": [],
                "iv_therapies": []
            }
        except json.JSONDecodeError:
            print(f"Invalid JSON in services configuration at {config_path}")
            self.services_config = {
                "categories": [], 
                "wellness_packages": [], 
                "individual_tests": [],
                "iv_therapies": []
            }

    def get_categories(self) -> List[str]:
        """
        Retrieve all service categories
        
        :return: List of service categories
        """
        return self.services_config.get('categories', [])

    def get_wellness_packages(self) -> List[Dict]:
        """
        Retrieve all wellness packages
        
        :return: List of wellness packages
        """
        return self.services_config.get('wellness_packages', [])

    def get_individual_tests(self) -> List[Dict]:
        """
        Retrieve all individual tests
        
        :return: List of individual tests
        """
        return self.services_config.get('individual_tests', [])

    def get_iv_therapies(self) -> List[Dict]:
        """
        Retrieve all IV Therapy services
        
        :return: List of IV Therapy services
        """
        return self.services_config.get('iv_therapies', [])

    def find_service_by_id(self, service_id: str) -> Optional[Dict]:
        """
        Find a service by its unique ID across all service types
        
        :param service_id: Unique service identifier
        :return: Service details or None
        """
        # Search wellness packages
        for package in self.get_wellness_packages():
            if package.get('id') == service_id:
                return package
        
        # Search individual tests
        for test in self.get_individual_tests():
            if test.get('id') == service_id:
                return test
        
        # Search IV therapies
        for therapy in self.get_iv_therapies():
            if therapy.get('id') == service_id:
                return therapy
        
        return None

    def find_service_by_name(self, name: str) -> Optional[Dict]:
        """
        Find a service by its exact name across all service types
        
        :param name: Name of the service
        :return: Service details or None
        """
        # Search wellness packages
        for package in self.get_wellness_packages():
            if package['name'].lower() == name.lower():
                return package
        
        # Search individual tests
        for test in self.get_individual_tests():
            if test['name'].lower() == name.lower():
                return test
        
        # Search IV therapies
        for therapy in self.get_iv_therapies():
            if therapy['name'].lower() == name.lower():
                return therapy
        
        return None

    def search_services(self, query: str, category: str = None) -> List[Dict]:
        """
        Search services by partial name match and optional category
        
        :param query: Search query
        :param category: Optional category to filter results
        :return: List of matching services
        """
        query = query.lower()
        results = []
        
        # Search wellness packages
        results.extend([
            pkg for pkg in self.get_wellness_packages() 
            if (query in pkg['name'].lower() or query in pkg.get('description', '').lower())
            and (category is None or pkg.get('category') == category)
        ])
        
        # Search individual tests
        results.extend([
            test for test in self.get_individual_tests() 
            if (query in test['name'].lower() or query in test.get('description', '').lower())
            and (category is None or test.get('category') == category)
        ])
        
        # Search IV therapies
        results.extend([
            therapy for therapy in self.get_iv_therapies() 
            if (query in therapy['name'].lower() or query in therapy.get('description', '').lower())
            and (category is None or therapy.get('category') == category)
        ])
        
        return results

    def get_services_by_category(self, category: str) -> List[Dict]:
        """
        Get all services in a specific category
        
        :param category: Category name
        :return: List of services in the category
        """
        return [
            *[pkg for pkg in self.get_wellness_packages() if pkg.get('category') == category],
            *[test for test in self.get_individual_tests() if test.get('category') == category],
            *[therapy for therapy in self.get_iv_therapies() if therapy.get('category') == category]
        ]

    def get_service_price(self, name: str) -> Optional[float]:
        """
        Get price for a specific service
        
        :param name: Name of the service
        :return: Price of the service or None
        """
        service = self.find_service_by_name(name)
        return service['price'] if service else None

    def get_recommended_services(self, target_group: str) -> List[Dict]:
        """
        Find services recommended for a specific group
        
        :param target_group: Target group (e.g., 'Women', 'Men', 'Athletes')
        :return: List of recommended services
        """
        return [
            service for service in [
                *self.get_wellness_packages(), 
                *self.get_individual_tests(), 
                *self.get_iv_therapies()
            ]
            if target_group in service.get('recommended_for', [])
        ]

# Create a global service manager instance
service_manager = ServiceManager() 