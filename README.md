# QUANTA - Educational Platform
![Quanta Logo](media/images/logo.png)

QUANTA is an educational platform, built with Django and React.  
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
EMAIL_HOST_USER=""
EMAIL_HOST_PASSWORD=""
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

#### **GET /mycourses/**

**Response:**

```json
{
        "id": 1,
        "title": "Python",
        "category": "Programming",
        "course_image": "/media/course_images/python.png",
        "author": "Bakkenti",
        "description": "Master the fundamentals of programming with Python!",
        "duration": "2 weeks",
        "level": "all",
        "students": 1
}
```

### **User/Account**

| Method  | Endpoint         | Description               |
|---------|------------------|---------------------------|
| `POST`  | `/signup/`       | Register                  |
| `POST`  | `/login/`        | Login (returns JWT)       |
| `POST`  | `/logout/`       | Logout (JWT invalidation) |
| `GET`   | `/profile/`      | View your profile         |
| `PATCH` | `/profile/edit/` | Edit your profile         |

#### **POST /signup/**

**Request Body:**

```json
{
  "username": "Guest",
  "email": "example@gmail.com",
  "password": "123guest"
}
```

#### **POST /login/**

**Request Body:**

```json
{
  "username/email": "Guest/example@gmail.com",
  "password": "123guest"
}
```

**Response:**

```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI",
    "refresh": "",
    "user": {
        "pk": 1,
        "username": "Guest",
        "email": "example@gmail.com"
    },
    "access_expiration": "2025-05-26T04:31:32.815526Z",
    "refresh_expiration": "2025-05-27T01:31:32.815526Z"
}
```



#### **GET /profile/**

**Response:**

```json
{
    "username": "Bakhtiyar",
    "email": "baktiar@gmail.com",
    "avatar": null,
    "role": "student/author/journalist",
    "is_journalist": true,
    "about": "Updated about info",
    "birthday": "2000-01-01",
    "gender": "M",
    "phone_number": "+77071234567",
    "enrolled_courses": {
        "1": "Python"
    }
}
```

#### **PATCH /profile/edit/**

**Request Body:**

```json
{
    "email": "baktiar@gmail.com",
    "avatar": null,
    "about": "Updated about info",
    "birthday": "2000-01-01",
    "phone_number": "+77071234567",
    "gender": "Male/Female/Other"
}
```
---

Вот как это лучше всего оформить для README, полностью в твоем стиле и с примерами (таблицами, запросами, примерами response/request):

---

### **Author/Journalist Applications**

| Method | Endpoint                    | Description                                               |
| ------ | --------------------------- | --------------------------------------------------------- |
| `POST` | `/author/apply-author/`     | Apply to become a course author                           |
| `POST` | `/author/apply-journalist/` | Apply to become a journalist (blog author)                |
| `GET`  | `/author/applies-status/`   | View your current application statuses                    |
| `POST` | `/author/withdraw/<role>/`  | Withdraw an active application ("author" or "journalist") |

---

#### **POST /author/apply-author/**

**Response:**

```json
{
  "message": "Your application to become a course author has been submitted. Please wait for review."
}
```

*If already pending or approved:*

```json
{
  "message": "You are already approved as a course author."
}
```

---

#### **POST /author/apply-journalist/**


**Response:**

```json
{
  "message": "Your application to become a journalist has been submitted. Please wait for review."
}
```

*If already pending or approved:*

```json
{
  "message": "You are already approved as a journalist."
}
```

---

#### **GET /author/applies-status/**

**Response:**

```json
{
  "author_status": "pending",      // "none", "pending", "approved", "rejected"
  "author_reject_reason": "",      // Reason for rejection, if any
  "journalist_status": "approved", // "none", "pending", "approved", "rejected"
  "journalist_reject_reason": ""   // Reason for rejection, if any
}
```

**Status values:**

* `none` — no application
* `pending` — under review
* `approved` — approved, you have this role
* `rejected` — rejected (see reason)

---

#### **POST /author/withdraw/<role>/**

**Params:**
`<role>` — either `"author"` or `"journalist"`

**Response (success):**

```json
{
  "message": "Your course author / journalist application has been withdrawn."
}
```

**Response (no active application):**

```json
{
  "message": "There is no pending course author application to withdraw."
}
```

```json
{
  "message": "There is no pending journalist application to withdraw."
}
```

---

#### **Notes**

* Only `pending` applications can be withdrawn. If application is already approved or rejected, use the endpoints above to view status and reason.
* After approval, your role (`is_author`/`is_journalist`) will be updated and new features/pages will become available in your UI.

---

**Example Flow:**

1. **Apply:**
   `POST /author/apply-author/`
   → Response: Application submitted
2. **Check status:**
   `GET /author/applies-status/`
   → Response: Status is `"pending"`
3. **Withdraw:**
   `POST /author/withdraw/author/`
   → Response: Application withdrawn

---

### **Author Course Endpoints**

| Method   | Endpoint                                                               | Description                            |
| -------- | ---------------------------------------------------------------------- | -------------------------------------- |
| `GET`    | `/author/courses/`                                                     | List all courses created by the author |
| `POST`   | `/author/courses/`                                                     | Create a new course                    |
| `GET`    | `/author/courses/<course_id>/`                                         | Get details of a specific course       |
| `PATCH`  | `/author/courses/<course_id>/`                                         | Update a specific course               |
| `DELETE` | `/author/courses/<course_id>/`                                         | Delete a specific course               |
|          |                                                                        |                                        |
| `GET`    | `/author/courses/<course_id>/modules/`                                 | List all modules in a course           |
| `POST`   | `/author/courses/<course_id>/modules/`                                 | Create a new module in a course        |
| `GET`    | `/author/courses/<course_id>/modules/<module_id>/`                     | Get details of a specific module       |
| `PATCH`  | `/author/courses/<course_id>/modules/<module_id>/`                     | Update a specific module               |
| `DELETE` | `/author/courses/<course_id>/modules/<module_id>/`                     | Delete a specific module               |
|          |                                                                        |                                        |
| `GET`    | `/author/courses/<course_id>/modules/<module_id>/lessons/`             | List all lessons in a module           |
| `POST`   | `/author/courses/<course_id>/modules/<module_id>/lessons/`             | Create a new lesson in a module        |
| `GET`    | `/author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/` | Get details of a specific lesson       |
| `PATCH`  | `/author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/` | Update a specific lesson               |
| `DELETE` | `/author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/` | Delete a specific lesson               |

#### **GET /author/courses**

**Response:**

```json
{
        "id": 1,
        "title": "Python",
        "category": "Programming",
        "course_image": "/media/course_images/python.png",
        "author": "Bakkenti",
        "description": "Master the fundamentals of programming with Python!",
        "duration": "2 weeks",
        "level": "all",
        "students": 1
    }
```
#### **POST /author/courses**

**Request Body:**

```json
{
  "title": "Python",
  "language": "Java/Golang/C#/C++/Javascript/Python",
  "course_image": "",
  "description": "Learn Python from scratch",
  "duration": "2 weeks",
  "level": "beginner/intermediate/expert/all",
}
```

#### **DELETE /author/courses/1**

**Response:**

```json
{"message": "Course deleted successfully"}
```

#### **GET /author/courses/1/modules**

**Response:**

```json
    {
        "module_id": 1,
        "module": "Introduction to Programming and Python",
        "duration": "1 hour",
        "lessons": [
            {
                "lesson_id": 1,
                "name": "What is Programming?",
                "short_description": "Discover what programming is, why it’s important, and how Python fits into the world of software development.",
                "video_url": null,
                "uploaded_video": null
            }
        ]
    },
    {
        "module_id": 2,
        "module": "Data Types and Variables",
        "duration": "1 hour",
        "lessons": [
            {
                "lesson_id": 1,
                "name": "Numbers, Strings, and Booleans",
                "short_description": "Explore the fundamental data types in Python and how they are used to store information.",
                "video_url": null,
                "uploaded_video": null
            }
        ]
    }
```
#### **POST /author/courses/1/modules**

**Request Body:**

```json
{
  "module": "Data Types and Variables",
  "duration": "2 weeks"
}
```
#### **GET /author/courses/1/modules/1/lessons**

**Response:**

```json
    {
        "lesson_id": 1,
        "name": "What is Programming?",
        "short_description": "Discover what programming is, why it’s important, and how Python fits into the world of software development.",
        "video_url": null,
        "uploaded_video": null
    },
    {
        "lesson_id": 2,
        "name": "Setting Up Your Python Environment",
        "short_description": "Learn how to install Python and set up your development environment to start writing your first code.",
        "video_url": null,
        "uploaded_video": null
    }
```
#### **POST /author/courses/1/modules/1/lessons**

**Request Body:**

```json
{
  "name": "What is programming?",
  "short_description": "Discover what programming is, why it’s important",
  "video_url": "google.com/video",
  "uploaded_video": null
}
```

#### **PATCH /author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/**
**Request Body:**
```json
{
  "content": "<p>Это новый урок. Картинка ниже:</p><img src=\"/media/images/example.jpg\" alt=\"Описание\"><p>Спасибо!</p>"
}
```
---
### **Author Blog Endpoints**

| Method   | Endpoint                     | Description                          |
|----------|------------------------------|--------------------------------------|
| `GET`    | `/author/blogs/`             | List all posts created by the author |
| `POST`   | `/author/blogs/`             | Create a new post                    |
| `PATCH`  | `/author/blogs/<course_id>/` | Update a specific post               |
| `DELETE` | `/author/blogs/<course_id>/` | Delete a specific post               |

#### **GET /author/blogs**

**Response:**

```json
    {
        "id": 6,
        "author_username": "Bakkenti",
        "title": "test blo1g",
        "content": "Test content1",
        "created_at": "2025-06-01T15:25:43.360489Z",
        "updated_at": "2025-06-01T15:25:43.360489Z",
        "published": true,
        "image": "/media/blog_images/uses-of-python.jpg",
        "views": 0
    },
    {
        "id": 5,
        "author_username": "Bakkenti",
        "title": "test blo1g",
        "content": "Test content1",
        "created_at": "2025-06-01T15:21:57.694285Z",
        "updated_at": "2025-06-01T15:24:21.016539Z",
        "published": true,
        "image": null,
        "views": 0
    },
```
#### **POST /author/blogs**

**Request Body:**

```json
{
    "title": "test blo1g",
    "published": "True/False",
    "image": ",/media/blog_images/uses-of-python.jpg",
    "content": "Test content1"
}
```

#### **PATCH /author/blogs/ID**

**Request Body:**

```json
{
    "title": "test blo1g",
    "published": "True/False",
    "image": null,
    "content": "Test content1"
}
```

#### **DELETE /author/blogs/ID**

**Response:**

```json
{"message": "Blog post deleted successfully"}
```
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
### **Exercises Endpoints**

| Method   | Endpoint                                                                                    | Description                                         |
|----------|---------------------------------------------------------------------------------------------|-----------------------------------------------------|
| `GET`    | `/author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/`            | List all exercises of chosen lesson in author panel |
| `POST`   | `/author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/ `           | Create an exercise in chosen lesson in author panel |
| `PATCH`  | `/author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/edit-mcq`    | Edit MCQ Tasks in author panel                      |
| `PATCH`  | `/author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/edit-code`   | Edit CODE Tasks in author panel                     |
 `DELETE` | `/author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/delete`      | Delete a specific (by id) or all exercises          |
| `GET`    | `/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises`                    | List all exercises of chosen lesson for student     |
| `GET`    | `/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/<exercise_id>`      | See details of specific exercise                    |
| `POST`   | `/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/submit-answer`                | Submit answer (code/mcq)                            |
| `GET`    | `/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/<exercise_id>/hint` | View actual information about hints                 |
| `POST`   | `/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/<exercise_id>/hint` | Request hint                                        |

#### **GET /author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/**
#### **GET /courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/**

**Response:**
**IF MCQ TASK**
```json
{
        "id": 33,
        "type": "mcq",
        "title": "What is the capital of France?",
        "description": "Choose the correct answer.",
        "language": "Python",
        "options": [
            {
                "id": 72,
                "text": "Paris",
                "is_correct": true
            },
            {
                "id": 73,
                "text": "London",
                "is_correct": false
            },
        ],
        "solution": null
    },
    {
        "id": 34,
        "type": "mcq",
        "title": "Which language runs in a web browser?",
        "description": "Choose the correct answer.",
        "language": 1,
        "options": [
            {
                "id": 75,
                "text": "Python",
                "is_correct": false
            },
            {
                "id": 76,
                "text": "JavaScript",
                "is_correct": true
            },
        ],
        "solution": null
    }
```
**Response:**
**IF CODE TASK**
```json
{
        "id": 36,
        "type": "code",
        "title": "Print Hello World",
        "description": "Write a program that prints 'Hello, World!'",
        "language": 1,
        "options": [],
        "solution": {
            "id": 7,
            "sample_input": "",
            "expected_output": "Hello, World!",
            "initial_code": "print()"
        }
    }
```

#### **POST /author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/**

**Request:**
**IF MCQ TASK**
```json
{
  "type": "mcq",
  "exercises": [
    {
      "title": "What is Python?",
      "description": "Choose the correct answer.",
      "options": [
        {"text": "A programming language", "is_correct": true},
        {"text": "A type of snake", "is_correct": false}
      ]
    },
    {
      "title": "What does HTML stand for?",
      "description": "Choose the correct answer.",
      "options": [
        {"text": "HyperText Markup Language", "is_correct": true},
        {"text": "Home Tool Markup Language", "is_correct": false}
      ]
    }
  ]
}

```
**Request:**
**IF CODE TASK**
```json
{
  "type": "code",
  "exercises": [
    {
      "title": "Print Hello World",
      "description": "Write a program that prints 'Hello, World!'",
      "solution": {
        "sample_input": "",
        "expected_output": "Hello, World!",
        "initial_code": "print()"
      }
    }
  ]
}
```
#### **PATCH /author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/edit-mcq**
**IF MCQ TASK**
**Request:**
```json
{
  "exercises": [
    {
      "exercise_id": 33,
      "title": "What is the capital of France? (Updated)",
      "description": "Choose the correct answer (Updated).",
      "options": [
        { "id": 72, "text": "Paris (Correct!)", "is_correct": true },
        { "id": 73, "text": "London", "is_correct": false },
        { "id": 74, "text": "Berlin", "is_correct": false }
      ]
    },
    {
      "exercise_id": 34,
      "title": "Which language runs in a web browser? (Fixed)",
      "options": [
        { "id": 75, "text": "Python", "is_correct": false },
        { "id": 76, "text": "JavaScript (Correct!)", "is_correct": true },
        { "id": 77, "text": "C++", "is_correct": false }
      ]
    }
  ]
}
```
#### **PATCH /author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/edit-code**
**IF CODE TASK**
**Request:**
```json
{
  "exercises": [
    {
      "exercise_id": 101,
      "title": "Print Hello (edited)",
      "description": "Update desc",
      "solution": {
        "sample_input": "",
        "expected_output": "Hello",
        "initial_code": "print()"
      }
    }
  ]
}
```
#### **DELETE /author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/delete/**
```json
{
  "ids": [12, 13, 14]
}


```

### **POST /courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/submit-answer/** 

*FOR MULTIPLE ANSWER FOR QUESTIONS*
**Request**
```json
{
  "answers": [
    { "exercise_id": 33, "selected_option": 72 },
    { "exercise_id": 34, "selected_option": 75 }
  ]
}
```
**Response**
```json
{
  "attempt_id": 5,
  "score": 1,
  "results": [
    {
      "exercise_id": 33,
      "is_correct": true
    },
    {
      "exercise_id": 34,
      "is_correct": false
    }
  ]
}
```

*FOR ANSWER TO CODE (COMPILER)*
**Request**
```json
{
  "answers": [
    {
      "exercise_id": 27,
      "submitted_code": "print('Hello, World!')"
    }
  ]
}

```
**Response**
```json
{
  "attempt_id": 6,
  "score": 1,
  "results": [
    {
      "exercise_id": 27,
      "is_correct": true,
      "submitted_output": "Hello, World!",
      "expected_output": "Hello, World!",
      "stderr": "",
      "exit_code": 0
    }
  ]
}
```

### **GET /courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/<exercise_id>/hint**

**Response**
```json
{
    "remaining": 0,
    "limit": 5,
    "next_available_in_minutes": 678
}
```

#### **POST /courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/<exercise_id>/hint**
*for code tasks only*

**Request**
```json
{
  "submitted_code": "print('Hi')"
}
```
**Response**

***If hints available***
```json
{
  "hint": "The function name should be `isPrint` for consistency with the task description. Additionally, the function should take an argument to print.\n\n",
  "fixed_code": "def isPrint(message):\n    print(message)\n\nisPrint('Hello')",
   "remaining": 4

}
```

***If no hints available (limit)***
```json
{
  "error": "You have reached the maximum number of hints allowed (5 per 12 hours).",
  "next_available_in_minutes": 720,
  "limit": 5,
  "remaining": 0
}
```
---


##  Conspect AI Assistant  

---

### **Endpoints Overview**

| Method   | Endpoint                            | Description                            |
|----------|-------------------------------------|----------------------------------------|
| `POST`   | `/conspect/start/`                  | Start new chat                         |
| `GET`    | `/conspect/`                        | Get a list of all chats                |
| `GET`    | `/conspect/<chat_id>/`              | History of messages of certain chat    |
| `POST`   | `/conspect/<chat_id>/send-message/` | Send a message to AI and get an answer |
| `DELETE` | `/conspect/<chat_id>/`              | Delete a chat with conspect            |
| `POST`   | `/conspect/<chat_id>/pdf/`          | Generate a pdf of conspect             |

---



**POST /conspect/start/**

```json
{
  "topic": "Recursion in Go",
  "language": "Go",
  "rules_style": "Short Academic Essay"
}
```

**Response**

```json
{
  "chat_id": 3
}
```

---


**GET /conspect/**

```json
[
  {
    "id": 3,
    "topic": "Recursion in Go",
    "language": "Go",
    "rules_style": "Short Academic Essay",
    "created_at": "2025-06-07T12:00:00Z"
  }
]
```

---



**GET /conspect/3/**

```json
{
  "chat_id": 3,
  "topic": "Recursion in Go",
  "language": "Go",
  "rules_style": "Short Academic Essay",
  "messages": [
    {
      "role": "user",
      "content": "What is recursion?"
    },
    {
      "role": "assistant",
      "content": "Recursion is when a function calls itself..."
    }
  ]
}
```

---

**POST /conspect/3/send-message/**

```json
{
  "content": "Add code examples."
}
```

**Response**

```json
{
  "chat_id": 3,
  "messages": [
    {
      "role": "user",
      "content": "Add code examples."
    },
    {
      "role": "assistant",
      "content": "Sure! Here's an example of recursion in Go..."
    }
  ]
}
```
---

### **Pet Projects Endpoints Overview**

| Method   | Endpoint                               | Description                                                  |
|----------|----------------------------------------|--------------------------------------------------------------|
| `POST`   | `/project-tor/`                        | Create a new ToR chat                                        |
| `GET`    | `/project-tor/`                        | Get all your ToR chats                                       |
| `GET`    | `/project-tor/<chat_id>/`              | Get ToR chat history                                         |
| `POST`   | `/project-tor/<chat_id>/send-message/` | Send a new message in ToR chat (AI answer & updated history) |
| `DELETE` | `/project-tor/<chat_id>/`              | Delete a ToR chat (with all its history)                     |
| `POST`   | `/project_tor/<chat_id>/pdf/`          | Generate a pdf of plan content                               |

### Create a new ToR chat 

**POST** `/project_tor/`

**Request:**

```json
{
  "topic": "Telegram bot for expense tracking"
}
```

**Response:**

```json
{
  "chat_id": 1
}
```

---

### Get all your ToR chats 

**GET** `/project_tor/`

**Response:**

```json
[
  {
    "id": 1,
    "topic": "Telegram bot for expense tracking",
    "created_at": "2025-06-09T12:00:00Z"
  },
  {
    "id": 2,
    "topic": "Personal finance API",
    "created_at": "2025-06-09T13:21:00Z"
  }
]
```

---

### Get ToR chat history 

**GET** `/project_tor/<chat_id>/`

**Response:**

```json
{
  "chat_id": 1,
  "topic": "Telegram bot for expense tracking",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Make a detailed technical specification for a pet project: a telegram bot for cost accounting.",
      "timestamp": "2025-06-09T12:01:05Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Here is a plan for your project: ...",
      "timestamp": "2025-06-09T12:01:07Z"
    }
  ]
}
```

---

### Send a new message in ToR chat (AI answer & updated history) 

**POST** `/project_tor/<chat_id>/send-message/`

**Request:**

```json
{
  "content": "Add an API endpoints section to the specification."
}
```

**Response:**

```json
{
  "chat_id": 1,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Make a detailed technical specification for a pet project: a telegram bot for cost accounting.",
      "timestamp": "2025-06-09T12:01:05Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Here is a plan for your project: ...",
      "timestamp": "2025-06-09T12:01:07Z"
    },
    {
      "id": 3,
      "role": "user",
      "content": "Add an API endpoints section to the specification.",
      "timestamp": "2025-06-09T12:03:02Z"
    },
    {
      "id": 4,
      "role": "assistant",
      "content": "API endpoints:\n1. POST /expense — ...\n2. GET /expense — ...\n...",
      "timestamp": "2025-06-09T12:03:05Z"
    }
  ]
}
```

---

### Delete a ToR chat (with all its history) 

**DELETE** `/project_tor/<chat_id>/`

**Response:**

```json
{
  "message": "Chat and all associated messages deleted."
}
```

---




---

## 📊 Language Recommendation AI (Survey)



### **Endpoint**

| Method | Endpoint     | Description                                   |
| ------ |--------------|-----------------------------------------------|
| `POST` | `/survey/`   | Send answers of survey and get recommendation |

---



**POST /survey/**

```json
{
  "answers": "1) I want to build web apps.\n2) I like clean syntax.\n3) I want to freelance."
}
```

---


**Response**
```json
{
  "result": "1. JavaScript - Great for web apps...\n2. Python - Clean syntax and easy to learn...\n3. Ruby - Elegant and great for freelancing...",
  "courses": {
    "Javascript": [
      {
        "id": 2,
        "title": "JavaScript"
      }
    ],
    "Python": [
      {
        "id": 1,
        "title": "Python"
      }
    ]
  }
}
```

---
### **Other**

| Method | Endpoint                   | Description                          |
|--------|----------------------------|--------------------------------------|
| `GET`  | `/mostpopularcourse/`      | Show most popular course             |
| `GET`  | `/bestcourse/`             | Show best-rated course               |
| `GET`  | `/advertisement/`          | Show advertisements                  |
| `GET`  | `/categories/`             | Show categories                      |
| `POST` | `/ckeditor5/image_upload/` | Upload images                        |
| `GET`  | `/keep-in-touch/`          | List all responses                   |
| `POST` | `/keep-in-touch/`          | Leave a response                     |
| `POST` | `/compiler/`               | Test a code                          |
| `GET`  | `/languages/`              | List all languages and their courses |

#### **GET /mostpopularcourse/**

**Response:**

```json
{
    "id": 1,
    "title": "Python",
    "category": "Programming",
    "course_image": "/media/course_images/python.png",
    "author": "Bakkenti",
    "description": "Master the fundamentals of programming with Python!",
    "duration": "2 weeks",
    "level": "all",
    "students": 1
}
```

#### **GET /bestcourse/**

**Response:**

```json
{
    "id": 2,
    "title": "JavaScript",
    "category": "Programming",
    "course_image": "/media/course_images/js.png",
    "author": "Bakkenti",
    "description": "Learn the essentials of JavaScript, the language of the web!\r\nThis course will guide you from the basics to key concepts used in interactive websites and web applications.\r\nYou’ll start with simple scripts and progress to writing real code for dynamic, responsive pages.\r\nBy the end, you’ll be able to create interactive features and understand the core principles behind modern web development.",
    "duration": "4 weeks",
    "level": "beginner",
    "students": 0
}
```

#### **GET /advertisement/**

**Response:**

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Agentic AI and AI Agents for Leaders",
            "content": "<p>Unlock the future of leadership with our exclusive program on Agentic AI and AI Agents.",
            "image": "https://quant.up.railway.app/media/ad.png",
            "url": "http://www.coursera.org/specializations/ai-agents-for-leaders",
            "created_at": "2025-05-18T23:23:59.003374Z"
        }
    ]
}
```
#### **GET /categories/**

**Response:**

```json
{
            "id": 1,
            "name": "Programming",
            "courses_count": 2
}
```
---
# Site reviews
| Method | Endpoint              | Description                 |
|--------|-----------------------|-----------------------------|
| `GET`  | `/blog/site-reviews/` | List all reviews on website |
| `POST` | `/blog/site-reviews/` | Create single review           
#### **GET /site-reviews/**

```json
 {
        "id": 1,
        "username": "Bakkenti",
        "role": "author",
        "rating": 4,
        "feedback": "Очень удобный сайт! Спасибо за сервис.",
        "created_at": "2025-05-28T23:05:38.403954Z",
        "status": "positive"
    }
```
#### **POST /site-reviews/**

```json
 {
        "rating": 4,
        "feedback": "Очень удобный сайт! Спасибо за сервис."
    }
```
#### **GET /keep-in-touch/**
 ```json   {
        "id": 1,
        "email": "user@email.com",
        "phone": "+1234567890",
        "message": "I want to keep in touch about your platform.",
        "created_at": "2025-06-01T23:09:34.727982Z"
    }
```
#### **POST /keep-in-touch/**
 ```json   {
        "email": "user@email.com",
        "phone": "+1234567890", //optional
        "message": "I want to keep in touch about your platform."
    }
```

#### **POST /keep-in-touch/**

**Body Request:**
 ```json   
{
  "language": "python",
  "code": "print('Hello')"
}
```

**Response:**
 ```json   
{
    "stdout": "Hello\n",
    "stderr": "",
    "exit_code": 0
}
```

### GET /programming-languages/

**Response:**
```json
[
  {
    "id": 1,
    "name": "Python",
    "courses": 5
  },
  {
    "id": 2,
    "name": "C++",
    "courses": 2
  }
]
```
---
# Chatting with AI support
| Method | Endpoint        | Description           |
|--------|-----------------|-----------------------|
| `GET`  | `/ai-history/`  | List history of chat  |
| `POST` | `/ai-dialog/`   | Send message  

### POST /ai-dialog/
**Request:**
```json
{
  "message": "Hello, how are you?"
}
````

**Response:**

```json
{
  "text": "Hi, I am good. What about you?"
}
```

---

### GET /ai-history/

**Response:**

```json
[
  {
    "role": "user",
    "content": "What is decorator in Python?",
    "timestamp": "2025-06-10T05:45:22.738Z"
  },
  {
    "role": "assistant",
    "content": "A decorator in Python is a function that changes the behavior of another function without changing its code.",
    "timestamp": "2025-06-10T05:45:23.159Z"
  }
]
```


**POST `/compiler/`**

```json
{
  "input": "print('hello')",
  "language": "python"
}
```

**Response:**

```json
{
  "stdout": "hello\n",
  "stderr": "",
  "exit_code": 0
}
```

---

### Body Request for AI features:

**POST `/compiler-features/`**

```json
{
  "input": "def foo():\n  pass",
  "feature": "Refactor code",
  "language": "python"
}
```

**Response:**

```json
{
  "text": "Код был улучшен...",
  "code": "def foo():\n    # improved version\n    pass"
}
```

---
## Moderation of applications for roles

### Get all applications for authorship/journalism

```
GET /applies/
```

**Answer:**

```json
[
  {
    "author_id": 1,
    "author_username": "Bakkenti",
    "author_status": "approved",
    "author_reject_reason": "",
    "journalist_status": "rejected",
    "journalist_reject_reason": ""
  },
  ...
]
```

---

### Approve the application

```
POST /applies/{user_id}/{role}/approve/
```

**role:** `"author"` or `"journalist"`
**Request body:** empty
**Response:**

```json
{"message": "Author application approved."}
```

or

```json
{"message": "Journalist application approved."}
```

---

### Reject the application

```
POST /applies/{user_id}/{role}/reject/
```

**role:** `"author"` or `"journalist"`
**Request body:**

```json
{"reason": "Not enough publications"}
``

**Answer:**

```json
{"message": "Author application rejected."}
```

or

```json
{"message": "Journalist application rejected."}
```

---

### Change the user role

```
POST /applies/{user_id}/change-role/
```

**Request body:**

```json
{"role": "student"}             // or "author", "journalist", "author_journalist"
``

**Answer:**

```json
{"message": "Role changed to student."}
```

---

## User Management

### Deactivate the user (delete after 7 days)

```
POST /users/{user_id}/deactivate/
```

**Request body:** empty
**Response:**

```json
{"message": "User deactivated and scheduled for deletion."}
```

---

### Restore the user

```
POST /users/{user_id}/restore/
```

**Request body:** empty
**Response:**

```json
{"message": "User restored."}
```

---

### Get a list of all users with roles

```
GET /users-list/
```

**Answer:**

```json
[
  {
    "id": 5,
    "username": "ElonMuskat",
    "role": "author_journalist"
  },
  ...
]
```

---

## Advertising

### Get a list of all ads (for the moderator)

```
GET /advertisements/
```

**Answer:**

``json
[
{
"id": 1,
"name": "Advertisement 1",
"content": "<p>Some HTML</p>",
"image": "/media/images/img.jpg ",
"url": "https://example.com ",
"created_at": "2025-06-10T15:00:00Z"
},
...
]
``

---

### Create a new ad

```
POST /advertisements/
```

**Request body:**

```json
{
  "name": "Promo",
  "content": "<p>The text of the advertisement</p>",
  "image": null, // file or url if sent via form-data
  "url": "https://promo.com"
}
```

**Answer:**

```json
{
  "id": 1,
  "name": "Promo",
  "content": "<p>The text of the advertisement</p>",
  "image": "/media/images/...",
  "url": "https://promo.com",
  "created_at": "2025-06-10T15:00:00Z"
}
```

---

### Get, edit, delete ads by id

```
GET /advertisements/{id}/
PATCH /advertisements/{id}/
DELETE /advertisements/{id}/
```

**PATCH — request body:** (example)

``json
{
"name": "New name",
  "content": "<p>Updated text</p>"
}
``

**Answer:**

```json
{
  "id": 1,
  "name": "New name",
  "content": "<p>Updated text</p>",
  "image": "/media/images/...",
  "url": "https://promo.com",
  "created_at": "2025-06-10T15:00:00Z"
}
```

---

## Blog — deleting comments

### Delete a comment by a moderator

```
DELETE /blog/comments/{id}/moderator-delete/
```
---

### Delete the comment by the owner (student)

```
DELETE /blog/comments/{id}/delete/
```
---

### Endpoint for getting lesson progress:

**GET**: `/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/progress/`

**Response**:

```json
{
  "lesson_id": 1,
  "student_id": 5,
  "is_viewed": true,
  "is_completed": false,
  "completed_at": null,
  "progress_percent": 60.0
}
```

**Fields in the response**:

* `lesson_id': The lesson ID.
* `student_id': The student's ID.
* `is_viewed`: The status of whether the student has viewed the lesson.
* `is_completed`: The status of whether the student has completed the lesson.
* `completed_at': Lesson completion time (if completed).
* `progress_percent`: Student's percentage of lesson completion (from 0 to 100%).

### Endpoint for getting course progress:

**GET**: `/courses/{course_id}/progress/`

**Response**:

```json
{
  "course_id": 9,
  "student_id": 5,
  "progress_percent": 85.0,
  "is_completed": false,
  "completed_at": null
}
```

---

###1. Get the details of the final exam

**GET /courses/{course\_id}/final-exam/**

**Response**

```json
{
  "id": 4,
  "course": 9,
"title": "Python Final",
"description": "Final Python Exam",
  "duration_minutes": 60,
  "max_attempts": 3,
  "questions": [
{
"id": 1,
"text": "What is Python?",
"options": [
{"id": 10, "text": "Programming language", "is_correct": true},
        {"id": 11, "text": "Snake type", "is_correct": false}
      ]
    }
  ]
}
```

---

### 2. Create a final exam (course author only)

**POST /courses/{course\_id}/final-exam/create/**

**Request**

``json
{
"title": "Python Final",
"description": "Final Python Exam",
  "duration_minutes": 60,
  "max_attempts": 3,
  "questions": [
{
"text": "What is Python?",
"options": [
{"text": "Programming language", "is_correct": true},
        {"text": "Snake type", "is_correct": false}
      ]
    }
  ]
}
```

**Response**

```json
{
  "id": 4,
  "detail": "Exam created"
}
```

If the exam already exists:

```json
{
  "error": "Final exam for this course already exists."
}
```

---

###3. Start the exam attempt

**POST /courses/{course\_id}/final-exam/start/**

**Response**

```json
{
  "id": 5,
  "student": 3,
  "exam": 4,
  "started_at": "2025-06-11T09:50:42.100Z",
  "finished_at": null,
  "score": null,
  "passed": false,
  "answers": {},
  "is_completed": false,
  "attempt_number": 1
}
```

If there is an incomplete attempt:

```json
{
  "error": "You already have an unfinished attempt."
}
```

If the attempts have ended:

```json
{
  "error": "No more attempts available"
}
```

---

###4. Send the exam answers (complete the attempt)

**POST /courses/{course\_id}/final-exam/submit-answer/**

**Request**

``json
{
"answers": {
"1": [10], // Question 1: Have the options with the id been selected=10
"2": [15, 16] // Question 2: options selected
}
}
``

**Response**

```json
{
  "score": 90.0,
  "details": [
    {"question_id": "1", "correct": true},
    {"question_id": "2", "correct": false}
  ],
  "max_score": 100,
  "attempt_number": 1,
  "can_retry": true
}
```

If there is no active attempt:

``json
{
"error": "No active exam attempt."
}
``

---

###5. Get a list of your exam attempts

**GET /courses/{course\_id}/final-exam/attempts/**

**Response**

```json
[
  {
    "id": 5,
    "student": 3,
    "exam": 4,
    "started_at": "2025-06-11T09:50:42.100Z",
    "finished_at": "2025-06-11T10:30:00.000Z",
    "score": 90.0,
    "passed": true,
    "answers": {
      "1": [10],
      "2": [15, 16]
    },
    "is_completed": true,
    "attempt_number": 1
  },
  {
    "id": 6,
    "student": 3,
    "exam": 4,
    "started_at": "2025-06-11T11:00:42.100Z",
    "finished_at": "2025-06-11T11:40:00.000Z",
    "score": 80.0,
    "passed": true,
    "answers": {
      "1": [10],
      "2": [15]
    },
    "is_completed": true,
    "attempt_number": 2
  }
]
```

---

## Briefly:

* **GET** `/courses/{course_id}/final-exam/` — get exam
* **POST** `/courses/{course_id}/final-exam/` — create exam
* **POST** `/courses/{course_id}/final-exam/start/` — start an attempt
* **POST** `/courses/{course_id}/final-exam/submit-answer/` — send answers and end the attempt
* **GET** `/courses/{course_id}/final-exam/attempts/` — a list of your attempts

This is enough to work with the final exam and the attempts.

---

### My certificates

* **GET** `/certificates/`
* **Response:**

```json
[
  {
    "course": "Python",
    "issued_at": "2025-06-10T23:17:41.994846Z",
    "pdf_url": "http://127.0.0.1:8000/media/certificates/certificate_Bakkenti_1.pdf",
    "score": 95.5,
    "verify_url": "https://quant.up.railway.app/certificate/verify/2f39bbbd-2b0d-4ea5-901e-c8ea15c6f4c3/"
  }
]
```

---

### Generate certificate

* **POST** `/certificates/generate/<course_id>/`
* **Response (success):**

```json
{
  "message": "Certificate generated successfully.",
  "pdf_url": "http://127.0.0.1:8000/media/certificates/certificate_Bakkenti_1.pdf",
  "highest_score": 95.5
}
```

* **Response (if already has):**

```json
{
  "error": "You already have a certificate for this course.",
  "pdf_url": "http://127.0.0.1:8000/media/certificates/certificate_Bakkenti_1.pdf"
}
```

---

### Verify certificate

* **GET** `/certificate/verify/<uuid:token>/`
* **Response:**

```json
{
  "user": "Bakkenti",
  "course": "Python",
  "issued_at": "2025-06-10T23:17:41.994846Z",
  "hash_code": "5854c085be2bada1bec8dbb0ed25563b803aabeec5d6975e93c00f85a4e4f477",
  "score": 95.5,
  "pdf_url": "http://127.0.0.1:8000/media/certificates/certificate_Bakkenti_1.pdf"
}
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
