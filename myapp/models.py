from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db.models import Avg
import re
from django.utils.text import slugify


# Validators
def validate_course_duration(value):
    pattern = r'^(?P<value>([1-9]|[1-2][0-9]|30)) (?P<unit>(week|day|weeks|days))$'
    match = re.match(pattern, value)
    if not match:
        raise ValidationError("Enter a valid duration (e.g., '3 weeks' or '1 day').")


def validate_module_duration(value):
    pattern = r'^(?P<value>([1-9]|[1-2][0-9]|30)) (?P<unit>(hour|minute|hours|minutes))$'
    match = re.match(pattern, value)
    if not match:
        raise ValidationError("Enter a valid duration (e.g., '2 hours' or '15 minutes').")


# User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


# User Model
class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ("guest", "Guest"),
        ("student", "Student"),
        ("author", "Author"),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="guest")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username

    def promote_to_student(self):
        if self.role == "guest":
            Student.objects.create(user=self)
            self.role = "student"
            self.save()
        else:
            raise ValueError("Only guests can be promoted to students.")

    def promote_to_author(self):
        if self.role == "student" and hasattr(self, "student"):
            Author.objects.create(
                user=self,
                avatar=self.student.avatar,
                about=self.student.about,
                birthday=self.student.birthday,
                phone_number=self.student.phone_number,
                gender=self.student.gender,
            )
            self.role = "author"
            self.save()
        else:
            raise ValueError("Only students can be promoted to authors.")


# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    about = models.TextField(max_length=500, blank=True)
    birthday = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    gender_choices = [("M", "Male"), ("F", "Female"), ("O", "Other")]
    gender = models.CharField(choices=gender_choices, max_length=1, blank=True)
    subscribed_courses = models.ManyToManyField("Course", blank=True)

    def __str__(self):
        return f"Student: {self.user.username}"


# Author Model
class Author(models.Model):
    GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("O", "Other")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="author")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    about = models.TextField(max_length=500, blank=True)
    birthday = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, blank=True)
    published_courses = models.ManyToManyField(
        "Course",
        blank=True,
        related_name="published_by_authors",  # Изменяем related_name
    )

    def __str__(self):
        return f"Author: {self.user.username}"


# Course Model
class Course(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authored_courses'
    )
    LEVEL_CHOICES = [
        ("all", "All Levels"),
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("expert", "Expert"),
    ]
    description = models.TextField()
    duration = models.CharField(max_length=20, validators=[validate_course_duration], help_text="e.g., '4 weeks'")
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, default="all")
    course_image = models.ImageField(upload_to="course_images/", null=True, blank=True)
    rating = models.FloatField(default=0.0)

    def get_slug(self):
        return slugify(self.title)

    def total_lessons(self):
        return self.modules.aggregate(total_lessons=models.Count("lessons__id"))["total_lessons"] or 0

    def total_duration(self):
        lessons = Lesson.objects.filter(module__course=self)
        total_seconds = sum([lesson.get_duration_in_seconds() for lesson in lessons])
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m"

    def __str__(self):
        return self.title


# Module Model
class Module(models.Model):
    module = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    duration = models.CharField(
        max_length=20,
        validators=[validate_module_duration],
        help_text="Enter duration (e.g., '2 hours' or '15 minutes')"
    )

    def __str__(self):
        return f"{self.title} - {self.course.title}"


# Lesson Model
class Lesson(models.Model):
    name = models.CharField(max_length=200)
    short_description = models.TextField(null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    video_url = models.URLField(blank=True, null=True)
    uploaded_video = models.FileField(upload_to="lesson_videos/", blank=True, null=True)
    duration = models.CharField(max_length=20, help_text="Enter duration (e.g., '25:32')")
    content = models.TextField(null=True, blank=True)

    def get_duration_in_seconds(self):
        try:
            minutes, seconds = map(int, self.duration.split(":"))
            return minutes * 60 + seconds
        except (ValueError, AttributeError):
            return 0

    def __str__(self):
        return f"{self.name} - {self.module.title}"
