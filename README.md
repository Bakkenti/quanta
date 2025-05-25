# QUANTA - Educational Platform
![Quanta Logo](media/logo.png)

QUANTA is an educational platform inspired by Stepik, built with Django and React.  
It allows users to create, manage, and enroll in courses, with a CKEditor-powered admin panel for content editing and a robust REST API for frontend integration.

---

## 🚩 Features

- 📚 **Course Management:** Create and edit courses with modules and lessons  
- 🎥 **Video Support:** Upload videos or use external video links  
- 📝 **Rich Text Editing:** CKEditor 5 integration for course and blog content  
- 🎓 **User Roles:** Students and authors with different permissions  
- ⭐ **Reviews & Ratings:** Students can rate and review courses  
- 📊 **Popular & Best Courses:** Automatic ranking by enrollments and ratings  
- 📰 **Blog Module:** Authors can post articles, users can comment  
- 💬 **Comments System:** Threaded, with likes/dislikes  
- ⚡ **React Admin Panel:** Teachers manage content via a modern UI  
- 🔒 **JWT Auth & Social Login:** Secure access and easy onboarding (Google, GitHub, etc.)  
- 🔔 **Email Confirmation:** With customizable templates (multi-language support)  
- 🏆 **Featured Courses & Ads:** Highlight the best and monetize your platform  

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
│
├── main/ # Main Django app (models, views, API, admin, etc.)
│ ├── admin.py
│ ├── models.py
│ ├── serializers.py
│ ├── urls.py
│ ├── views.py
│
├── exercises/ # Exercises app (assignments, AI helper, etc.)
│ ├── admin.py
│ ├── ai_helper.py
│ ├── models.py
│ ├── serializers.py
│ ├── urls.py
│ ├── views.py
│
├── blog/ # Blog module (posts, comments)
│ ├── admin.py
│ ├── models.py
│ ├── serializers.py
│ ├── urls.py
│ ├── views.py
│
├── media/ # Uploaded user files (avatars, images, videos)
│
├── requirements.txt # Python dependencies
├── .env # Environment variables
├── manage.py # Django management script
└── 
```

---

## 📜 Models Overview

### 1. `Student`
- One-to-one relation with Django's `User`
- Stores role, avatar, about info, phone number, gender
- Tracks enrolled courses 

### 2. `Author`
- One-to-one relation with `User`
- Can create and manage courses & blog posts

### 3. `Course`
- Has a title, category, description, duration, level, and author
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

### **Course Management**

| Method | Endpoint                                                        | Description                               |
| ------ | --------------------------------------------------------------- | ----------------------------------------- |
| `GET`  | `/courses/`                                                     | List all courses                          |
| `GET`  | `/courses/<id>/`                                                | Get course details                        |
| `GET`  | `/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/` | Get lesson details                        |
| `POST` | `/courses/<id>/`                                                | Leave a review (one per course, enrolled) |

---

### **Enrollment**

| Method | Endpoint                    | Description                              |
| ------ | --------------------------- | ---------------------------------------- |
| `POST` | `/courses/<id>/enroll/`     | Enroll in a course                       |
| `POST` | `/courses/<id>/unenroll/`   | Unenroll from a course                   |
| `GET`  | `/mycourses/`               | List courses you are enrolled in         |

---

### **Blog & Comments**

| Method | Endpoint                     | Description                         |
| ------ | ---------------------------- | ----------------------------------- |
| `GET`  | `/blog/posts/`               | List blog posts                     |
| `GET`  | `/blog/posts/<id>/`          | Blog post details                   |
| `GET`  | `/blog/posts/<id>/comments/` | List comments for a post            |
| `POST` | `/blog/posts/<id>/comments/` | Add a comment (auth required)       |
| `POST` | `/blog/posts/<id>/comments/` | Reply to a comment (with parent ID) |

---

### **User/Account**

| Method | Endpoint    | Description               |
| ------ | ----------- | ------------------------- |
| `GET`  | `/profile/` | View your profile         |
| `POST` | `/login/`   | Login (returns JWT)       |
| `POST` | `/logout/`  | Logout (JWT invalidation) |
| `POST` | `/signup/`  | Register                  |

---

### **Other**

| Method | Endpoint              | Description              |
| ------ | --------------------- | ------------------------ |
| `GET`  | `/mostpopularcourse/` | Show most popular course |
| `GET`  | `/bestcourse/`        | Show best-rated course   |
| `GET`  | `/advertisement/`     | Show advertisements      |

---


## ⭐️ Quick API Usage Examples

#### Enroll in a course

```http
POST /courses/1/enroll/
Authorization: Bearer <token>
```

#### Leave a review

```http
POST /courses/1/
Content-Type: application/json
Authorization: Bearer <token>

{
  "rating": 5,
  "feedback": "Awesome!"
}
```

#### Post a blog comment

```http
POST /blog/posts/2/comments/
Content-Type: application/json
Authorization: Bearer <token>

{
  "content": "Nice article!",
  "parent": null
}
```

#### Get your enrolled courses

```http
GET /mycourses/
Authorization: Bearer <token>
```

---

## 🚀 Deployment

### Gunicorn + Nginx

```sh
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 quanta.wsgi
```

Set up **Nginx** for reverse proxy (see `nginx.conf`).

### Docker

```sh
docker-compose up --build -d
```

---

## 🔗 Technologies

* **Backend:** Django 5, Django REST Framework
* **Frontend:** React, TailwindCSS, CKEditor 5
* **Database:** PostgreSQL
* **Auth:** Django Auth, JWT, allauth (social login)
* **Media Storage:** Local `/media/`
* **Deployment:** Docker, Nginx, Gunicorn

---

## 🛠 Roadmap

* [x] Student course & profile management
* [x] Tasks in lessons (with compiler)
* [ ] Multiple language interface
* [ ] Quizzes and competitions

---

## 📝 License

MIT — see [LICENSE](LICENSE) for details.

---

## 💬 Contact & Support

* **Email:** [baktiarlesov@example.com](mailto:baktiarlesov@example.com)
* **GitHub Issues:** [Open an issue](https://github.com/Bakkeni/quanta/issues)
* **Discord:** Coming soon!
