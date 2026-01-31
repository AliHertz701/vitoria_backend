# Company Website

## Overview
This project is a Django web application for a company website that showcases products, provides information about the company, and includes an admin dashboard for managing products and inquiries.

## Features
- **Product Listings**: Display a list of products with images, descriptions, and inquiry forms.
- **About Us Page**: Information about the company's mission and services.
- **Contact Us Page**: A form for users to send messages to the company.
- **Admin Dashboard**: Manage products, inquiries, and messages from users.
- **User Authentication**: Login functionality for users to access the dashboard.

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd company-website
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**:
   Open your web browser and go to `http://127.0.0.1:8000/`.

## Directory Structure
- `manage.py`: Command-line utility for interacting with the Django project.
- `README.md`: Documentation for the project.
- `requirements.txt`: List of required Python packages.
- `company_site/`: Contains the main Django project settings and configurations.
- `main/`: Contains the main application logic, including models, views, templates, and static files.
- `static/`: Contains global static assets.
- `.gitignore`: Specifies files to be ignored by Git.

## Usage Guidelines
- Ensure that you have Python and Django installed.
- Follow the setup instructions to get the application running locally.
- Use the admin dashboard to manage products and inquiries effectively.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any changes or improvements.