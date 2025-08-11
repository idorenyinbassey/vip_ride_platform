web: gunicorn vip_ride_platform.wsgi:application --bind 0.0.0.0:$PORT --workers 3
worker: celery -A vip_ride_platform worker -l info
beat: celery -A vip_ride_platform beat -l info
