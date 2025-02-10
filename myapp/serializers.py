from rest_framework import serializers
from .models import Author, Student, Course, Module, Lesson, Review
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


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
        student = Student.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'guest'),
            avatar=validated_data.get('avatar'),
            about=validated_data.get('about'),
            birthday=validated_data.get('birthday'),
            phone_number=validated_data.get('phone_number'),
            gender=validated_data.get('gender'),
        )
        student.set_password(validated_data['password'])
        student.save()
        return student


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # You can add custom validation here, if needed
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'username', 'email', 'role', 'avatar', 'about', 'birthday', 'phone_number', 'gender']



class CourseSerializer(serializers.ModelSerializer):
    course_image = serializers.SerializerMethodField()
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'course_image',
            'author_username',
            'description',
            'duration',
            'level'
        ]

    def get_course_image(self, obj):
        return obj.course_image.url if obj.course_image else None

    def get_author_username(self, obj):
        if obj.author and hasattr(obj.author, 'user') and obj.author.user:
            return "obj.author.user.username"
        return None


class LessonSerializer(serializers.ModelSerializer):
    module = serializers.CharField(source='module.module', read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'name', 'short_description', 'module', 'video_url', 'uploaded_video', 'content']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'module', 'lessons', 'duration']

class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user_username', 'rating', 'feedback', 'created_at']

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d %B %Y")
