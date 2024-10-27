---

# Edu Platform

A Django-based platform for managing and accessing educational courses, lessons, and student interactions.

## Features
- JWT Authentication for secure user access
- REST API for managing courses, lessons, and student data
- Media handling for course images and user avatars
- Admin interface for managing course content

## Getting Started

### Prerequisites
- Python 3.8 or later
- PostgreSQL
- Django
- Required Python packages in `requirements.txt`

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Bakkenti/quanta.git
   cd quanta
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory and set the following environment variables:

   ```dotenv
   SECRET_KEY=jpejIA4XIe
   DEBUG=True
   DB_NAME=railway
   DB_USER=postgres
   DB_PASSWORD=DeFgXmiYAitPpwlUgEApmvawqwhCeuNF
   DB_HOST=junction.proxy.rlwy.net
   DB_PORT=14875
   ```

5. **Database Setup:**
   Ensure PostgreSQL is installed and running. Then, create a new database or connect to an existing one using the provided environment variables.

   **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Server:**
   ```bash
   python manage.py runserver
   ```

   The application will be available at `http://127.0.0.1:8000/`.

### Usage

- Access the Django admin panel at `http://127.0.0.1:8000/admin` to manage courses, lessons, and users.
- Use the API endpoints to interact with courses, lessons, and authentication.

### API Documentation

- **Course List**: `GET /courses/`
- **Course Detail**: `GET /courses/<int:id>/<str:title>/`
- **Lesson Detail**: `GET /courses/<int:id>/<str:title>/lesson/<int:lessonid>/`
- **Signup**: `POST /signup/`
- **Login**: `POST /login/`
- **Token Refresh**: `POST /api/token/refresh/`

---

### Static and Media Files

- **Static files**: Located in the `static/` folder, served with `whitenoise`.
- **Media files**: Uploaded files (like course images) are stored in the `media/` directory.

### Additional Notes

- **JWT Tokens**: The platform uses JWT tokens for authentication. Access tokens expire after 60 minutes, while refresh tokens expire after 1 day.
- **Debug Mode**: `DEBUG=True` in `.env` is for development. For production, set `DEBUG=False` and configure `ALLOWED_HOSTS`.

---

## Deployment

For deployment, ensure to:
1. Set `DEBUG=False`.
2. Configure a production-ready database.
3. Use secure settings and review Django’s deployment checklist.

---

## License

This project is licensed under the MIT License.

