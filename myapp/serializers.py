from rest_framework import serializers
from .models import Author, Student, Course, Module, Lesson, Post
from django.conf import settings


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['username', 'password']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)



class CourseSerializer(serializers.ModelSerializer):
    course_image = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'course_image',
            'description',
            'duration',
            'students_count',
            'level',
            'author',
            'rating',
        ]

    def get_course_image(self, obj):
        if obj.course_image:
            return f"{settings.MEDIA_URL}{obj.course_image}"
        return None


class LessonSerializer(serializers.ModelSerializer):
    module = serializers.CharField(source='module.title', read_only=True)
    class Meta:
        model = Lesson
        fields = ['id', 'name', 'short_description', 'module']

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'module', 'lessons']

    def get_course(self, obj):
        return f"{obj.course.title} [id={obj.course.id}]"