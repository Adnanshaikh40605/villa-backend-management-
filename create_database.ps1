# PowerShell script to create PostgreSQL database for local development
# Run this script before starting the Django server

Write-Host "=" -NoNewline; Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Local PostgreSQL Database Creation Script" -ForegroundColor Cyan
Write-Host "=" -NoNewline; Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Read database configuration from .env
$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "❌ Error: .env file not found at $envFile" -ForegroundColor Red
    exit 1
}

# Parse .env file
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

$dbName = if ($envVars.LOCAL_DB_NAME) { $envVars.LOCAL_DB_NAME } else { "villa_manage" }
$dbUser = if ($envVars.LOCAL_DB_USER) { $envVars.LOCAL_DB_USER } else { "postgres" }
$dbPassword = if ($envVars.LOCAL_DB_PASSWORD) { $envVars.LOCAL_DB_PASSWORD } else { "adnan12" }
$dbHost = if ($envVars.LOCAL_DB_HOST) { $envVars.LOCAL_DB_HOST } else { "localhost" }
$dbPort = if ($envVars.LOCAL_DB_PORT) { $envVars.LOCAL_DB_PORT } else { "5432" }

Write-Host "Database Configuration:" -ForegroundColor Yellow
Write-Host "  Name: $dbName"
Write-Host "  User: $dbUser"
Write-Host "  Host: $dbHost"
Write-Host "  Port: $dbPort"
Write-Host ""

# Set PostgreSQL password for this session
$env:PGPASSWORD = $dbPassword

# Check if psql is available
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlPath) {
    Write-Host "❌ Error: psql command not found. Make sure PostgreSQL is installed and in your PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Use the Python script instead:" -ForegroundColor Yellow
    Write-Host "  python create_local_database.py" -ForegroundColor Cyan
    exit 1
}

Write-Host "Checking if database '$dbName' exists..." -ForegroundColor Yellow

# Check if database exists
$checkDb = & psql -h $dbHost -p $dbPort -U $dbUser -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$dbName'" 2>&1

if ($checkDb -match "1") {
    Write-Host "✅ Database '$dbName' already exists!" -ForegroundColor Green
} else {
    Write-Host "Creating database '$dbName'..." -ForegroundColor Yellow
    
    # Create database (handle spaces by quoting)
    if ($dbName -match '\s') {
        # Database name has spaces, use quotes
        $quotedDbName = "`"$dbName`""
    } else {
        $quotedDbName = $dbName
    }
    
    $createResult = & psql -h $dbHost -p $dbPort -U $dbUser -d postgres -c "CREATE DATABASE $quotedDbName;" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database '$dbName' created successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Error creating database:" -ForegroundColor Red
        Write-Host $createResult -ForegroundColor Red
        exit 1
    }
}

# Clear password
Remove-Item Env:\PGPASSWORD

Write-Host ""
Write-Host "=" -NoNewline; Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "✅ Next steps:" -ForegroundColor Green
Write-Host "  1. Run migrations:     python manage.py migrate" -ForegroundColor White
Write-Host "  2. Create superuser:   python manage.py createsuperuser" -ForegroundColor White
Write-Host "  3. Start server:       python manage.py runserver" -ForegroundColor White
Write-Host "=" -NoNewline; Write-Host ("=" * 59) -ForegroundColor Cyan
