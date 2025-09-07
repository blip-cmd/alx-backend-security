web: gunicorn core.wsgi:application --host=0.0.0.0 --port=$PORT --log-file -
worker: celery -A core worker --loglevel=info
beat: celery -A core beat --loglevel=info
