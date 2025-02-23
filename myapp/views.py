from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse, path, reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, logout as django_logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.utils.decorators import method_decorator
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.account.views import LoginView, SignupView
from .models import Course, Lesson, Student, Author, Review, Module, MostPopularCourse, BestCourse, Advertisement
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
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from dj_rest_auth.views import LoginView
import logging
from django.utils.functional import SimpleLazyObject

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')  # Перенаправляем на главную, если пользователь уже вошел
        return Response({"detail": "Please log in using POST request."}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({"detail": "You are already authenticated."}, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)

@method_decorator(csrf_exempt, name='dispatch')
class Logout(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        django_logout(request)
        return Response({"message": "Successfully logged out."}, status=200)

    def get(self, request):
        django_logout(request)
        return Response({"message": "Successfully logged out (GET)."}, status=200)


class Profile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQwMzQ0MjA0LCJpYXQiOjE3NDAzNDM5MDQsImp0aSI6IjY3YzBlMTlkZDVjYzQwZmZhYTUzZTNiMTY0ZTQwMGY0IiwidXNlcl9pZCI6MTl9.ye3988d0MDONOc7VASmimN_TcWU7t2K0RiMQOIyRtqI"

        # Прикрепляем токен к мета-информации запроса
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        user = request.user

        if user.is_anonymous:
            return Response({"detail": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            "username": user.username,
            "email": user.email
        })


class CourseList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        courses = Course.objects.all()

        if not courses:
            return Response({'message': 'No courses available'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)


class CourseDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, id):
        try:
            User = get_user_model()

            if isinstance(request.user, SimpleLazyObject):
                request.user = User.objects.get(pk=request.user.pk)

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

    def post(self, request, id):
        try:
            User = get_user_model()

            if isinstance(request.user, SimpleLazyObject):
                request.user = User.objects.get(pk=request.user.pk)

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

        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return Response({"error": str(e)}, status=500)

class LessonDetail(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id, lessonid):
        course = get_object_or_404(Course, id=id)
        lesson = get_object_or_404(Lesson, lesson_id=lessonid, module__course=course)

        lesson_data = {
            "id": lesson.lesson_id,
            "name": lesson.name,
            "description": lesson.short_description,
            "content": lesson.content,
            "video_url": lesson.video_url if lesson.video_url else None,
            "uploaded_video": lesson.uploaded_video.url if lesson.uploaded_video else None,
        }

        return Response(lesson_data, status=status.HTTP_200_OK)

class MostPopularCourseView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        most_popular_entry = MostPopularCourse.objects.select_related('course').first()

        if not most_popular_entry or not most_popular_entry.course:
            return Response({"message": "No most popular course found"}, status=404)

        serializer = CourseSerializer(most_popular_entry.course, context={'request': request})
        return Response(serializer.data)

class BestCourseView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        best_course_entry = BestCourse.objects.select_related('course').first()

        if not best_course_entry or not best_course_entry.course:
            return Response({"message": "No best course found"}, status=404)

        serializer = CourseSerializer(best_course_entry.course, context={'request': request})
        return Response(serializer.data)

class AdvertisementView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Advertisement.objects.all().order_by("-created_at")
    serializer_class = AdvertisementSerializer

class AuthorCourseListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get(self, request, *args, **kwargs):
        try:
            author = Author.objects.get(user=request.user)
            courses = Course.objects.filter(author=author)
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Author.DoesNotExist:
            return Response({"error": "Author profile not found."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            try:
                author = Author.objects.get(user=request.user)
                serializer.save(author=author)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Author.DoesNotExist:
                return Response({"error": "Author profile not found."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorCourseEditView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id, author__user=request.user)
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id, author__user=request.user)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id, author__user=request.user)
        course.delete()
        return Response({"message": "Course deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class AuthorModuleListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id, author__user=request.user)
        modules = Module.objects.filter(course=course)
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id, author__user=request.user)
        serializer = ModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorModuleEditView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get(self, request, course_id, module_id, *args, **kwargs):
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)
        serializer = ModuleSerializer(module)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, module_id, *args, **kwargs):
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)
        serializer = ModuleSerializer(module, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, module_id, *args, **kwargs):
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)
        module.delete()
        return Response({"message": "Module deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class AuthorLessonListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get(self, request, course_id, module_id, *args, **kwargs):
        # Получаем модуль по его id и course_id
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)

        # Получаем все уроки для данного модуля
        lessons = Lesson.objects.filter(module=module)

        # Сериализуем уроки и возвращаем их в ответе
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, course_id, module_id, *args, **kwargs):
        # Получаем модуль по его id и course_id
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)

        # Сериализуем входные данные для нового урока
        serializer = LessonSerializer(data=request.data)

        # Если сериализатор валиден, сохраняем урок, связывая его с нужным модулем
        if serializer.is_valid():
            lesson = serializer.save(module=module)  # Здесь передаем сам объект module
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Если сериализатор не валиден, возвращаем ошибку
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorLessonEditView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get(self, request, course_id, module_id, lesson_id, *args, **kwargs):
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)
        lesson = get_object_or_404(Lesson, lesson_id=lesson_id, module=module)
        serializer = LessonSerializer(lesson)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, course_id, module_id, lesson_id, *args, **kwargs):
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)
        lesson = get_object_or_404(Lesson, lesson_id=lesson_id, module=module)

        serializer = LessonSerializer(lesson, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, course_id, module_id, lesson_id, *args, **kwargs):
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)

        lesson = get_object_or_404(Lesson, lesson_id=lesson_id, module=module)

        lesson.delete()
        return Response({"message": "Lesson deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

