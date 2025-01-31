from rest_framework import serializers
from .models import Author, Student, Course, Module, Lesson


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


class ProfileSerializer(serializers.ModelSerializer):
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
            'level',
            'rating',
        ]

    def get_course_image(self, obj):
        return obj.course_image.url if obj.course_image else None

    def get_author_username(self, obj):
        return obj.author.user.username if obj.author and obj.author.user else None


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
