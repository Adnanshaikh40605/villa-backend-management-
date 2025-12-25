# Villa Manager Hub - Django REST API Backend

A comprehensive Django REST API backend for managing villa bookings and reservations.

## Features

- 🔐 **JWT Authentication** - Secure token-based authentication
- 🏠 **Villa Management** - CRUD operations for villa properties
- 📅 **Booking System** - Complete booking lifecycle management
- 🔍 **Availability Checking** - Real-time villa availability validation
- 📊 **Dashboard Analytics** - Statistics and activity tracking
- 📖 **API Documentation** - Interactive Swagger/ReDoc documentation
- 🎯 **Admin Panel** - Django admin interface for data management

## Tech Stack

- **Framework**: Django 6.0
- **API**: Django REST Framework 3.14
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **CORS**: django-cors-headers

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   cd villa-backend
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   py -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   copy .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Seed database with initial data**
   ```bash
   python manage.py seed_data
   ```

   This creates:
   - Superuser: `admin@villa.com` / `admin123`
   - 4 sample villas
   - Sample bookings

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/` - Login and get JWT tokens
- `POST /api/v1/auth/refresh/` - Refresh access token
- `POST /api/v1/auth/logout/` - Logout (blacklist token)
- `GET /api/v1/auth/me/` - Get current user profile

### Villas
- `GET /api/v1/villas/` - List all villas
- `GET /api/v1/villas/{id}/` - Get villa details
- `PATCH /api/v1/villas/{id}/` - Update villa
- `GET /api/v1/villas/{id}/availability/` - Check availability

### Bookings
- `GET /api/v1/bookings/` - List bookings (with filters)
- `POST /api/v1/bookings/` - Create booking
- `GET /api/v1/bookings/{id}/` - Get booking details
- `PATCH /api/v1/bookings/{id}/` - Update booking
- `DELETE /api/v1/bookings/{id}/` - Delete booking
- `GET /api/v1/bookings/calendar/` - Calendar view

### Dashboard
- `GET /api/v1/bookings/dashboard/stats/` - Dashboard statistics
- `GET /api/v1/bookings/dashboard/today-activity/` - Today's check-ins/outs

### Documentation
- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc UI
- `GET /api/schema/` - OpenAPI schema

## Authentication

All endpoints (except login) require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Example Login Request

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@villa.com",
    "password": "admin123"
  }'
```

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/`

Login with:
- Email: `admin@villa.com`
- Password: `admin123`

## Database Models

### User
- Email-based authentication
- Custom user model with name and phone fields

### Villa
- Name, location, capacity
- Pricing and status (active/maintenance)
- Images and amenities

### Booking
- Villa reference
- Client information
- Check-in/out dates
- Payment status and booking source
- Auto-calculated total amount

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

## Deployment

### Environment Variables

Create a `.env` file with:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure PostgreSQL database
- [ ] Set up static/media file serving
- [ ] Configure CORS for production frontend
- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Set up logging and monitoring

## API Documentation

Visit `/api/docs/` for interactive API documentation with Swagger UI.

## Project Structure

```
villa-backend/
├── accounts/          # User authentication
├── villas/            # Villa management
├── bookings/          # Booking system
├── config/            # Project settings
├── manage.py
├── requirements.txt
└── README.md
```

## License

MIT License

## Support

For issues and questions, please create an issue in the repository.
