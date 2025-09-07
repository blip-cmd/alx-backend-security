# Deployment Guide

## Summary of Changes Made

1. **Fixed Procfile**: Updated to use `core.wsgi:application` instead of `project.wsgi`
2. **Added render.yaml**: Complete Render.com deployment configuration
3. **Updated settings.py**: Production-ready configuration with database and cache handling
4. **Added build script**: Automated build process with migrations and static files
5. **Updated requirements.txt**: Added `dj-database-url` for database URL parsing
6. **Added health check**: Simple endpoint to verify service health

## Deployment Steps

### Option 1: Using render.yaml (Recommended)

1. Push your code to GitHub
2. Connect your GitHub repository to Render.com
3. Render will automatically detect the `render.yaml` file and configure:
   - Web service with PostgreSQL database
   - Redis instance for caching and Celery
   - Environment variables

### Option 2: Manual Render Setup

1. Create a new Web Service on Render.com
2. Connect your GitHub repository
3. Use these settings:
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn core.wsgi:application --host=0.0.0.0 --port=$PORT`
   - **Environment**: Python 3
4. Add environment variables:
   - `SECRET_KEY`: Generate a secure secret key
   - `DEBUG`: Set to `false`
   - `ALLOWED_HOSTS`: Set to your domain or `*`
   - `DATABASE_URL`: Will be provided by Render when you add a PostgreSQL database
   - `REDIS_URL`: Will be provided by Render when you add a Redis instance

### Environment Variables Required

- `SECRET_KEY`: Django secret key (auto-generated in render.yaml)
- `DEBUG`: Set to `false` for production
- `ALLOWED_HOSTS`: Your domain name or `*` for any host
- `DATABASE_URL`: PostgreSQL connection string (auto-provided by Render)
- `REDIS_URL`: Redis connection string (auto-provided by Render)

## Testing the Deployment

Once deployed, test these endpoints:
- `/health/` - Health check endpoint
- `/admin/` - Django admin
- `/swagger/` - API documentation
- `/api/v1/` - Your API endpoints

## Post-Deployment

1. Create a superuser: Use Render's shell to run `python manage.py createsuperuser`
2. Check logs for any issues
3. Monitor the health check endpoint
4. Set up your Celery workers if needed (already configured in render.yaml)

## Common Issues

1. **Static files not loading**: Ensured WhiteNoise is configured
2. **Database errors**: Check DATABASE_URL environment variable
3. **Redis connection issues**: Check REDIS_URL environment variable
4. **Module import errors**: Fixed by using correct module names (`core` instead of `project`)
