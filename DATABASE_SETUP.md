# Database Configuration Guide

This project supports two database configurations:
1. **Local Development**: PostgreSQL database (villa_manage)
2. **Production/Railway**: Railway PostgreSQL database

## Local Development Setup

### Prerequisites
- PostgreSQL installed and running locally
- Database created: `villa_manage` (or `villa manage` if your database has spaces)

### Configuration
The `.env` file is already configured for local development:

```env
USE_LOCAL_DB=True
LOCAL_DB_NAME=villa_manage
LOCAL_DB_USER=postgres
LOCAL_DB_PASSWORD=adnan12
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5432
```

**Note**: If your database name has spaces (e.g., "villa manage"), Django will handle it automatically. However, underscores are preferred for database names.

### Create the Database (if not exists)
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE "villa_manage";

-- Or if your database name has spaces:
CREATE DATABASE "villa manage";
```

### Run Migrations
```bash
cd villa-backend
python manage.py migrate
python manage.py createsuperuser
```

## Production/Railway Setup

### Configuration
When deploying to Railway:

1. **Comment out** local database settings in `.env`:
   ```env
   # USE_LOCAL_DB=True
   ```

2. **Uncomment** and set `DATABASE_URL` (Railway automatically provides this):
   ```env
   DATABASE_URL=postgresql://postgres:TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa@turntable.proxy.rlwy.net:57771/railway
   ```

3. **Set in Railway Environment Variables**:
   - Railway automatically sets `DATABASE_URL` when you link a PostgreSQL service
   - Or manually set: `DATABASE_URL` = `postgresql://postgres:TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa@turntable.proxy.rlwy.net:57771/railway`

### Railway Database Credentials
From `villa-backend/db credentials`:
- **Public URL**: `postgresql://postgres:TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa@turntable.proxy.rlwy.net:57771/railway`
- **Internal URL**: `postgresql://postgres:TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa@postgres.railway.internal:5432/railway`
- **Username**: `postgres`
- **Password**: `TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa`
- **Database**: `railway`

## How It Works

The `settings.py` file automatically detects which database to use:

1. **If `DATABASE_URL` is set and `USE_LOCAL_DB=False`**:
   - Uses Railway/Production PostgreSQL from `DATABASE_URL`

2. **If `USE_LOCAL_DB=True`**:
   - Uses local PostgreSQL with credentials from `.env`

3. **If neither is configured and `DEBUG=True`**:
   - Falls back to SQLite (development only)

4. **If neither is configured and `DEBUG=False`**:
   - Exits with error (prevents accidental production issues)

## Switching Between Databases

### Switch from Local to Railway
1. Edit `.env`:
   ```env
   # USE_LOCAL_DB=True  # Comment this out
   DATABASE_URL=postgresql://postgres:TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa@turntable.proxy.rlwy.net:57771/railway
   ```

2. Restart Django server

### Switch from Railway to Local
1. Edit `.env`:
   ```env
   USE_LOCAL_DB=True
   # DATABASE_URL=...  # Comment this out or remove
   ```

2. Restart Django server

## Troubleshooting

### Connection Refused
- **Local**: Check if PostgreSQL is running: `pg_ctl status` or check services
- **Railway**: Verify `DATABASE_URL` is set correctly in Railway environment variables

### Authentication Failed
- Check username and password in `.env` file
- Verify database user has proper permissions

### Database Does Not Exist
- Create the database manually:
  ```sql
  CREATE DATABASE villa_manage;
  ```
- Or let Django create it (if user has CREATE DATABASE permission)

### Migrations Not Running
- Run manually: `python manage.py migrate`
- Check database connection first: `python manage.py check --database default`
