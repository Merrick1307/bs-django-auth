FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ARG DATABASE_URL=postgres://user:password@localhost:5432/djanodb
ARG REDIS_URL=redis://localhost:6379/1
ARG SECRET_KEY="hjegftuyie39883yuiehkjet8yueroi03oi34uey97uodjk3080ieuuye"
ARG DEBUG=true
ENV DATABASE_URL=$DATABASE_URL \
    REDIS_URL=$REDIS_URL \
    SECRET_KEY=$SECRET_KEY \
    DEBUG=$DEBUG

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false

RUN poetry install --no-root

COPY .. .

RUN poetry run python manage.py migrate

RUN poetry run python manage.py test users

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "auth_service.wsgi:application"]