# Coderr Backend

The Coderr Backend provides the API for the Coderr platform. It enables the management of offers, orders, user profiles, and reviews. This project was developed using Django REST Framework (DRF).

## Features

- User registration & authentication
- Offer creation & management
- Order management with status updates
- Review function for business users
- API with full filtering, search, and sorting functionality

## Installation & Setup

### Requirements

- Python 3.10+
- Django 4.0
- PostgreSQL oder SQLite (for local testing)
- Virtual env(recommended for virtual environments)

### Clone project & install dependencies

```bash
git clone https://github.com/Pao040883/coderr
cd backend.Coderr
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### Run database migrations

```bash
python manage.py migrate
```

### Create superuser (Admin)

```bash
python manage.py createsuperuser
```

### Start server

```bash
python manage.py runserver
```

## API Endpoints

### Offers

GET /offers/ - List of all offers with filtering options
POST /offers/ - Create a new offer
GET /offers/{id}/ - Details of a specific offer
PATCH /offers/{id}/ - Update an offer
DELETE /offers/{id}/ - Delete an offer

### Orders

GET /orders/ - List of the user's orders
POST /orders/ - Create a new order
PATCH /orders/{id}/ - Change the status of an order (business users only)
DELETE /orders/{id}/ - Delete an order (admins only)

### User Profiles & Authentication

POST /login/ - User login
POST /registration/ - User registration
GET /profile/{id}/ - Retrieve user profile
PATCH /profile/{id}/ - Update profile

### Reviews

GET /reviews/ - List of all reviews
POST /reviews/ - Create a review
PATCH /reviews/{id}/ - Edit a review
DELETE /reviews/{id}/ - Delete a review

## Authentication

The API uses token authentication.
After logging in, the user receives a token that must be sent in the headers with requests:

```json
{
  "Authorization": "Token <your-token>"
}
```

## Author

This project was developed by Patrick Offermanns.