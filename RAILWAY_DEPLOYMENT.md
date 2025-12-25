# Railway Deployment Guide

## Environment Variables Setup

To deploy your Django application to Railway, you need to configure the following environment variables in your Railway project settings:

### Required Environment Variables

1. **DATABASE_URL** (Automatically provided by Railway PostgreSQL)
   ```
   postgresql://postgres:TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa@postgres.railway.internal:5432/railway
   ```
   > **Note:** Railway automatically sets this when you add a PostgreSQL database to your project.

2. **SECRET_KEY** (Generate a new one for production)
   ```
   your-production-secret-key-here
   ```
   > **Important:** Use a strong, unique secret key. You can generate one using:
   > ```python
   > python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   > ```

3. **DEBUG**
   ```
   False
   ```
   > **Important:** Always set to `False` in production.

4. **ALLOWED_HOSTS**
   ```
   .railway.app,your-custom-domain.com
   ```
   > Add your Railway domain and any custom domains you're using.

5. **CORS_ALLOWED_ORIGINS**
   ```
   https://your-frontend-domain.com,https://your-frontend.railway.app
   ```
   > Add your frontend application URLs.

### Optional Environment Variables

6. **JWT_ACCESS_TOKEN_LIFETIME** (default: 60 minutes)
   ```
   60
   ```

7. **JWT_REFRESH_TOKEN_LIFETIME** (default: 10080 minutes / 7 days)
   ```
   10080
   ```

## How to Set Environment Variables in Railway

1. Go to your Railway project dashboard
2. Select your Django service
3. Click on the **Variables** tab
4. Click **+ New Variable**
5. Add each variable name and value
6. Click **Add** to save

## Database Connection Details

Your PostgreSQL database credentials:

- **Host (Internal):** `postgres.railway.internal`
- **Port:** `5432`
- **Database:** `railway`
- **Username:** `postgres`
- **Password:** `TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa`

**Public Connection URL (for external access):**
```
postgresql://postgres:TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa@turntable.proxy.rlwy.net:57771/railway
```

**Internal Connection URL (for Railway services):**
```
postgresql://postgres:TfJvwkrSvCryRtkKuTelBBbEWDLWrhOa@postgres.railway.internal:5432/railway
```

> **Note:** Railway automatically sets the `DATABASE_URL` environment variable when you add a PostgreSQL database.

## Deployment Steps

1. **Install dependencies locally** (optional, for testing):
   ```bash
   pip install -r requirements.txt
   ```

2. **Commit and push your changes:**
   ```bash
   git add .
   git commit -m "Fix Railway deployment: Update Pillow version and add missing dependencies"
   git push origin main
   ```

3. **Railway will automatically:**
   - Detect the changes
   - Install dependencies from `requirements.txt`
   - Run migrations: `python manage.py migrate`
   - Start the server: `gunicorn config.wsgi:application`

## Troubleshooting

### Build Fails with Pillow Error
- **Solution:** Updated `requirements.txt` to use Pillow 11.0.0 (compatible with Python 3.13)

### Database Connection Error
- **Solution:** Ensure `DATABASE_URL` environment variable is set in Railway
- **Check:** Railway PostgreSQL service is running and linked to your Django service

### Static Files Not Loading
- **Solution:** Run `python manage.py collectstatic` during deployment
- **Check:** `STATIC_ROOT` is properly configured in `settings.py`

## Post-Deployment Tasks

After successful deployment, you may need to:

1. **Create a superuser** (via Railway CLI or shell):
   ```bash
   railway run python manage.py createsuperuser
   ```

2. **Collect static files** (if not done automatically):
   ```bash
   railway run python manage.py collectstatic --noinput
   ```

3. **Run migrations** (if not done automatically):
   ```bash
   railway run python manage.py migrate
   ```

## Monitoring

- Check deployment logs in Railway dashboard
- Monitor application health at: `https://your-app.railway.app/admin/`
- API documentation: `https://your-app.railway.app/api/schema/swagger-ui/`
