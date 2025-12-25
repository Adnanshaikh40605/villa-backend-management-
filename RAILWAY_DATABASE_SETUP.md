# Railway PostgreSQL Database Setup Guide

## Step 1: Create PostgreSQL Database on Railway

1. Go to [Railway.app](https://railway.app/)
2. Create a new project or select existing project
3. Click "+ New" → "Database" → "Add PostgreSQL"
4. Railway will provision a PostgreSQL database

## Step 2: Get Database Credentials

1. Click on your PostgreSQL database in Railway
2. Go to "Variables" tab
3. Copy the `DATABASE_URL` value
   - It will look like: `postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway`

## Step 3: Configure Django Backend

### For Local Development (keep using SQLite):
- No changes needed
- Django will use SQLite by default

### For Railway Deployment:
1. In Railway, go to your Django service
2. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: (paste the PostgreSQL DATABASE_URL from Step 2)

3. Add other required environment variables:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-railway-domain.up.railway.app
   CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
   ```

## Step 4: Run Migrations on Railway

After deploying to Railway, run migrations:

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Step 5: Test Connection

Your Django app will now use:
- **Local**: SQLite (db.sqlite3)
- **Railway**: PostgreSQL (from DATABASE_URL)

## Database Models

Your database includes:

### 1. User Model (accounts app)
- Custom user with email authentication
- Fields: email, name, phone, password

### 2. Villa Model (villas app)
- name, location, max_guests, price_per_night
- status (active/maintenance)
- image, description, amenities
- timestamps

### 3. Booking Model (bookings app)
- villa (ForeignKey to Villa)
- client_name, client_phone, client_email
- check_in, check_out dates
- status (booked/blocked)
- number_of_guests, notes
- payment_status, booking_source
- total_amount (auto-calculated)
- created_by (ForeignKey to User)
- timestamps

## Migrations

All migrations are already created. When you deploy to Railway, just run:
```bash
python manage.py migrate
```

This will create all tables in PostgreSQL automatically!
