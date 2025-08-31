release: poetry run python manage.py migrate && poetry run python manage.py collectstatic --noinput
web: gunicorn --bind 0.0.0.0:$PORT auth_service.wsgi:application