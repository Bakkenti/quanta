```markdown
# QUANTA - Educational Platform

QUANTA is an educational platform similar to Stepik, built with Django and React.
It allows users to create, manage, and enroll in courses, whileproviding a CKEditor-powered admin panel for content editing.

## Features

- 📚 **Course Management**: Create and edit courses with structured modules and lessons.
- 🎥 **Video Support**: Upload videos or use external video links.
- 📝 **Rich Text Editing**: CKEditor 5 integrated for content creation.
- 🎓 **User Roles**: Students and authors with different permissions.
- ⭐ **Reviews & Ratings**: Users can rate and review courses.
- 📊 **Best & Popular Courses**: Automatic ranking based on enrollments and ratings.
- ⚡ **React Admin Panel**: Teachers can manage content via a React-based admin interface.

---

## 🏗 Installation

### 1. Clone the Repository
```sh
git clone https://github.com/your-username/quanta.git
cd quanta
```

### 2. Create Virtual Environment & Install Dependencies
```sh
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up the Database
```sh
python manage.py migrate
```

### 4. Create a Superuser (Optional)
```sh
python manage.py createsuperuser
```

### 5. Run the Development Server
```sh
python manage.py runserver
```
The application will be available at `http://127.0.0.1:8000/`

---

## ⚙️ Configuration

### Environment Variables (`.env`)

Create a `.env` file in the root directory and configure the following settings:
```
SECRET_KEY=""
DEBUG=""
DATABASE_NAME=""
DATABASE_USER=""
DATABASE_PASSWORD=""
DATABASE_HOST=""
DATABASE_PORT=""
```

---

## 📂 Project Structure

```
quanta/
│── myapp/                 # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # Business logic
│   ├── urls.py            # URL routing
│   ├── templates/         # HTML templates
│   ├── static/            # Static files (CSS, JS)
│── media/                 # Uploaded files
│── static/                # Collected static files
│── manage.py              # Django management script
│── requirements.txt       # Python dependencies
│── .env                   # Environment variables
│── README.md              # This file
```

---

## 📜 Models Overview

### 1. `Student`
- One-to-one relation with Django's `User`
- Stores role, avatar, about info, phone number, gender
- Tracks enrolled courses

### 2. `Author`
- One-to-one relation with `User`
- Can create and manage courses

### 3. `Course`
- Has a title, description, duration, level, and author
- Linked to multiple `Module` instances

### 4. `Module`
- Belongs to a `Course`
- Contains multiple `Lesson` instances

### 5. `Lesson`
- Belongs to a `Module`
- Contains a video (either uploaded or external URL)
- Supports CKEditor for content

### 6. `Review`
- Users can rate courses from 1 to 5 stars
- Only enrolled students can leave reviews

### 7. `MostPopularCourse`
- Automatically updated based on student enrollments

### 8. `BestCourse`
- Automatically updated based on ratings and review count

### 9. `Advertisement`
- Stores ads with text, image, and optional URL link

---

## 🔧 Admin Panel (React)
The admin panel for teachers is built with **React** and allows:
- Editing lessons directly from Django using **CKEditor**
- Managing courses, modules, and lessons
- Viewing student progress

### Running the Admin Panel
```sh
python manage.py createsuperuser
```
Access it at `http://localhost:8000/`

---

## 📌 API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET`  | `/courses/` | List all courses |
| `GET`  | `/courses/<id>/` | Get course details |
| `GET`  | `/courses/<id>/<id_lesson/` | List all lessons |

> Full API documentation available in `docs/`

---

## 🚀 Deployment

### Using Gunicorn + Nginx
1. Install Gunicorn
   ```sh
   pip install gunicorn
   ```
2. Run Gunicorn server
   ```sh
   gunicorn --bind 0.0.0.0:8000 quanta.wsgi
   ```
3. Set up **Nginx** for reverse proxy (example config in `nginx.conf`)

### Using Docker (Optional)
```sh
docker-compose up --build -d
```

---

## 🔗 Technologies Used

- **Backend**: Django 5, Django REST Framework
- **Frontend**: React, TailwindCSS, CKEditor
- **Database**: PostgreSQL 
- **Authentication**: Django Auth, JWT (planned)
- **Storage**: Local `media/`
- **Deployment**: Docker, Nginx, Gunicorn

---

## 🛠 Future Plans

- ✅ Improve student progress tracking  
- ✅ Add course recommendations  
- ⏳ Implement payment system for premium courses  
- ⏳ Add quizzes and assignments  

---

## 📝 License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## 💬 Contact & Support

For questions, suggestions, or contributions:

- **Email**: baktiarlesov@example.com
- **GitHub Issues**: [Open an issue](https://github.com/Bakkeni/quanta/issues)
- **Discord**: Coming soon!

---
```
