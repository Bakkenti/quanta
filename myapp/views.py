from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from rest_framework import status
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from rest_framework.decorators import api_view, permission_classes
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Course, Lesson, Student, Review, Module
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    CourseSerializer,
    LessonSerializer,
    ModuleSerializer,
    ReviewSerializer,
    ProfileSerializer
)
from django.urls import path

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from allauth.account.views import LoginView, SignupView
from django.contrib import messages
from django.contrib.auth import get_user_model

class login(LoginView):
    def form_valid(self, form):
        messages.success(self.request, f"✅ Welcome back, {self.request.user.username}!")
        return super().form_valid(form)


class signup(SignupView):
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.user
        student, created = Student.objects.get_or_create(user=user)
        messages.success(self.request, f"🎉 Successfully registered as {user.email}")
        return response

def auth_logout(request):
    django_logout(request)
    return HttpResponseRedirect('/')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    print(f"➡ Запрос в profile от пользователя: {request.user}")
    student = getattr(request.user, 'student', None)

    if not student:
        return Response({"error": "Student profile not found for this user."}, status=404)
    serializer = ProfileSerializer(student)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def course_list(request):
    courses = Course.objects.all()
    if not courses:
        return Response({'message': 'No courses available'})
    serializer = CourseSerializer(courses, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def course(request, id):
    try:
        course = get_object_or_404(Course.objects.prefetch_related('modules', 'modules__lessons', 'reviews'), id=id)

        if request.user.is_authenticated and hasattr(request.user, 'student'):
            student = request.user.student
        else:
            student = None  # Guest user (not logged in)

        # Handle review submission (POST)
        if request.method == 'POST':
            if not student:
                return Response({"error": "You must be logged in to write a review."}, status=status.HTTP_401_UNAUTHORIZED)

            existing_review = Review.objects.filter(user=student, course=course).first()
            if existing_review:
                return Response({"error": "You have already reviewed this course."}, status=status.HTTP_400_BAD_REQUEST)

            rating = request.data.get("rating")
            feedback = request.data.get("feedback", "")

            if not rating or int(rating) not in range(1, 6):
                return Response({"error": "Rating must be between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)

            Review.objects.create(user=student, course=course, rating=rating, feedback=feedback)
            return Response({"message": "Review submitted successfully!"}, status=status.HTTP_201_CREATED)

        # Fetch course data
        course_data = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "course_image": course.course_image.url if course.course_image else None,
            "duration": course.duration,
            "level": course.level,
        }

        modules = course.modules.all()
        module_serializer = ModuleSerializer(modules, many=True)

        author_data = None
        if course.author and course.author.user:
            author_data = {
                "id": course.author.user.id,
                "username": course.author.user.username,
                "about": course.author.user.about,
                "avatar": course.author.user.avatar.url if course.author.user.avatar else None,
            }

        # Fetch existing reviews
        reviews = Review.objects.filter(course=course)
        reviews_data = ReviewSerializer(reviews, many=True).data

        # Check if the student has already reviewed (only if authenticated)
        existing_review = Review.objects.filter(user=student, course=course).first() if student else None
        can_write_review = student and not existing_review and student.is_enrolled(course)

        write_review = {
            "allowed": can_write_review,
            "message": "You can write a review for this course" if can_write_review else "You have already reviewed this course",
            "form_fields": {
                "rating": "Integer (1-5)",
                "feedback": "Optional text"
            }
        } if student else None  # Hide if user is not logged in

        response_data = {
            "Overview": course_data,
            "Curriculum": module_serializer.data,
            "Author": author_data,
            "Reviews": {
                "existing_reviews": reviews_data,
                "write_review": write_review
            }
        }

        return Response(response_data, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


# Урок
@api_view(['GET'])
@permission_classes([AllowAny])
def lesson(request, id, lessonid=None, name=None):
    course = get_object_or_404(Course, id=id)
    if lessonid is None:
        return Response({"error": "Lesson ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    lesson = get_object_or_404(Lesson, id=lessonid, module__course=course)
    lesson_data = {
        "id": lesson.id,
        "name": lesson.name,
        "description": lesson.short_description,
        "content": lesson.content,
        "video_url": lesson.video_url if lesson.video_url else None,
        "uploaded_video": lesson.uploaded_video.url if lesson.uploaded_video else None,
    }

    return Response(lesson_data, status=status.HTTP_200_OK)
