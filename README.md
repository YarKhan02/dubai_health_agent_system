# WhatsApp GPT-4 Healthcare Assistant

## Project Overview
A multilingual healthcare assistant that provides smart interactions via WhatsApp, Instagram, and a website widget.

## Features
- 💬 AI-Powered Chat Assistant (GPT-4)
- 📅 Appointment Booking
- 💳 Payment Integration
- 🌐 Multi-Platform Support
- 🧑‍💼 Admin Dashboard

## Prerequisites
- Python 3.9+
- Twilio Account
- OpenAI API Key
- Stripe Account
- Google Cloud Project

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/whatsapp-health-assistant.git
cd whatsapp-health-assistant
```

2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:
- OpenAI API Key
- Twilio Credentials
- Stripe Keys
- Google Sheets Credentials

## Running the Application

### Backend Server
```bash
uvicorn main:app --reload
```

### Streamlit Dashboard
```bash
streamlit run dashboard/Home.py
```

## Configuration
- Modify services/prices in Google Sheets
- Configure bot responses in `config/responses.json`

## Deployment
- Recommended: Heroku, AWS, or DigitalOcean
- Use Gunicorn for production WSGI

## Security
- Never commit `.env` file
- Use environment-specific configurations
- Implement proper authentication for admin dashboard

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License

## Support
For issues, please open a GitHub issue or contact support@yourdomain.com 

## Services Configuration

### Overview
The project uses a flexible service configuration system that allows easy management of medical services and packages.

### Configuration File
Services are defined in `config/services.json`, which contains:
- `categories`: List of service categories
- `wellness_packages`: Comprehensive health screening packages
- `individual_tests`: Specific medical tests

### Service Management Features
The `services.py` module provides advanced methods to:
- List all service categories
- List wellness packages and individual tests
- Search services by name or description
- Filter services by category
- Find services by unique ID
- Get service prices
- Find recommended services for specific groups

### Example Usage
```python
from services import service_manager

# Get all categories
categories = service_manager.get_categories()

# Search for cancer-related services
cancer_services = service_manager.search_services("cancer")

# Get services in a specific category
wellness_packages = service_manager.get_services_by_category("Wellness Packages")

# Find services recommended for women
women_services = service_manager.get_recommended_services("Women")

# Get price of a specific service
price = service_manager.get_service_price("Basic Health Check Up")
```

### Service Metadata
Each service includes:
- Unique ID
- Name
- Price
- Turnaround Time
- Category
- Description
- Specific Tests
- Recommended Target Groups

### Updating Services
To update services:
1. Edit `config/services.json`
2. Restart the application

### Supported Operations
- Exact and partial service name lookup
- Category-based filtering
- Price retrieval
- Target group recommendations
- Detailed service information extraction

### Best Practices
- Keep service IDs unique
- Maintain consistent category names
- Update descriptions for clarity
- Regularly review and update service offerings 

## IV Therapy Services

### Overview
Our IV Therapy services provide targeted, intravenous treatments designed to address specific health and wellness needs.

### Service Types
- Multivitamin Infusions
- NAD+ Cellular Regeneration
- Immune System Boosters
- Energy and Performance Enhancement
- Beauty and Skin Health
- Personalized Wellness Treatments

### Key Features
- Rapid nutrient absorption
- Customized treatment plans
- Professional medical administration
- Targeted health benefits

### Example IV Therapy Services
- Multivitamins IV: Comprehensive nutritional support
- NAD 250mg: Cellular rejuvenation and cognitive enhancement
- Immune Boost: Strengthen immune system function
- Energy Boost: Enhance athletic performance
- Wellness VIP: Comprehensive, personalized wellness treatment

### Searching IV Therapy Services
```python
from services import service_manager

# Find all IV Therapy services
iv_therapies = service_manager.get_services_by_category("IV Therapy")

# Search for specific treatments
energy_treatments = service_manager.search_services("energy")

# Get recommended services for athletes
athlete_services = service_manager.get_recommended_services("Athletes")
```

### Pricing and Consultation
- Prices range from 450 AED to 1,450 AED
- Personalized consultation recommended
- Treatment duration varies by service

### Booking and Consultation
1. Browse available IV Therapy services
2. Consult with our medical professionals
3. Customize your treatment plan
4. Schedule your IV therapy session 