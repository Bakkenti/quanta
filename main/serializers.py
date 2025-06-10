from rest_framework import serializers
from .models import (Author, Student, Course, Module, Lesson, Review, Advertisement, Category, SiteReview, KeepInTouch,
                     ConspectChat, ConspectMessage, ProjectToRMessage, ProjectToRChat, Moderator)
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
from rest_framework.validators import UniqueValidator
from allauth.account.utils import send_email_confirmation
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Username already exists.")]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email already registered.")]
    )
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.CharField(required=False, default='student')
    avatar = serializers.ImageField(required=False, allow_null=True)
    about = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    birthday = serializers.DateField(required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=15)
    gender = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=10)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def validate_gender(self, value):
        if value and value not in ["Male", "Female", "Other"]:
            raise serializers.ValidationError("Invalid gender.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        student = user.student
        student.role = validated_data.get('role', 'student')
        student.avatar = validated_data.get('avatar')
        student.about = validated_data.get('about', '')
        student.birthday = validated_data.get('birthday')
        student.phone_number = validated_data.get('phone_number')
        student.gender = validated_data.get('gender')
        student.save()
        send_email_confirmation(self.context['request'], user)
        return student

class CustomLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        user = authenticate(request=self.context.get('request'), **attrs)

        if not user:
            raise serializers.ValidationError({
                'non_field_errors': [_('Invalid credentials.')]
            })

        verified = EmailAddress.objects.filter(user=user, verified=True).exists()
        if not verified:
            raise serializers.ValidationError({
                'non_field_errors': [_('Please confirm your email before logging in.')]
            })

        self.user = user

        return super().validate(attrs)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'email')

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ['avatar', 'about', 'birthday', 'phone_number', 'gender']

    def validate_email(self, value):
        user = self.instance.user if self.instance else None
        if user and value != user.email:
            if User.objects.filter(email=value).exclude(pk=user.pk).exists():
                raise serializers.ValidationError("This email is already in use.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'email' in user_data:
            instance.user.email = user_data['email']
            instance.user.save()
        return super().update(instance, validated_data)

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            'is_author',
            'is_journalist',
            'author_status',
            'author_reject_reason',
            'journalist_status',
            'journalist_reject_reason'
        ]


class CourseSerializer(serializers.ModelSerializer):
    course_image = serializers.ImageField(required=False, allow_null=True)
    author = serializers.CharField(source="author.user.username", read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    students = serializers.SerializerMethodField()
    language = serializers.CharField(source='language.name', read_only=True)
    average_mark = serializers.FloatField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'category',
            'language',
            'course_image',
            'author',
            'description',
            'duration',
            'level',
            'students',
            'average_mark',
            'created_at'
        ]

    def get_course_image(self, obj):
        return obj.course_image.url if obj.course_image else None

    def get_students(self, obj):
        return obj.students.count()

    def get_average_mark(self, obj):
        reviews = obj.reviews.all()
        if not reviews.exists():
            return None
        return round(sum([review.rating for review in reviews]) / reviews.count(), 2)

class CategorySerializer(serializers.ModelSerializer):
    courses_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'courses_count']

    def get_courses_count(self, obj):
        return obj.courses.count()


class LessonSerializer(serializers.ModelSerializer):
    content = CKEditor5Field()

    class Meta:
        model = Lesson
        fields = ['lesson_id', 'name', 'short_description', 'video_url', 'uploaded_video', 'content']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('hide_content', False):
            self.fields.pop('content')

class ModuleSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['module_id', 'module', 'duration', 'lessons']

    def get_lessons(self, obj):
        serializer = LessonSerializer(obj.lessons.all(), many=True, context={'hide_content': True})
        return serializer.data


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

class SiteReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    role = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)

    class Meta:
        model = SiteReview
        fields = ['id', 'username', 'role', 'rating', 'feedback', 'created_at', 'status']

    def get_role(self, obj):
        if hasattr(obj.user, 'student'):
            return obj.user.student.role
        return None

class KeepInTouchSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeepInTouch
        fields = ['id', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

class ConspectMessageSerializer(serializers.ModelSerializer):
    pagination_class = None

    class Meta:
        model = ConspectMessage
        fields = ['id', 'role', 'content', 'timestamp']

class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField()

class ConspectChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConspectChat
        fields = ['id', 'topic', 'language', 'rules_style', 'created_at']


class ProjectToRMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectToRMessage
        fields = ['id', 'role', 'content', 'timestamp']

class ProjectToRChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectToRChat
        fields = ['id', 'topic', 'created_at']

class ModeratorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='student.user.username', read_only=True)
    avatar = serializers.ImageField(source='student.avatar', read_only=True)
    birthday = serializers.DateField(source='student.birthday', read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = Moderator
        fields = ['id', 'username', 'avatar', 'birthday', 'role', 'is_active', 'created_at']

    def get_role(self, obj):
        return "Moderator"