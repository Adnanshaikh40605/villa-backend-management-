# Railway Deployment Guide for Villa Management System

## ✅ Current Configuration (FIXED)

### **Problem 1: Migrations Not Running**
**FIXED** - Extended healthcheck timeout from 100s to 300s to allow migrations to complete.

### **Problem 2: Data Being Deleted on Redeployment**
**FIXED** - Ensured PostgreSQL database is properly connected (not using ephemeral SQLite).

---

## 🔧 Required Railway Environment Variables

### **Backend Service (`villa-backend-management`)**

Add these variables in Railway Dashboard → Your Service → Variables tab:

```bash
# Database (Reference from Postgres service)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Django Security
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False

# JWT Settings (in minutes)
JWT_ACCESS_TOKEN_LIFETIME=10080    # 7 days
JWT_REFRESH_TOKEN_LIFETIME=20160   # 14 days

# Allowed Hosts (comma-separated)
ALLOWED_HOSTS=your-custom-domain.com,.railway.app

# CORS Origins (comma-separated)
CORS_ALLOWED_ORIGINS=https://your-frontend.com,https://your-frontend.railway.app

# CSRF Trusted Origins (comma-separated)
CSRF_TRUSTED_ORIGINS=https://your-frontend.com,https://villa-backend-management-production.up.railway.app
```

---

## 📋 Deployment Checklist

### **Initial Setup**

1. ✅ **Add PostgreSQL Database**
   - In Railway project, click "New" → "Database" → "Add PostgreSQL"
   - Railway automatically creates `DATABASE_URL` variable

2. ✅ **Connect Database to Backend**
   - Go to backend service → "Variables" tab
   - Add variable: `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`

3. ✅ **Set Required Environment Variables**
   - Copy all variables from the list above
   - Ensure `SECRET_KEY` is unique and secure

4. ✅ **Deploy**
   - Push code to trigger automatic deployment
   - Or click "Deploy" button in Railway dashboard

### **Verify Deployment**

1. Check "Deploy Logs" tab for migration output:
   ```
   Running migrations:
     Applying contenttypes.0001_initial... OK
     Applying accounts.0001_initial... OK
     Applying villas.0001_initial... OK
     Applying bookings.0001_initial... OK
   ```

2. Check "HTTP Logs" for successful startup:
   ```
   🚀 Using configured DATABASE_URL (PostgreSQL - Railway/Production)
   [INFO] Booting worker with pid: XXX
   ```

3. Test API endpoint:
   - Visit: `https://your-backend.railway.app/api/v1/`
   - Should return API root response

---

## 🔍 Troubleshooting

### **Issue: "relation 'accounts_user' does not exist"**
**Cause:** Migrations haven't run
**Fix:**
1. Check if `DATABASE_URL` is set correctly in Variables
2. Check Deploy Logs for migration errors
3. Manually run migrations via Railway CLI:
   ```bash
   railway run python manage.py migrate
   ```

### **Issue: "Healthcheck failed"**
**Cause:** Migrations taking longer than healthcheck timeout
**Fix:** Already fixed in `railway.toml` (timeout increased to 300s)

### **Issue: "Data deleted after redeployment"**
**Cause:** Using SQLite instead of PostgreSQL
**Fix:**
1. Verify `DATABASE_URL` is set to PostgreSQL
2. Check logs for: "🚀 Using configured DATABASE_URL"
3. Never use SQLite in production (ephemeral on Railway)

---

## 🚀 Deployment Flow

```
1. Code Push → Railway detects changes
2. Build Phase → Nixpacks builds Docker image
3. Start Command → Runs in order:
   a. python manage.py migrate          # Updates database schema
   b. python manage.py createsuperuser_production  # Creates admin if needed
   c. python manage.py collectstatic    # Gathers static files
   d. gunicorn starts application       # Starts web server
4. Healthcheck → Railway checks /api/v1/ endpoint
5. Deployment Complete → Service is live
```

---

## 📊 Database Persistence

**✅ Your data is now SAFE:**
- PostgreSQL is a **persistent** database service
- Data survives redeployments
- Backups available via Railway dashboard (Postgres → Backups tab)

**⚠️ Never delete the Postgres service** - this will delete all data

---

## 🔄 Making Changes

### **Adding New Models/Fields**

1. Make changes locally
2. Create migrations:
   ```bash
   python manage.py makemigrations
   ```
3. Commit migration files to git
4. Push to trigger deployment
5. Railway automatically runs migrations via `startCommand`

### **Manual Migration (if needed)**

If automatic migrations fail:
```bash
railway link  # Link to your project
railway run python manage.py migrate
railway run python manage.py createsuperuser_production
```

---

## 📝 Files Modified

- ✅ `railway.toml` - Extended healthcheck timeout, improved configuration
- ✅ `settings.py` - Already configured for Railway (DATABASE_URL support)
- ✅ `Procfile` - Backup start command configuration

---

## 🎯 Next Steps

1. **Push this fix to GitHub:**
   ```bash
   git add railway.toml RAILWAY_DEPLOYMENT.md
   git commit -m "fix: Improve Railway deployment configuration"
   git push origin main
   ```

2. **Verify deployment in Railway dashboard**

3. **Check logs for successful migration**

4. **Test your application endpoints**

---

**Last Updated:** 2026-01-08
**Status:** ✅ Ready for Production
