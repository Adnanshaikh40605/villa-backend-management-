# Local Database Setup Guide

## ✅ Quick Setup (One-Time)

### Step 1: Create the Database
Run this command once to create the local PostgreSQL database:

```powershell
cd villa-backend
py create_local_database.py
```

Or use PowerShell script:
```powershell
.\create_database.ps1
```

### Step 2: Run Migrations
Apply database migrations:

```powershell
py manage.py migrate
```

### Step 3: Create Superuser (Optional)
Create an admin user:

```powershell
py manage.py createsuperuser
```

### Step 4: Start Server
Start the Django development server:

```powershell
py manage.py runserver
```

## Database Configuration

The database is configured in `.env`:

```env
USE_LOCAL_DB=True
LOCAL_DB_NAME=villa_manage
LOCAL_DB_USER=postgres
LOCAL_DB_PASSWORD=adnan12
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5432
```

## Troubleshooting

### Database Already Exists
If you see "Database already exists" - that's fine! The database is ready to use.

### Connection Refused
- Make sure PostgreSQL is running
- Check if PostgreSQL service is started (Windows: Services app)
- Verify host, port, username, and password in `.env`

### Database Name with Spaces
If your database name has spaces (e.g., "villa manage"), the script handles it automatically.
However, it's recommended to use underscores (villa_manage) instead.

### Migrations Already Applied
If migrations fail saying they're already applied, that's normal if you've run them before.
The database is ready to use.

## Production (Railway) Setup

When deploying to Railway:
1. Comment out `USE_LOCAL_DB=True` in `.env`
2. Uncomment `DATABASE_URL` in Railway environment variables
3. Railway will use the production PostgreSQL database
