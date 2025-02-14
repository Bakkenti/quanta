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
from .models import Course, Lesson, Student, Review, Module, MostPopularCourse, BestCourse, Advertisement
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    CourseSerializer,
    LessonSerializer,
    ModuleSerializer,
    ReviewSerializer,
    ProfileSerializer,
    AdvertisementSerializer
)
from rest_framework import generics
from django.urls import path
from django.db.models import Count, Avg
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from allauth.account.views import LoginView, SignupView
from django.contrib import messages
from django.contrib.auth import get_user_model
import logging
from django.utils.functional import SimpleLazyObject

logger = logging.getLogger(__name__)

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
    student, created = Student.objects.get_or_create(user=request.user)
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
    User = get_user_model()

    if isinstance(request.user, SimpleLazyObject):
        request.user = User.objects.get(pk=request.user.pk)

    try:
        logger.info(f"🔍 request.user: {request.user} (Type: {type(request.user)})")

        course = get_object_or_404(
            Course.objects.prefetch_related('modules', 'modules__lessons', 'reviews'), id=id
        )

        student = None
        if request.user.is_authenticated:
            try:
                student = request.user.student
            except Student.DoesNotExist:
                student = None

        if request.method == 'POST':
            if not student:
                return Response({"error": "You must be logged in to write a review."}, status=status.HTTP_401_UNAUTHORIZED)

            if not isinstance(student.user, User):
                return Response({"error": "Invalid user instance."}, status=status.HTTP_400_BAD_REQUEST)

            existing_review = Review.objects.filter(user=student.user, course=course).first()
            if existing_review:
                return Response({"error": "You have already reviewed this course."}, status=status.HTTP_400_BAD_REQUEST)

            rating = request.data.get("rating")
            feedback = request.data.get("feedback", "")

            if not rating or int(rating) not in range(1, 6):
                return Response({"error": "Rating must be between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)

            Review.objects.create(user=student.user, course=course, rating=rating, feedback=feedback)
            return Response({"message": "Review submitted successfully!"}, status=status.HTTP_201_CREATED)

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
        if course.author and hasattr(course.author, 'user') and isinstance(course.author.user, User):
            author_data = {
                "id": course.author.user.id,
                "username": course.author.user.username,
                "about": getattr(course.author, 'about', None),
                "avatar": course.author.user.avatar.url if getattr(course.author.user, 'avatar', None) else None,
            }

        reviews = Review.objects.filter(course=course)
        reviews_data = ReviewSerializer(reviews, many=True).data

        existing_review = None
        can_write_review = False

        if student and isinstance(student.user, User):
            existing_review = Review.objects.filter(user=student.user, course=course).first()
            can_write_review = not existing_review and student.is_enrolled(course)

        write_review = {
            "allowed": can_write_review,
            "message": (
                "You can write a review for this course"
                if can_write_review
                else "You must be enrolled to review this course"
                if student
                else "Login required to leave a review"
            ),
            "form_fields": {
                "rating": "Integer (1-5)",
                "feedback": "Optional text"
            }
        } if student else None

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
        logger.error(f"❌ Error: {str(e)}")
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


@api_view(['GET'])
@permission_classes([AllowAny])
def most_popular_course(request):
    most_popular_entry = MostPopularCourse.objects.select_related('course').first()

    if not most_popular_entry or not most_popular_entry.course:
        return Response({"message": "No most popular course found"}, status=404)

    serializer = CourseSerializer(most_popular_entry.course, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def best_course(request):
    best_course_entry = BestCourse.objects.select_related('course').first()

    if not best_course_entry or not best_course_entry.course:
        return Response({"message": "No best course found"}, status=404)

    serializer = CourseSerializer(best_course_entry.course, context={'request': request})
    return Response(serializer.data)

class advertisement(generics.ListAPIView):
    queryset = Advertisement.objects.all().order_by("-created_at")
    serializer_class = AdvertisementSerializer

