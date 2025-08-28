release: cd backend && python manage.py collectstatic --noinput && python manage.py migrate --noinput
web: cd backend && gunicorn hisabpro.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 300
