from rest_framework import serializers
from .models import Author, Student, Course, Module, Lesson, Review, Advertisement
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django_ckeditor_5.fields import CKEditor5Field


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ['username', 'email', 'password', 'confirm_password', 'role', 'avatar', 'about', 'birthday',
                  'phone_number', 'gender']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if len(data['password']) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        student = Student.objects.create(
            user=user,
            role=validated_data.get('role', 'guest'),
            avatar=validated_data.get('avatar'),
            about=validated_data.get('about'),
            birthday=validated_data.get('birthday'),
            phone_number=validated_data.get('phone_number'),
            gender=validated_data.get('gender'),
        )

        return student


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'username', 'email', 'role', 'avatar', 'about', 'birthday', 'phone_number', 'gender']



class CourseSerializer(serializers.ModelSerializer):
    course_image = serializers.SerializerMethodField()
    author = serializers.CharField(source="author.user.username", read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'category',
            'course_image',
            'author',
            'description',
            'duration',
            'level'
        ]

    def get_course_image(self, obj):
        return obj.course_image.url if obj.course_image else None


class LessonSerializer(serializers.ModelSerializer):
    module = serializers.CharField(source='module.module', read_only=True)
    content = CKEditor5Field()

    class Meta:
        model = Lesson
        fields = ['module', 'lesson_id', 'name', 'short_description', 'video_url', 'uploaded_video', 'content']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['module_id', 'module', 'lessons', 'duration']

class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user_username', 'rating', 'feedback', 'created_at']

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d %B %Y")

class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ["id", "name", "content", "image", "url", "created_at"]