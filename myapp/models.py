from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django_ckeditor_5.fields import CKEditor5Field
from .custom_storage import video_storage
import re
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg

def validate_course_duration(value):
    pattern = r'^(?P<value>[1-9]|[1-2][0-9]|30) (?P<unit>(day|week|days|weeks))$'
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid duration (e.g., '3 weeks' or '1 day').")


def validate_module_duration(value):
    pattern = r'^(?P<value>([1-9]|[1-2][0-9]|30)) (?P<unit>(hour|minute|hours|minutes))$'
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid duration (e.g., '2 hours' or '15 minutes').")


def validate_phone_number(value):
    if not re.match(r"^\+?[1-9]\d{1,14}$", value):
        raise ValidationError("Enter a valid phone number (e.g., +1234567890).")


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student", null=True, blank=True)

    ROLE_CHOICES = [
        ("student", "Student"),
        ("author", "Author"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    about = models.TextField(max_length=500, null=True, blank=True, default="")
    birthday = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, validators=[validate_phone_number], null=True, blank=True)
    gender_choices = [("M", "Male"), ("F", "Female"), ("O", "Other")]
    gender = models.CharField(choices=gender_choices, null=True, max_length=1, blank=True)
    enrolled_courses = models.ManyToManyField("Course", blank=True, related_name="students")

    def set_password(self, raw_password):
        if self.user:
            self.user.set_password(raw_password)

    def check_password(self, raw_password):
        if self.user:
            return self.user.check_password(raw_password)
        return False

    def is_enrolled(self, course):
        return self.enrolled_courses.filter(id=course.id).exists()

    def save(self, *args, **kwargs):
        if not self.user:
            raise ValidationError("Student must have an associated user.")
        super().save(*args, **kwargs)

    def __str__(self):
        if self.user:
            return self.user.username
        return "No Username"


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="author")

    def __str__(self):
        return f"Author: {self.user.username if self.user else 'Unknown'}"

class Course(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    LEVEL_CHOICES = [
        ("all", "All Levels"),
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("expert", "Expert"),
    ]
    description = models.TextField()
    duration = models.CharField(max_length=20, validators=[validate_course_duration])
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, default="all")
    course_image = models.ImageField(upload_to="course_images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    module = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    duration = models.CharField(max_length=20, validators=[validate_module_duration])

    def __str__(self):
        return f"{self.module} - {self.course.title}"


class Lesson(models.Model):
    name = models.CharField(max_length=200)
    short_description = models.TextField(null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    video_url = models.URLField(blank=True, null=True)
    uploaded_video = models.FileField(upload_to="lesson_videos/", storage=video_storage, blank=True, null=True)
    content = CKEditor5Field(config_name='default', blank=True, null=True)

    def clean(self):
        if any([self.video_url, self.uploaded_video]) and not all([self.video_url, self.uploaded_video]):
            return
        raise ValidationError("You must provide either a video URL or an uploaded video, but not both.")

    def __str__(self):
        return f"{self.name} - {self.module.module}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    feedback = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "course")

    def clean(self):
        student = getattr(self.user, "student", None)
        if not student or not student.is_enrolled(self.course):
            raise ValidationError("You must be enrolled in this course to leave a review.")

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}/5) ⭐"


class MostPopularCourse(models.Model):
    course = models.OneToOneField("Course", on_delete=models.CASCADE, related_name="most_popular", unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def update_most_popular(cls):
        most_popular = (
            Course.objects.annotate(student_count=Count("students"))
            .filter(student_count__gt=0)
            .order_by("-student_count", "-created_at", "-id")
            .first()
        )

        if most_popular:
            cls.objects.update_or_create(defaults={"course": most_popular})
        else:
            cls.objects.filter(id=1).delete()


class BestCourse(models.Model):
    course = models.OneToOneField("Course", on_delete=models.CASCADE, related_name="best_course", unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def update_best_course(cls):
        best_course = (
            Course.objects.annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews"))
            .filter(review_count__gt=0)
            .order_by("-avg_rating", "-review_count", "-created_at", "-id")
            .first()
        )

        if best_course:
            cls.objects.update_or_create(defaults={"course": best_course})
        else:
            cls.objects.filter(id=1).delete()

class Advertisement(models.Model):
    name = models.CharField(max_length=255)
    content = CKEditor5Field(config_name='default', blank=True, null=True)
    image = models.ImageField(upload_to="media/", null=True, blank=True)
    url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
