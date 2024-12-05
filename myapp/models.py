from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    about = models.TextField(default="No information available.")
    course_list = models.ManyToManyField('Course', blank=True, related_name='authored_courses')
    subscribed_courses = models.JSONField(default=dict, blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def __str__(self):
        return self.username


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True, default='default@example.com')
    username = models.CharField(max_length=40, unique=True)
    password = models.CharField(max_length=128)
    subscribed_courses = models.JSONField(default=dict, blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return self.username


def validate_course_duration(value):
    pattern = r'^(?P<value>([1-9]|[1-2][0-9]|30)) (?P<unit>(week|day|weeks|days))$'
    match = re.match(pattern, value)
    if not match:
        raise ValidationError("Write valid duration for course.")


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    course_image = models.ImageField(upload_to='course_images/', null=False, blank=False)
    description = models.TextField()
    duration = models.CharField(
        max_length=20,
        validators=[validate_course_duration],
        help_text="Enter duration (e.g., '3 weeks' or '1 day')"
    )
    students = models.ManyToManyField('Student', related_name='courses_subscribed_to', blank=True)
    level = models.CharField(
        max_length=20,
        choices=[('all', 'All Levels'), ('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')],
        default='all'
    )
    author = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='courses')
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0, null=True, blank=True)

    @property
    def students_count(self):
        # Returns the number of students enrolled in the course
        return self.students.count()

    @property
    def lessons_count(self):
        return Lesson.objects.filter(module__course=self).count()

    def save(self, *args, **kwargs):
        if self.description:
            self.description = self.description.replace('"', '')
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


def validate_module_duration(value):
    pattern = r'^(?P<value>([1-9]|[1-2][0-9]|30)) (?P<unit>(hour|minute|hours|minutes))$'
    match = re.match(pattern, value)
    if not match:
        raise ValidationError("Write valid duration for module.")


class Module(models.Model):
    id = models.AutoField(primary_key=True)
    module = models.CharField(max_length=200)
    duration = models.CharField(
        max_length=20,
        validators=[validate_module_duration],
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')

    def lessons_count(self):
        return self.lessons.count()

    def __str__(self):
        return self.module


class Lesson(models.Model):
    name = models.CharField(max_length=200)
    short_description = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    uploaded_video = models.FileField(upload_to='lesson_videos/', blank=True, null=True)
    content = CKEditor5Field(blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons', default=1)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', default=1)

    def __str__(self):
        return self.name


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure that content_type is set correctly
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.content_object)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}: {self.text[:20]}"


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return self.title

