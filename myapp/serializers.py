from rest_framework import serializers
from .models import Author, Student, Course, Module, Lesson, Post
from django.conf import settings


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ['username', 'email', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        if Student.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email is already in use."})

        if Student.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Username is already in use."})

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        student = Student.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return student

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username and not email:
            raise serializers.ValidationError({"error": "Username or email is required."})

        user = None
        if username:
            user = Student.objects.filter(username=username).first()
        elif email:
            user = Student.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({"error": "User not found."})

        if not user.check_password(password):
            raise serializers.ValidationError({"error": "Invalid password."})

        data['user'] = user
        return data

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

    def validate(self, data):
        if data.get('video_url') and data.get('uploaded_video'):
            raise serializers.ValidationError("You cannot provide both a video URL and an uploaded video.")
        return data

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'module', 'lessons']

    def get_course(self, obj):
        return f"{obj.course.title} [id={obj.course.id}]"