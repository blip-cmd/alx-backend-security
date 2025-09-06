# ALX Backend Security - IP Tracking & Security System

A comprehensive Django application implementing IP tracking, geolocation analytics, rate limiting, and anomaly detection for enhanced backend security.

## 🚀 Features

- **IP Logging Middleware**: Logs all incoming requests with IP address, timestamp, and path
- **IP Blacklisting**: Block suspicious IPs with 403 Forbidden responses
- **Geolocation Analytics**: Track country and city information for each request
- **Rate Limiting**: Prevent abuse with configurable rate limits
- **Anomaly Detection**: Automated detection of suspicious activities
- **REST API**: Public API with Swagger documentation
- **Celery Integration**: Background tasks for anomaly detection

## 📋 Requirements

- Python 3.8+
- Django 5.2+
- Redis (for Celery broker)
- SQLite (default) or PostgreSQL (production)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/blip-cmd/alx-backend-security.git
cd alx-backend-security
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
IPGEOLOCATION_API_KEY=your-api-key
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Start Redis Server

```bash
# Install Redis if not already installed
# Ubuntu/Debian: sudo apt install redis-server
# macOS: brew install redis
# Windows: Download from https://redis.io/download

redis-server
```

### 7. Start Celery Worker & Beat

```bash
# Terminal 1: Start Celery worker
celery -A core worker --loglevel=info

# Terminal 2: Start Celery beat scheduler
celery -A core beat --loglevel=info
```

### 8. Run Development Server

```bash
python manage.py runserver
```

## 📱 Usage

### Access Points

- **Main Application**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/swagger/
- **Login Endpoint**: http://localhost:8000/login/

### Management Commands

#### Block an IP Address

```bash
python manage.py block_ip 192.168.1.100
```

### API Endpoints

- `POST /login/` - Login with rate limiting
- `GET /swagger/` - API documentation
- `GET /admin/` - Django admin panel

## 🏗️ Project Structure

```
alx-backend-security/
├── core/                          # Main Django project
│   ├── __init__.py               # Celery app initialization
│   ├── celery.py                 # Celery configuration
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Main URL routing
│   └── wsgi.py                   # WSGI configuration
├── ip_tracking/                   # IP tracking app
│   ├── management/commands/
│   │   └── block_ip.py           # IP blocking command
│   ├── migrations/               # Database migrations
│   ├── middleware.py             # IP logging middleware
│   ├── models.py                 # Database models
│   ├── tasks.py                  # Celery tasks
│   ├── views.py                  # API views
│   └── urls.py                   # App URL routing
├── .env.example                  # Environment variables template
├── requirements.txt              # Python dependencies
├── Procfile                      # Deployment configuration
├── manage.py                     # Django management script
└── README.md                     # This file
```

## 🔒 Security Features

### 1. IP Logging Middleware

Automatically logs all requests with:
- IP address
- Timestamp
- Request path
- Country and city (via geolocation)

### 2. IP Blacklisting

- Block malicious IPs
- Returns 403 Forbidden for blocked IPs
- Easy management through admin panel

### 3. Rate Limiting

- Anonymous users: 5 requests/minute
- Authenticated users: 10 requests/minute
- Configurable per endpoint

### 4. Anomaly Detection

Automated hourly detection of:
- IPs with >100 requests/hour
- Access to sensitive paths (/admin, /login)
- Suspicious activity patterns

### 5. Geolocation Analytics

- 24-hour caching for performance
- Country and city tracking
- Helps identify attack patterns

## 🚀 Deployment

### Deploy to Render

1. **Prepare for Production**

```bash
# Update .env for production
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
```

2. **Create Render Account**
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub repository

3. **Configure Web Service**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn core.wsgi --log-file -`
   - Add environment variables from `.env`

4. **Configure Redis Service**
   - Add Redis service on Render
   - Update `CELERY_BROKER_URL` in environment variables

5. **Configure Background Worker**
   - Create background worker service
   - Start Command: `celery -A core worker --loglevel=info`

6. **Configure Beat Scheduler**
   - Create another background worker
   - Start Command: `celery -A core beat --loglevel=info`

### Deploy to PythonAnywhere (Recommended)

1. **Upload Code**
```bash
git clone https://github.com/blip-cmd/alx-backend-security.git
cd alx-backend-security
```

2. **Install Dependencies**
```bash
pip3.10 install --user -r requirements.txt
```

3. **Configure Web App**
   - Set source code: `/home/yourusername/alx-backend-security`
   - Set WSGI file: `/home/yourusername/alx-backend-security/core/wsgi.py`

4. **Configure Static Files**
   - Static files URL: `/static/`
   - Static files directory: `/home/yourusername/alx-backend-security/staticfiles/`

5. **Run Migrations**
```bash
python manage.py migrate
python manage.py collectstatic
```

6. **Configure Celery**
   - Set up always-on task for Celery worker
   - Command: `celery -A core worker --loglevel=info`

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-production-database-url
CELERY_BROKER_URL=redis://your-redis-url
IPGEOLOCATION_API_KEY=your-api-key
```

## 🧪 Testing

### Run Tests

```bash
python manage.py test
```

### Test Rate Limiting

```bash
# Test anonymous rate limiting (5 requests/minute)
curl -X POST http://localhost:8000/login/ -d "username=test&password=test"

# Test with authentication
curl -X POST http://localhost:8000/login/ -d "username=admin&password=admin"
```

### Test IP Blocking

```bash
# Block an IP
python manage.py block_ip 127.0.0.1

# Try to access (should return 403)
curl http://localhost:8000/login/
```

## 📊 Monitoring

### Check Logs

```bash
# Django logs
tail -f logs/django.log

# Celery logs
tail -f logs/celery.log
```

### Admin Panel Monitoring

Access `/admin/` to monitor:
- Request logs
- Blocked IPs
- Suspicious IPs
- User activities

## 🔧 Configuration

### Rate Limiting

Modify in `ip_tracking/views.py`:

```python
@ratelimit(key="ip", rate="10/m", method="POST", block=True)  # 10 per minute
```

### Anomaly Detection

Modify thresholds in `ip_tracking/tasks.py`:

```python
# Change request threshold
if count > 50:  # Reduced from 100

# Add new sensitive paths
SENSITIVE_PATHS = ["/admin", "/login", "/api/sensitive"]
```

### Geolocation Caching

Modify cache timeout in `ip_tracking/middleware.py`:

```python
# Cache for 12 hours instead of 24
cache.set(cache_key, data, timeout=60 * 60 * 12)
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Celery Not Working**
   - Ensure Redis is running
   - Check CELERY_BROKER_URL in settings

2. **Geolocation Not Working**
   - Verify IPGEOLOCATION_API_KEY is set
   - Check API quota limits

3. **Rate Limiting Not Applied**
   - Ensure 'ratelimit' is in INSTALLED_APPS
   - Check RATELIMIT_ENABLE = True in settings

4. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_ROOT and STATIC_URL settings

### Getting Help

- Check the [Django documentation](https://docs.djangoproject.com/)
- Review [Celery documentation](https://docs.celeryproject.org/)
- Open an issue on GitHub

## 📞 Contact

- **Author**: ALX Backend Security Team
- **Email**: admin@example.com
- **GitHub**: [blip-cmd](https://github.com/blip-cmd)

---

**Note**: This project is part of the ALX Backend Security curriculum. Ensure you understand each component before deploying to production.