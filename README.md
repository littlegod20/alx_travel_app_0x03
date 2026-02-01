# alx_travel_app

The alxtravelapp project is a real-world Django application that serves as the foundation for a travel listing platform.

## Features

- RESTful API for managing travel listings and bookings
- Background task processing with Celery and RabbitMQ
- Email notifications for booking confirmations
- Payment integration with Chapa

## Setup Instructions

### Prerequisites

- Python 3.8+
- Django 5.2.7
- RabbitMQ (for Celery message broker)
- MySQL database

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd alx_travel_app_0x03
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r alx_travel_app/requirement.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root with the following variables:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   DB_NAME=your-database-name
   DB_USER=your-database-user
   DB_PASSWORD=your-database-password
   DB_HOST=localhost
   DB_PORT=3306
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-email-password
   DEFAULT_FROM_EMAIL=noreply@alxtravelapp.com
   CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
   CELERY_RESULT_BACKEND=rpc://
   ```

5. **Set up RabbitMQ:**
   
   **On Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install rabbitmq-server
   sudo systemctl start rabbitmq-server
   sudo systemctl enable rabbitmq-server
   ```
   
   **On macOS (using Homebrew):**
   ```bash
   brew install rabbitmq
   brew services start rabbitmq
   ```
   
   **On Windows:**
   - Download and install Erlang from https://www.erlang.org/downloads
   - Download and install RabbitMQ from https://www.rabbitmq.com/download.html
   - Start RabbitMQ service from Windows Services or run: `rabbitmq-server.bat`

6. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

### Running the Application

1. **Start the Django development server:**
   ```bash
   python manage.py runserver
   ```

2. **Start the Celery worker (in a separate terminal):**
   ```bash
   celery -A alx_travel_app worker --loglevel=info
   ```

3. **Start the Celery beat scheduler (optional, for periodic tasks):**
   ```bash
   celery -A alx_travel_app beat --loglevel=info
   ```

### Background Task Management

This project uses Celery with RabbitMQ for asynchronous task processing. When a booking is created, an email confirmation is sent asynchronously using a Celery task.

**Key Components:**
- `alx_travel_app/celery.py`: Celery application configuration
- `alx_travel_app/listings/tasks.py`: Contains the `send_booking_confirmation_email` shared task
- `alx_travel_app/listings/views.py`: BookingViewSet triggers the email task using `.delay()`

**Testing Background Tasks:**
1. Ensure RabbitMQ is running
2. Start the Celery worker: `celery -A alx_travel_app worker --loglevel=info`
3. Create a booking via the API
4. Check the Celery worker logs to see the email task being processed
5. Check your email (or console if using console backend) for the confirmation email

## API Documentation

This project provides a RESTful API for managing travel listings and bookings. The API is built using Django REST Framework and is documented with Swagger.

### Base URL

All API endpoints are accessible under `/api/`:

- Base API URL: `http://localhost:8000/api/`
- Swagger Documentation: `http://localhost:8000/swagger/`
- ReDoc Documentation: `http://localhost:8000/redoc/`

### Endpoints

#### Listings API

The listings API provides CRUD operations for travel accommodation listings.

**Base Endpoint:** `/api/listings/`

##### List All Listings

- **GET** `/api/listings/`
- Returns a list of all listings
- **Query Parameters:**
  - `city` (optional): Filter by city (case-insensitive partial match)
  - `country` (optional): Filter by country (case-insensitive partial match)
  - `property_type` (optional): Filter by property type (apartment, house, villa, condo, cabin, hotel, resort)
  - `max_price` (optional): Filter by maximum price per night
  - `is_active` (optional): Filter by active status (default: true)

**Example:**

```bash
GET /api/listings/?city=Paris&max_price=100
```

##### Retrieve a Specific Listing

- **GET** `/api/listings/{id}/`
- Returns details of a specific listing

##### Create a New Listing

- **POST** `/api/listings/`
- Creates a new listing
- **Request Body:**

```json
{
  "title": "Beautiful Apartment in Paris",
  "description": "A cozy apartment in the heart of Paris",
  "address": "123 Rue de la Paix",
  "city": "Paris",
  "state": "",
  "country": "France",
  "zip_code": "75001",
  "property_type": "apartment",
  "price_per_night": "150.00",
  "max_guests": 4,
  "bedrooms": 2,
  "bathrooms": 1,
  "amenities": "WiFi, Air Conditioning, Kitchen",
  "host_id": 1,
  "is_active": true
}
```

##### Update a Listing

- **PUT** `/api/listings/{id}/` - Full update
- **PATCH** `/api/listings/{id}/` - Partial update
- Updates an existing listing

##### Delete a Listing

- **DELETE** `/api/listings/{id}/`
- Deletes a listing

##### Get Bookings for a Listing

- **GET** `/api/listings/{id}/bookings/`
- Returns all bookings for a specific listing

#### Bookings API

The bookings API provides CRUD operations for reservations/bookings.

**Base Endpoint:** `/api/bookings/`

##### List All Bookings

- **GET** `/api/bookings/`
- Returns a list of all bookings
- **Query Parameters:**
  - `guest` (optional): Filter by guest ID
  - `listing` (optional): Filter by listing ID
  - `status` (optional): Filter by status (pending, confirmed, cancelled, completed)
  - `check_in_after` (optional): Filter bookings with check-in date after this date (YYYY-MM-DD)
  - `check_out_before` (optional): Filter bookings with check-out date before this date (YYYY-MM-DD)

**Example:**

```bash
GET /api/bookings/?guest=1&status=confirmed
```

##### Retrieve a Specific Booking

- **GET** `/api/bookings/{id}/`
- Returns details of a specific booking

##### Create a New Booking

- **POST** `/api/bookings/`
- Creates a new booking
- **Request Body:**

```json
{
  "listing_id": 1,
  "guest_id": 2,
  "check_in_date": "2024-06-01",
  "check_out_date": "2024-06-05",
  "number_of_guests": 2,
  "total_price": "600.00",
  "status": "pending",
  "special_requests": "Late check-in please"
}
```

**Note:** The `total_price` is automatically calculated based on the listing's price per night and the number of nights if not provided.

##### Update a Booking

- **PUT** `/api/bookings/{id}/` - Full update
- **PATCH** `/api/bookings/{id}/` - Partial update
- Updates an existing booking

##### Delete a Booking

- **DELETE** `/api/bookings/{id}/`
- Deletes a booking

### Response Format

All API responses are in JSON format. Successful responses typically return:

- **List/Retrieve:** The object(s) data
- **Create:** The created object with status code 201
- **Update:** The updated object with status code 200
- **Delete:** Empty response with status code 204

Error responses include appropriate HTTP status codes and error messages.

### Testing the API

You can test the API endpoints using:

1. **Swagger UI:** Visit `http://localhost:8000/swagger/` for an interactive API documentation and testing interface
2. **ReDoc:** Visit `http://localhost:8000/redoc/` for alternative API documentation
3. **Postman:** Import the API endpoints and test them manually
4. **cURL:** Use command-line tools to make HTTP requests

### Example cURL Commands

```bash
# Get all listings
curl -X GET http://localhost:8000/api/listings/

# Get a specific listing
curl -X GET http://localhost:8000/api/listings/1/

# Create a new listing
curl -X POST http://localhost:8000/api/listings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cozy Apartment",
    "description": "A beautiful apartment",
    "address": "123 Main St",
    "city": "New York",
    "country": "USA",
    "property_type": "apartment",
    "price_per_night": "100.00",
    "max_guests": 4,
    "bedrooms": 2,
    "bathrooms": 1,
    "host_id": 1
  }'

# Create a new booking
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": 1,
    "guest_id": 2,
    "check_in_date": "2024-06-01",
    "check_out_date": "2024-06-05",
    "number_of_guests": 2,
    "status": "pending"
  }'
```
