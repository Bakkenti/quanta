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
#### **DELETE /author/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/**
```json
{
  "exercise_ids": [33, 34, 35]
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

#### **POST /courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/exercises/<exercise_id>/hint**
*for code tasks only*

**Request**
```json
{
  "submitted_code": "print('Hi')"
}
```
**Response**
```json
{
  "hint": "The function name should be `isPrint` for consistency with the task description. Additionally, the function should take an argument to print.\n\n",
  "fixed_code": "def isPrint(message):\n    print(message)\n\nisPrint('Hello')"
}
```
---


##  Conspect AI Assistant  

---

### **Endpoints Overview**

| Method | Endpoint                    | Description                            |
| ------ | --------------------------- |----------------------------------------|
| `POST` | `/conspect/start/`          | Start new chat                         |
| `GET`  | `/conspect/`                | Get a list of all chats                |
| `GET`  | `/conspect/<chat_id>/`      | History of messages of certain chat    |
| `POST` | `/conspect/<chat_id>/send/` | Send a message to AI and get an answer |

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



**POST /conspect/3/send/**

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

## 📊 Language Recommendation AI (Survey)



### **Endpoint**

| Method | Endpoint     | Description                                   |
| ------ |--------------|-----------------------------------------------|
| `POST` | `/survey/`   | Send answers of survey and get recommendation |

---



**POST /survey/recommendation/**

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

| Method | Endpoint                   | Description              |
|--------|----------------------------|--------------------------|
| `GET`  | `/mostpopularcourse/`      | Show most popular course |
| `GET`  | `/bestcourse/`             | Show best-rated course   |
| `GET`  | `/advertisement/`          | Show advertisements      |
| `GET`  | `/categories/`             | Show categories          |
| `POST` | `/ckeditor5/image_upload/` | Upload images            |
| `GET`  | `/keep-in-touch/`          | List all responses       |
| `POST` | `/keep-in-touch/`          | Leave a response         |

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
