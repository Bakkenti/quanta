from rest_framework import serializers
from .models import Author, Student, Course, Module, Lesson, User
from django.conf import settings


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'confirm_password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if len(data['password']) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user


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
            user = User.objects.filter(username=username).first()
        elif email:
            user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({"error": "User not found."})

        if not user.check_password(password):
            raise serializers.ValidationError({"error": "Invalid password."})

        data['user'] = user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Student
        fields = ['id', 'username', 'email', 'avatar', 'about', 'birthday', 'phone_number', 'gender', 'subscribed_courses']


class CourseSerializer(serializers.ModelSerializer):
    course_image = serializers.SerializerMethodField()
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'course_image',
            'author_username',  # Добавляем username автора
            'description',
            'duration',
            'level',
            'rating',
        ]

    def get_course_image(self, obj):
        if obj.course_image:
            return obj.course_image.url
        return None

    def get_author_username(self, obj):
        # Проверяем, связан ли курс с автором
        if obj.author and obj.author.user:
            return obj.author.user.username
        return None


class LessonSerializer(serializers.ModelSerializer):
    module = serializers.CharField(source='module.title', read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'name', 'short_description', 'module', 'video_url', 'uploaded_video', 'duration']

    def validate(self, data):
        if data.get('video_url') and data.get('uploaded_video'):
            raise serializers.ValidationError("You cannot provide both a video URL and an uploaded video.")
        if not data.get('video_url') and not data.get('uploaded_video'):
            raise serializers.ValidationError("You must provide either a video URL or an uploaded video.")
        return data


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['module', 'id', 'lessons', 'duration']
