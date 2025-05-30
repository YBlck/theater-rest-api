# 🎭 theater-rest-api

**Theater API** is a RESTful service built with Django REST Framework that allows users to interact with a theater's system. The API supports operations related to actors, plays, performances, ticket reservations, and more.

## 🚀 Features

- JWT Authentication (for both admin and regular users)
- Role-based access control (admin & user)
- ViewSets for all resources
- Filtering support on Plays and Performances
- Swagger UI documentation
- Dockerized setup with PostgreSQL

## 📦 Technologies

- Python 3.11
- Django 5.2
- Django REST Framework
- djangorestframework-simplejwt
- drf-spectacular (Swagger)
- PostgreSQL
- Docker & Docker Compose

## 📚 API Overview

### Resources

- `Actor`
- `Genre`
- `Play`
- `Performance`
- `TheaterHall`
- `Reservation`
- `Ticket`
- `User` (Custom, based on `AbstractUser`)

### Available Endpoints

| Resource      | Methods                         |
|---------------|---------------------------------|
| Actor         | `GET`, `POST` (admin)           |
| Genre         | `GET`, `POST` (admin)           |
| Play          | `GET`, `POST` (admin)           |
| Performance   | `GET`, `POST`, `DELETE` (admin) |
| TheaterHall   | `GET`, `POST` (admin)           |
| Reservation   | `GET`, `POST` (user)            |
| Ticket        | Created via Reservation         |
| User          | `GET`, `POST`, `PATCH`          |

### Filtering

- `Play`: by `title`, `genres`, `actors`
- `Performance`: by `play`, `date`

### Authentication

Use JWT to access protected endpoints:

#### Obtain token

```
POST /api/token/
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

## 🐳 Setup with Docker

### 1. Clone the repository

```
git clone https://github.com/YBlck/theater-rest-api.git
cd theater-rest-api
```

### 2. Create .env file
Use the provided .env.sample to create your own .env file:
```bash
cp .env.sample .env
```
Then fill in the values:
```
DJANGO_SECRET_KEY=<your-secret-key>
POSTGRES_DB=<your_db>
POSTGRES_USER=<your_user>
POSTGRES_PASSWORD=<your_password>
POSTGRES_HOST=db
POSTGRES_PORT=5432
```
### 3. Build and run the containers
```bash
docker-compose up --build
```
The API will be available at:
```
http://localhost:8000/
```
### 4. Load initial data (optional)
If you want to prepopulate the database with sample data:
```bash
docker-compose exec theater python manage.py loaddata theater_fixture.json
```
Now you can use these credentials to get superuser access:
```
email: admin@theater.com
password: 1qazcde3
```
Or you can create your own user:
```bash
docker-compose exec theater python manage.py createsuperuser
```

### 5. Access API documentation
Swagger UI is available at:
```
http://localhost:8000/api/doc/swagger/
```
