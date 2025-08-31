release: poetry run python manage.py migrate
web: gunicorn --bind 0.0.0.0:$PORT auth_service.wsgi:application