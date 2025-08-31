# Auth Service

A Django-based REST API for user authentication, providing endpoints for registration, login, password reset, and Swagger documentation. Built with Django REST Framework (DRF) and JWT authentication, it uses PostgreSQL for data storage and Redis for caching.

- **Local Development:** Uses Docker with user-configurable PostgreSQL and Redis connections via build arguments or `Dockerfile` edits.
- **Production Deployment:** Deployed on Railway with a `Procfile`, using managed PostgreSQL and Redis services.
- **API Documentation:** Interactive Swagger UI at `/swagger/` and ReDoc at `/redoc/`.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [Local Development with Docker](#local-development-with-docker)
  - [Production Deployment on Railway](#production-deployment-on-railway)
- [Usage](#usage)
  - [Local Usage](#local-usage)
  - [Production Usage](#production-usage)
- [API Documentation](#api-documentation)
  - [Endpoints](#endpoints)
  - [Example Requests](#example-requests)
- [Project Structure](#project-structure)
- [Testing](#testing)

## Prerequisites
- **Python**: 3.11
- **Docker**: For local development
- **Poetry**: Dependency management
- **Git**: For version control
- **GitHub Account**: For Railway deployment
- **Railway Account**: For production deployment

## Setup

### Local Development with Docker
1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/bs-django-auth.git
   cd bs-django-auth
   ```

2. **Set Up Environment Variables**
   - Create `.env` in the project root:
     ```env
     # .env
     DATABASE_URL=postgres://your_user:your_password@your-db-server-addr:5432/your_db
     REDIS_URL=redis://your-redis-addr:6379/1
     SECRET_KEY=your-secret-key
     DEBUG=True
     ```
   - Replace `your_user`, `your_password`, `your_db`, `your-db-server-addr`, `your-redis-addr`,  and `your-secret-key` with your PostgreSQL credentials, database name, host db address, redis host, and a secure key.

3. **Configure Docker**
   - **Option 1: Use Build Arguments**
     Build the Docker image with your PostgreSQL and Redis connection details:
     ```bash
     docker build -t auth_service \
     --build-arg DATABASE_URL=postgres://your_user:your_password@your-db-server-addr:5432/your_db \
     --build-arg REDIS_URL=redis://your-redis-addr:6379/1 \
     --build-arg SECRET_KEY=your-secret-key \
     --build-arg DEBUG=True .
     ```
     Replace `your_user`, `your_password`, `your_db`, `your-db-server-addr`, `your-redis-addr`,  and `your-secret-key` with your values.

   - **Option 2: Edit Dockerfile**
     Modify `Dockerfile` in the project root to replace default values:
     ```dockerfile
     # Dockerfile
     FROM python:3.11-slim

     ARG DATABASE_URL=postgres://your_user:your_password@your-db-server-addr:5432/your_db
     ARG REDIS_URL=redis://your-redis-addr:6379/1
     ARG SECRET_KEY=your-secret-key
     ARG DEBUG=true

     ENV PYTHONUNBUFFERED=1 \
         PYTHONDONTWRITEBYTECODE=1 \
         DATABASE_URL=$DATABASE_URL \
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

     COPY . .

     RUN poetry run python manage.py migrate
     RUN poetry run python manage.py test users

     EXPOSE 8000

     CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "auth_service.wsgi:application"]
     ```
     - Replace `your_user`, `your_password`, `your_db`, and `your-secret-key` with your PostgreSQL credentials, database name, and a secure key.
     - Build the image:
       ```bash
       docker build -t auth_service .
       ```

4. **Run Docker**
   ```bash
   docker run -d -p 8000:8000 --env-file .env auth_service
   ```

5. **Verify Setup**
   - Access Swagger UI: `http://localhost:8000/swagger/`
   - Test registration:
     ```bash
     curl -X POST http://localhost:8000/api/register/ \
     -H "Content-Type: application/json" \
     -d '{"full_name": "John Doe", "email": "john.doe@example.com", "password": "strongpass123"}'
     ```

### Production Deployment on Railway
1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Create Railway Project**
   - Sign up/login at [railway.app](https://railway.app).
   - Click **New Project** > **Deploy from GitHub** > Select `django-auth-service`.

3. **Add Managed Services**
   - Add PostgreSQL: Click **New** > **Database** > **Add PostgreSQL** > Name: `auth-service-db`, Database: `djangodb`.
   - Add Redis: Click **New** > **Database** > **Add Redis** > Name: `auth-service-redis`.

4. **Configure Environment Variables**
   - Go to the web service > **Variables**.
   - Add:
     ```
     DATABASE_URL=<postgres-connection-string>
     REDIS_URL=<redis-connection-string>
     SECRET_KEY=<generate-a-strong-key>
     DEBUG=False
     ALLOWED_HOSTS=your-project-name.up.railway.app
     ```
     - Copy `DATABASE_URL` and `REDIS_URL` from the PostgreSQL and Redis services’ **Variables** tab.
     - Generate a secure `SECRET_KEY` (e.g., `openssl rand -hex 32`).

5. **Deploy**
   - Railway detects the `Procfile`, installs Poetry dependencies, runs `release: poetry run python manage.py migrate`, and starts `web: gunicorn --workers 3 --bind 0.0.0.0:$PORT auth_service.wsgi:application`.
   - Generate a domain in **Settings** > **Networking**.
   - Access at `https://your-project-name.up.railway.app`.

## Usage

### Local Usage
- **Run the Application:**
  ```bash
  docker build -t auth_service .
  docker run -d -p 8000:8000 --env-file .env auth_service
  ```
- **Access Swagger UI:** `http://localhost:8000/swagger/`
- **Access ReDoc:** `http://localhost:8000/redoc/`
- **Test Endpoints:** See [Example Requests](#example-requests).

### Production Usage
- **Access the Deployed App:** `https://your-project-name.up.railway.app`
- **Swagger UI:** `https://your-project-name.up.railway.app/swagger/`
- **ReDoc:** `https://your-project-name.up.railway.app/redoc/`
- **Test Endpoints:** Use `https://your-project-name.up.railway.app` as the base URL in [Example Requests](#example-requests).

## API Documentation

The API provides endpoints for user authentication, documented via Swagger UI and ReDoc.

### Endpoints
| Endpoint                  | Method | Description                     | Authentication |
|---------------------------|--------|---------------------------------|----------------|
| `/api/register/`          | POST   | Register a new user            | None           |
| `/api/login/`             | POST   | Authenticate and get JWT token | None           |
| `/api/forgot-password/`   | POST   | Request password reset         | None           |
| `/api/reset-password/`    | POST   | Reset password with token      | None           |
| `/swagger/`               | GET    | Swagger UI documentation       | None           |
| `/redoc/`                 | GET    | ReDoc documentation            | None           |

### Example Requests
1. **Register a User**
   ```bash
   curl -X POST https://your-project-name.up.railway.app/api/register/ \
   -H "Content-Type: application/json" \
   -d '{"full_name": "John Doe", "email": "john.doe@example.com", "password": "strongpass123"}'
   ```
   **Response:**
   ```json
   {"message": "Signup successful"}
   ```

2. **Login**
   ```bash
   curl -X POST https://your-project-name.up.railway.app/api/login/ \
   -H "Content-Type: application/json" \
   -d '{"email": "john.doe@example.com", "password": "strongpass123"}'
   ```
   **Response:**
   ```json
   {
       "access": "<access_token>",
       "refresh": "<refresh_token>"
   }
   ```

3. **Forgot Password**
   ```bash
   curl -X POST https://your-project-name.up.railway.app/api/forgot-password/ \
   -H "Content-Type: application/json" \
   -d '{"email": "john.doe@example.com"}'
   ```
   **Response:**
   ```json
   {"message": "Reset token generated", "token": "<generated_token>"}
   ```

4. **Reset Password**
   ```bash
   curl -X POST https://your-project-name.up.railway.app/api/reset-password/ \
   -H "Content-Type: application/json" \
   -d '{"token": "<generated_token>", "new_password": "newpass123"}'
   ```
   **Response:**
   ```json
   {"message": "Password reset successful"}
   ```

## Project Structure
```
auth_service/
├── Procfile              # Railway process definitions
├── pyproject.toml        # Poetry dependencies
├── poetry.lock           # Dependency lock file
├── manage.py             # Django management script
├── .env                  # Local environment variables
├── .env.example          # environment variables example
├── .gitignore            # Git ignore file
├── auth_service/
│   ├── __init__.py
│   ├── settings.py       # Django settings
│   ├── urls.py           # URL routing
│   ├── wsgi.py           # WSGI application
├── users/
│   ├── __init__.py
│   ├── admin.py          # Admin panel configuration
│   ├── apps.py           # App configuration
│   ├── migrations/       # Database migrations
│   ├── models.py         # User models
│   ├── serializers.py    # DRF serializers
│   ├── tests.py          # Unit tests
│   ├── urls.py           # App-specific URLs
│   ├── views.py          # API views
```

## Testing
- **Local Testing (Docker):**
  Tests are run during the Docker build process. To re-run manually:
  ```bash
  docker exec -it <container_id> poetry run python manage.py test users
  ```
  Find `<container_id>`:
  ```bash
  docker ps
  ```
  Expected output:
  ```
  Creating test database for alias 'default'...
  System check identified no issues (0 silenced).
  ......
  ----------------------------------------------------------------------
  Ran 6 tests in 0.123s
  OK
  Destroying test database for alias 'default'...
  ```

- **Production Testing:** Run tests locally or in a CI pipeline (e.g., GitHub Actions) before deployment.

---