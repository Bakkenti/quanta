from django.shortcuts import get_object_or_404
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status, viewsets
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission
from django.core.mail import send_mail
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.test import APIRequestFactory
from rest_framework.generics import RetrieveAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.sessions.middleware import SessionMiddleware
from dj_rest_auth.views import LoginView
from reportlab.pdfbase.pdfmetrics import stringWidth
from .models import (Course, Lesson, Student, Author, Review, Module, MostPopularCourse, BestCourse, Advertisement, Category, SiteReview,
                     KeepInTouch, ProgrammingLanguage, ConspectChat, ConspectMessage, Certificate, CourseProgress, LessonProgress,
                     ProjectToRChat, ProjectToRMessage, ChatMessage, Chat, FinalExam, FinalExamAttempt, FinalExamQuestion, FinalExamOption)
from .serializers import (RegistrationSerializer, CategorySerializer, CourseSerializer, LessonSerializer, ModuleSerializer, ReviewSerializer,
                          ProfileSerializer, AdvertisementSerializer, UserSerializer, SiteReviewSerializer, KeepInTouchSerializer,
                          ConspectMessageSerializer, SendMessageSerializer, ConspectChatSerializer, ProjectToRMessageSerializer, ProjectToRChatSerializer,
                          FinalExamSerializer, FinalExamAttemptSerializer)
from blog.models import BlogPost
import datetime
from .signals import recalc_lesson_progress
from exercises.models import Exercise, LessonAttempt
from rest_framework.decorators import action
from django.utils import timezone
from blog.serializers import BlogPostSerializer
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.db.models import Avg
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.account.models import EmailAddress, EmailConfirmation, EmailConfirmationHMAC
from exercises.ai_helper import forward_answers_to_ai, generate_conspect_response, execute_code, ask_ai, compiler_feature
from quanta import settings
from .utils import generate_certificate
import urllib.parse
import json
import requests
import logging
import os
import uuid
import time
from io import BytesIO
from django.conf import settings
from django.http import JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor

logger = logging.getLogger(__name__)

class Registration(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Registration successful."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(LoginView):

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({"detail": "You are already authenticated."}, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get("username")
        if username:
            try:
                user = get_user_model().objects.get(username=username)
                email_obj = EmailAddress.objects.filter(user=user, verified=True).first()
                if not email_obj:
                    return Response({"detail": "Please verify your email before logging in."}, status=400)
            except get_user_model().DoesNotExist:
                pass

        response = super().post(request, *args, **kwargs)

        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        else:
            User = get_user_model()
            if 'user' in response.data:
                username = response.data['user'].get('username')
                user = User.objects.filter(username=username).first()

        if user:
            response.data['user'] = UserSerializer(user).data

        return response


class ConfirmEmail(APIView):
    def post(self, request):
        key = request.data.get('key')
        if not key:
            return Response({"detail": "No key provided."}, status=400)

        confirmation = EmailConfirmationHMAC.from_key(key)
        if confirmation is None:
            try:
                confirmation = EmailConfirmation.objects.get(key=key)
            except EmailConfirmation.DoesNotExist:
                return Response({"detail": "Invalid or expired key."}, status=400)

        confirmation.confirm(request)
        return Response({"detail": "Email confirmed successfully."})

class Profile(APIView):

    def get(self, request):
        user = request.user

        try:
            student = user.student
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            is_journalist = user.author.is_journalist
        except Exception:
            is_journalist = False

        enrolled_courses = student.enrolled_courses.all()
        enrolled_courses_dict = {course.id: course.title for course in enrolled_courses}

        return Response({
            "username": user.username,
            "email": user.email,
            "avatar": student.avatar.url if student.avatar else None,
            "role": student.role,
            "is_journalist": is_journalist,
            "about": student.about,
            "birthday": student.birthday,
            "gender": student.gender,
            "phone_number": student.phone_number,
            "enrolled_courses": enrolled_courses_dict
        })

class ProfileEdit(APIView):

    def patch(self, request):
        user = request.user
        try:
            student = user.student
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfileSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CourseList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        courses = Course.objects.annotate(average_mark=Avg('reviews__rating')).all()

        if not courses:
            return Response({'message': 'No courses available'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)


class CourseDetail(APIView):

    def get(self, request, id):
        try:
            User = get_user_model()

            if isinstance(request.user, SimpleLazyObject):
                request.user = User.objects.get(pk=request.user.pk)

            logger.info(f"🔍 request.user: {request.user} (Type: {type(request.user)})")

            course = get_object_or_404(
                Course.objects.annotate(average_mark=Avg('reviews__rating')).prefetch_related('modules', 'modules__lessons', 'reviews'), id=id)

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
                "students": course.students_count,
                "average_mark": course.average_mark,
                "created_at": course.created_at
            }

            modules = course.modules.all()
            module_serializer = ModuleSerializer(modules, many=True)

            author_data = None
            if course.author and hasattr(course.author, 'user') and isinstance(course.author.user, User):
                student_profile = getattr(course.author.user, 'student', None)
                author_data = {
                    "id": course.author.user.id,
                    "username": course.author.user.username,
                    "about": student_profile.about if student_profile else None,
                    "avatar": student_profile.avatar.url if student_profile and student_profile.avatar else None,
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

    def patch(self, request, id):

            User = get_user_model()
            if isinstance(request.user, SimpleLazyObject):
                request.user = User.objects.get(pk=request.user.pk)

            course = get_object_or_404(Course, id=id)
            student = getattr(request.user, "student", None)
            if not student:
                return Response({"error": "No student profile."}, status=404)

            review = Review.objects.filter(user=student.user, course=course).first()
            if not review:
                return Response({"error": "Review does not exist."}, status=404)

            rating = request.data.get("rating")
            feedback = request.data.get("feedback")

            if rating is not None:
                if int(rating) not in range(1, 6):
                    return Response({"error": "Rating must be 1-5."}, status=400)
                review.rating = int(rating)
            if feedback is not None:
                review.feedback = feedback

            review.save()
            return Response({"message": "Review updated successfully."}, status=200)

    def delete(self, request, id):
            User = get_user_model()
            if isinstance(request.user, SimpleLazyObject):
                request.user = User.objects.get(pk=request.user.pk)

            course = get_object_or_404(Course, id=id)
            student = getattr(request.user, "student", None)
            if not student:
                return Response({"error": "No student profile."}, status=404)

            review = Review.objects.filter(user=student.user, course=course).first()
            if not review:
                return Response({"error": "Review does not exist."}, status=404)

            review.delete()
            return Response({"message": "Review deleted successfully."}, status=204)

class LessonDetail(APIView):
    permission_classes = [AllowAny]

    def get(self, request, course_id, module_id, lesson_id):
        module = get_object_or_404(Module, course__id=course_id, module_id=module_id)
        lesson = get_object_or_404(Lesson, module=module, lesson_id=lesson_id)

        student = request.user.student
        lp, _ = LessonProgress.objects.get_or_create(student=student, lesson=lesson)
        if not lp.is_viewed:
            lp.is_viewed = True
            lp.save()
        recalc_lesson_progress(student, lesson)

        lesson_data = {
            "id": lesson.lesson_id,
            "name": lesson.name,
            "description": lesson.short_description,
            "content": lesson.content,
            "video_url": lesson.video_url if lesson.video_url else None,
            "uploaded_video": lesson.uploaded_video.url if lesson.uploaded_video else None,
        }

        return Response(lesson_data, status=status.HTTP_200_OK)


class EnrollCourse(APIView):

    def post(self, request, course_id):
        student = request.user.student
        course = get_object_or_404(Course, id=course_id)
        if course in student.enrolled_courses.all():
            return Response({"detail": "You are already enrolled."}, status=status.HTTP_400_BAD_REQUEST)
        student.enrolled_courses.add(course)
        return Response({"detail": "Enrolled successfully."}, status=status.HTTP_200_OK)


class UnenrollCourse(APIView):

    def post(self, request, course_id):
        student = request.user.student
        course = get_object_or_404(Course, id=course_id)
        if course not in student.enrolled_courses.all():
            return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_400_BAD_REQUEST)
        student.enrolled_courses.remove(course)
        return Response({"detail": "Unenrolled successfully."}, status=status.HTTP_200_OK)

class MyCourses(APIView):

    def get(self, request):
        student = request.user.student
        enrolled_courses = student.enrolled_courses.all()
        serializer = CourseSerializer(enrolled_courses, many=True)
        return Response(serializer.data)

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

class AdvertisementView(ListAPIView):
    pagination_class = None
    queryset = Advertisement.objects.all().order_by('-created_at')
    serializer_class = AdvertisementSerializer
    permission_classes = [AllowAny]


class AuthorCourseListCreate(APIView):

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


class AuthorCourseEdit(APIView):

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


class AuthorModuleListCreate(APIView):

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


class AuthorModuleEdit(APIView):

    def get(self, request, course_id, module_id, *args, **kwargs):
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)
        serializer = ModuleSerializer(module)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, course_id, module_id, *args, **kwargs):
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)
        serializer = ModuleSerializer(module, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, course_id, module_id, *args, **kwargs):
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)
        module.delete()
        return Response({"message": "Module deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class AuthorLessonListCreate(APIView):

    def get(self, request, course_id, module_id, *args, **kwargs):
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)
        lessons = Lesson.objects.filter(module=module)
        serializer = LessonSerializer(lessons, many=True, context={'hide_content': True})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, course_id, module_id, *args, **kwargs):
        module = get_object_or_404(Module, module_id=module_id, course__id=course_id, course__author__user=request.user)

        serializer = LessonSerializer(data=request.data)

        if serializer.is_valid():
            lesson = serializer.save(module=module)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorLessonEdit(APIView):

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

class SiteStats(APIView):
    def get(self, request):
        students_count = Student.objects.count()
        authors_count = Author.objects.count()
        total_courses = Course.objects.count()
        total_lessons = Lesson.objects.count()
        average_site_rating = SiteReview.objects.aggregate(avg_rating=Avg('rating'))['avg_rating']
        average_site_rating = round(average_site_rating, 2) if average_site_rating is not None else None
        return Response({
            "total_students": students_count,
            "total_authors": authors_count,
            "total_courses": total_courses,
            "total_lessons": total_lessons,
            "average_site_rating": average_site_rating
        })


class SiteReviewView(APIView):

    def post(self, request):
        user = request.user
        if SiteReview.objects.filter(user=user).exists():
            return Response({"error": "You have already left a review."}, status=status.HTTP_400_BAD_REQUEST)
        rating = request.data.get("rating")
        feedback = request.data.get("feedback", "")
        if not rating or int(rating) not in range(1, 6):
            return Response({"error": "Rating must be between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)
        review = SiteReview.objects.create(user=user, rating=rating, feedback=feedback)
        serializer = SiteReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        reviews = SiteReview.objects.select_related('user').all().order_by('-created_at')
        serializer = SiteReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LessonImageUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('upload')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)
        filename = default_storage.save(f'images/{file.name}', file)
        file_url = default_storage.url(filename)
        return Response({
            'url': file_url
        })


class GoogleCodeExchangeView(APIView):
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({"detail": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)
        code = urllib.parse.unquote(code)

        redirect_uri = request.data.get('redirect_uri', settings.GOOGLE_REDIRECT_URI)
        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        token_resp = requests.post(token_url, data=data, headers=headers)
        try:
            token_json = token_resp.json()
        except Exception:
            token_json = {}
        if token_resp.status_code != 200 or 'access_token' not in token_json:
            return Response({
                "detail": "Could not get access_token from Google",
                "response": token_resp.text
            }, status=400)
        access_token = token_json['access_token']
        id_token = token_json.get('id_token', None)

        factory = APIRequestFactory()
        social_data = {'access_token': access_token}
        if id_token:
            social_data['id_token'] = id_token

        new_request = factory.post(
            '/auth/google/',
            social_data,
            format='json'
        )
        new_request.user = request.user

        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(new_request)
        new_request.session.save()
        setattr(new_request, '_messages', FallbackStorage(new_request))

        view = GoogleLogin.as_view()
        return view(new_request)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class GithubCodeExchangeView(APIView):
    def post(self, request):
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri', settings.GITHUB_REDIRECT_URI)
        if not code:
            return Response({"detail": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)

        token_url = 'https://github.com/login/oauth/access_token'
        data = {
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': redirect_uri
        }
        headers = {
            'Accept': 'application/json'
        }
        token_resp = requests.post(token_url, data=data, headers=headers)
        print(f"GitHub response status: {token_resp.status_code}")
        print(f"GitHub response text: {token_resp.text}")

        token_json = token_resp.json()
        if token_resp.status_code != 200 or 'access_token' not in token_json:
            return Response({"detail": "Could not get access_token from GitHub", "response": token_resp.text}, status=400)

        access_token = token_json['access_token']

        factory = APIRequestFactory()
        new_request = factory.post(
            '/auth/github/',
            {'access_token': access_token},
            format='json'
        )
        new_request.user = request.user

        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(new_request)
        new_request.session.save()

        setattr(new_request, '_messages', FallbackStorage(new_request))

        view = GithubLogin.as_view()
        return view(new_request)

class GithubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter


class AuthorBlogListCreate(APIView):

    def get(self, request, *args, **kwargs):
        try:
            author = Author.objects.get(user=request.user)
            if not author.is_journalist:
                return Response({"error": "Access denied. Not a journalist."}, status=status.HTTP_403_FORBIDDEN)
            blogs = BlogPost.objects.filter(author=author)
            serializer = BlogPostSerializer(blogs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Author.DoesNotExist:
            return Response({"error": "Author profile not found."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            author = Author.objects.get(user=request.user)
            if not author.is_journalist:
                return Response({"error": "Access denied. Not a journalist."}, status=status.HTTP_403_FORBIDDEN)
        except Author.DoesNotExist:
            return Response({"error": "Author profile not found."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthorBlogEdit(APIView):

    def get(self, request, blog_id, *args, **kwargs):
        author = get_object_or_404(Author, user=request.user)
        if not author.is_journalist:
            return Response({"error": "Access denied. Not a journalist."}, status=status.HTTP_403_FORBIDDEN)
        blog = get_object_or_404(BlogPost, id=blog_id, author=author)
        serializer = BlogPostSerializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, blog_id, *args, **kwargs):
        author = get_object_or_404(Author, user=request.user)
        if not author.is_journalist:
            return Response({"error": "Access denied. Not a journalist."}, status=status.HTTP_403_FORBIDDEN)
        blog = get_object_or_404(BlogPost, id=blog_id, author=author)
        serializer = BlogPostSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, blog_id, *args, **kwargs):
        author = get_object_or_404(Author, user=request.user)
        if not author.is_journalist:
            return Response({"error": "Access denied. Not a journalist."}, status=status.HTTP_403_FORBIDDEN)
        blog = get_object_or_404(BlogPost, id=blog_id, author=author)
        blog.delete()
        return Response({"message": "Blog deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class KeepInTouchView(APIView):
    def get(self, request):
        messages = KeepInTouch.objects.all().order_by('-created_at')
        serializer = KeepInTouchSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = KeepInTouchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Message sent successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplyAuthor(APIView):
    def post(self, request):
        author, _ = Author.objects.get_or_create(user=request.user)
        if author.author_status == "approved":
            return Response({"message": "You are already approved as a course author."}, status=200)
        if author.author_status == "pending":
            return Response({"message": "Your course author application is already under review."}, status=200)
        author.author_status = "pending"
        author.author_reject_reason = ""
        author.save()
        return Response({"message": "Your application to become a course author has been submitted. Please wait for review."}, status=202)

class ApplyJournalist(APIView):
    def post(self, request):
        author, _ = Author.objects.get_or_create(user=request.user)
        if author.journalist_status == "approved":
            return Response({"message": "You are already approved as a journalist."}, status=200)
        if author.journalist_status == "pending":
            return Response({"message": "Your journalist application is already under review."}, status=200)
        author.journalist_status = "pending"
        author.journalist_reject_reason = ""
        author.save()
        return Response({"message": "Your application to become a journalist has been submitted. Please wait for review."}, status=202)

class AppliesStatus(APIView):
    def get(self, request):
        author = getattr(request.user, 'author', None)
        if not author:
            return Response({
                "author_status": "none",
                "author_reject_reason": "",
                "journalist_status": "none",
                "journalist_reject_reason": ""
            }, status=200)
        return Response({
            "author_status": author.author_status,
            "author_reject_reason": author.author_reject_reason or "",
            "journalist_status": author.journalist_status,
            "journalist_reject_reason": author.journalist_reject_reason or ""
        }, status=200)

class WithdrawApplication(APIView):
    def post(self, request, role):
        author, _ = Author.objects.get_or_create(user=request.user)
        if role == "author":
            if author.author_status != "pending":
                return Response({"message": "There is no pending course author application to withdraw."}, status=400)
            author.author_status = "none"
            author.author_reject_reason = ""
            author.save()
            return Response({"message": "Your course author application has been withdrawn."}, status=200)
        elif role == "journalist":
            if author.journalist_status != "pending":
                return Response({"message": "There is no pending journalist application to withdraw."}, status=400)
            author.journalist_status = "none"
            author.journalist_reject_reason = ""
            author.save()
            return Response({"message": "Your journalist application has been withdrawn."}, status=200)
        else:
            return Response({"message": "Invalid role specified."}, status=400)

class SurveyRecommendationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        answers = request.data.get("answers", "")
        if not answers or not isinstance(answers, str):
            return Response({"error": "Missing or invalid 'answers'"}, status=400)

        response = forward_answers_to_ai(answers)
        if "error" in response:
            return Response({"error": response["error"]}, status=500)

        return Response(response)



class ConspectChatListView(ListAPIView):
    pagination_class = None
    serializer_class = ConspectChatSerializer

    def get_queryset(self):
        return ConspectChat.objects.filter(user=self.request.user).order_by("-created_at")


class ConspectHistoryView(APIView):
    pagination_class = None

    def get(self, request, chat_id):
        chat = get_object_or_404(ConspectChat, id=chat_id, user=request.user)
        messages = chat.messages.order_by("timestamp")
        serialized = ConspectMessageSerializer(messages, many=True)
        return Response({
            "chat_id": chat.id,
            "topic": chat.topic,
            "language": chat.language,
            "rules_style": chat.rules_style,
            "messages": serialized.data
        })

    def delete(self, request, chat_id):
        chat = get_object_or_404(ConspectChat, id=chat_id, user=request.user)
        chat.delete()
        return Response({"message": "Chat and all associated messages deleted."}, status=204)

class ConspectSendMessageView(APIView):
    pagination_class = None

    def post(self, request, chat_id):
        chat = get_object_or_404(ConspectChat, id=chat_id, user=request.user)
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.validated_data["content"]

        ConspectMessage.objects.create(chat=chat, role="user", content=content)

        try:
            ai_text = generate_conspect_response(chat, content)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        ConspectMessage.objects.create(chat=chat, role="assistant", content=ai_text)

        messages = chat.messages.order_by("timestamp")
        serialized = ConspectMessageSerializer(messages, many=True)

        return Response({
            "chat_id": chat.id,
            "messages": serialized.data
        })


class ConspectStartChatView(APIView):
    pagination_class = None

    def post(self, request):
        topic = request.data.get("topic")
        language = request.data.get("language")
        style = request.data.get("rules_style")

        if not topic or not language or not style:
            return Response({"error": "Missing topic, language, or rules_style"}, status=400)

        chat = ConspectChat.objects.create(
            user=request.user,
            topic=topic,
            language=language,
            rules_style=style
        )

        return Response({"chat_id": chat.id}, status=201)

class CodeExecutionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        language = request.data.get("language")
        code = request.data.get("input") or request.data.get("code")
        if not language or not code:
            return Response({"error": "Missing 'language' or 'code'"}, status=400)
        stdout, stderr, exit_code = execute_code(language, code)
        return Response({
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code
        })


class CompilerFeaturesView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("input") or request.data.get("code")
        feature = request.data.get("feature")
        language = request.data.get("language")
        if not code or not feature or not language:
            return Response({"error": "Missing required fields"}, status=400)
        text, new_code = compiler_feature(code, feature, language)
        return Response({"text": text, "code": new_code})

class MyCertificatesView(APIView):
    def get(self, request):
        certs = Certificate.objects.filter(user=request.user)
        data = [{
            "course": cert.course.title,
            "issued_at": cert.issued_at,
            "pdf_url": request.build_absolute_uri(cert.pdf_file.url),
            "verify_url": f"https://quant.up.railway.app/certificate/verify/{cert.token}/"
        } for cert in certs]
        return Response(data)

class CertificateVerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        cert = get_object_or_404(Certificate, token=token)
        return Response({
            "user": cert.user.username,
            "course": cert.course.title,
            "issued_at": cert.issued_at,
            "hash_code": cert.hash_code,
            "pdf_url": request.build_absolute_uri(cert.pdf_file.url),
        })

class TriggerCertificateView(APIView):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        existing = Certificate.objects.filter(user=request.user, course=course).first()
        if existing:
            return Response({
                "error": "You already have a certificate for this course.",
                "pdf_url": request.build_absolute_uri(existing.pdf_file.url)
            }, status=400)

        try:
            cert = generate_certificate(request.user, course)
        except IntegrityError as e:
            logger.error(f"IntegrityError: {str(e)}")
            return Response({
                "error": "An error occurred while generating the certificate. Possibly a duplicate.",
                "details": str(e)
            }, status=400)
        except Exception as e:
            logger.error(f"Error during certificate generation: {str(e)}")
            return Response({
                "error": "An error occurred while generating the certificate.",
                "details": str(e)
            }, status=500)

        return Response({
            "message": "Certificate generated successfully.",
            "pdf_url": request.build_absolute_uri(cert.pdf_file.url)
        })

def all_exercises_completed(student, lesson):
    exercises = Exercise.objects.filter(lesson=lesson)
    if not exercises.exists():
        return True

    latest_attempt = LessonAttempt.objects.filter(student=student, lesson=lesson).order_by('-created_at').first()
    if not latest_attempt:
        return False

    correct_ids = set()
    for ans in latest_attempt.answers:
        if ans.get('is_correct'):
            correct_ids.add(ans.get('exercise_id'))

    return all(e.id in correct_ids for e in exercises)


class ProjectToRChatListView(APIView):

    def get(self, request):
        chats = ProjectToRChat.objects.filter(user=request.user).order_by('-created_at')
        serializer = ProjectToRChatSerializer(chats, many=True)
        return Response(serializer.data)

    def post(self, request):
        topic = request.data.get('topic', '')
        if not topic:
            return Response({'error': 'Topic is required'}, status=400)
        chat = ProjectToRChat.objects.create(user=request.user, topic=topic)
        return Response({'chat_id': chat.id}, status=201)

class ProjectToRHistoryView(APIView):

    def get(self, request, chat_id):
        chat = ProjectToRChat.objects.filter(user=request.user, id=chat_id).first()
        if not chat:
            return Response({'error': 'Not found'}, status=404)
        messages = chat.messages.order_by('timestamp')
        serializer = ProjectToRMessageSerializer(messages, many=True)
        return Response({
            'chat_id': chat.id,
            'topic': chat.topic,
            'messages': serializer.data
        })

    def delete(self, request, chat_id):
        chat = ProjectToRChat.objects.filter(user=request.user, id=chat_id).first()
        if not chat:
            return Response({'error': 'Not found'}, status=404)
        chat.delete()
        return Response({'message': 'Chat and all associated messages deleted.'}, status=204)

class ProjectToRSendMessageView(APIView):

    def post(self, request, chat_id):
        chat = ProjectToRChat.objects.filter(user=request.user, id=chat_id).first()
        if not chat:
            return Response({'error': 'Not found'}, status=404)
        content = request.data.get('content', '')
        if not content:
            return Response({'error': 'Content required'}, status=400)
        ProjectToRMessage.objects.create(chat=chat, role='user', content=content)
        history = chat.messages.order_by('timestamp')
        history_text = ""
        for m in history:
            history_text += f"{m.role}: {m.content}\n"
        try:
            response = requests.post(
                'https://microservice-quanta.up.railway.app/pet',
                json={
                    "question": content,
                    "input": history_text,
                    "language": ""
                },
                timeout=30
            )
            ai_text = response.json().get("result", "AI error")
        except Exception as e:
            ai_text = f"Error: {str(e)}"
        ProjectToRMessage.objects.create(chat=chat, role='assistant', content=ai_text)
        messages = chat.messages.order_by('timestamp')
        serializer = ProjectToRMessageSerializer(messages, many=True)
        return Response({
            'chat_id': chat.id,
            'messages': serializer.data
        })

def replace_math_symbols(text):
    import re
    text = re.sub(r"\\\((.*?)\\\)", r"\1", text)  # убираем \( ... \)
    text = text.replace(r"\times", "×")  # заменяем \times на ×
    return text


def split_text(text, font_name, font_size, max_width):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        if stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def draw_rich_text_line(p, x, y, text, font_regular, font_bold, font_size):
    import re
    pattern = r"\*\*(.+?)\*\*"
    parts = re.split(pattern, replace_math_symbols(text))
    is_bold = False
    cursor_x = x

    for part in parts:
        font = font_bold if is_bold else font_regular
        p.setFont(font, font_size)
        p.drawString(cursor_x, y, part)
        cursor_x += stringWidth(part, font, font_size)
        is_bold = not is_bold


def render_markdown_pdf(text, buffer):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    from reportlab.pdfbase.pdfmetrics import stringWidth
    import re

    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2 * cm
    left = 2 * cm
    max_text_width = width - left - 2 * cm
    code_bg = HexColor("#f5f5f5")
    code_font = "Courier"
    normal_font = "Helvetica"
    bold_font = "Helvetica-Bold"

    lines = text.splitlines()
    in_code = False
    code_block = []

    for i, line in enumerate(lines + [""]):
        # --- CODE BLOCK ---
        if line.strip().startswith("```"):
            if in_code:
                # Draw code block
                p.setFont(code_font, 11)
                p.setFillColor(code_bg)
                block_height = 0.7 * cm * len(code_block)
                p.rect(left - 0.2*cm, y - block_height + 0.2*cm, width - 4*cm, block_height, fill=1, stroke=0)
                p.setFillColor(HexColor("#333333"))
                cy = y - 0.4*cm
                for code_line in code_block:
                    p.drawString(left, cy, code_line)
                    cy -= 0.7*cm
                y -= 0.7*cm * len(code_block) + 0.5*cm
                code_block = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_block.append(line)
            continue

        # --- HEADINGS ---
        if line.startswith("###### "):
            p.setFillColor(HexColor("#4a4a4a"))
            draw_rich_text_line(p, left, y, line[7:], normal_font, bold_font, 10)
            y -= 0.7 * cm
        elif line.startswith("##### "):
            p.setFillColor(HexColor("#4a4a4a"))
            draw_rich_text_line(p, left, y, line[6:], normal_font, bold_font, 11)
            y -= 0.8 * cm
        elif line.startswith("#### "):
            p.setFillColor(HexColor("#4a4a4a"))
            draw_rich_text_line(p, left, y, line[5:], normal_font, bold_font, 12)
            y -= 0.9 * cm
        elif line.startswith("### "):
            p.setFillColor(HexColor("#264653"))
            draw_rich_text_line(p, left, y, line[4:], normal_font, bold_font, 13)
            y -= 1 * cm
        elif line.startswith("## "):
            p.setFillColor(HexColor("#2a9d8f"))
            draw_rich_text_line(p, left, y, line[3:], normal_font, bold_font, 16)
            y -= 1 * cm

        # --- UNORDERED LIST ---
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            p.setFont(normal_font, 12)
            p.setFillColor(HexColor("#333333"))
            bullet_text = "• " + line.strip()[2:]
            for subline in split_text(bullet_text, normal_font, 12, max_text_width - 0.5 * cm):
                draw_rich_text_line(p, left + 0.5 * cm, y, subline, normal_font, bold_font, 12)
                y -= 0.65 * cm

        # --- ORDERED LIST ---
        elif re.match(r"\d+\.", line.strip()):
            p.setFont(normal_font, 12)
            p.setFillColor(HexColor("#333333"))
            for subline in split_text(line.strip(), normal_font, 12, max_text_width - 0.5 * cm):
                draw_rich_text_line(p, left + 0.5 * cm, y, subline, normal_font, bold_font, 12)
                y -= 0.65 * cm

        # --- HORIZONTAL RULE ---
        elif line.strip() == "---":
            y -= 0.2*cm
            p.setStrokeColor(HexColor("#a5a5a5"))
            p.line(left, y, width-left, y)
            y -= 0.5*cm

        # --- EMPTY LINE ---
        elif not line.strip():
            y -= 0.5*cm

        # --- NORMAL PARAGRAPH TEXT ---
        else:
            p.setFont(normal_font, 12)
            p.setFillColor(HexColor("#222222"))
            for subline in split_text(line, normal_font, 12, max_text_width):
                draw_rich_text_line(p, left, y, subline, normal_font, bold_font, 12)
                y -= 0.65 * cm

        # --- PAGE BREAK ---
        if y < 2 * cm:
            p.showPage()
            y = height - 2 * cm

    p.save()
    buffer.seek(0)


class ConspectPDFView(APIView):

    def post(self, request, chat_id):
        chat = ConspectChat.objects.get(id=chat_id, user=request.user)
        last_message = chat.messages.filter(role="assistant").order_by('-timestamp').first()
        if not last_message:
            return Response({"error": "Нет сообщений от ИИ."}, status=400)

        text = last_message.content

        buffer = BytesIO()
        render_markdown_pdf(text, buffer)

        filename = f"conspect_{request.user.id}_{uuid.uuid4().hex}.pdf"
        filepath = f"pdf/conspect/{filename}"
        default_storage.save(filepath, buffer)
        file_url = default_storage.url(filepath)

        delete_later(filepath, 300)

        return Response({"url": file_url})


import threading
import time

def delete_later(filepath, seconds=300):
    def deleter():
        time.sleep(seconds)
        if default_storage.exists(filepath):
            default_storage.delete(filepath)
    threading.Thread(target=deleter, daemon=True).start()

class ProjectToRPDFView(APIView):
    def post(self, request, chat_id):
        chat = ProjectToRChat.objects.filter(id=chat_id, user=request.user).first()
        if not chat:
            return Response({"error": "Chat not found"}, status=404)

        last_message = chat.messages.filter(role="assistant").order_by('-timestamp').first()
        if not last_message:
            return Response({"error": "No assistant messages found"}, status=400)

        text = last_message.content
        buffer = BytesIO()
        render_markdown_pdf(text, buffer)

        filename = f"project_tor_{request.user.id}_{uuid.uuid4().hex}.pdf"
        filepath = f"pdf/project_tor/{filename}"
        default_storage.save(filepath, buffer)
        file_url = default_storage.url(filepath)

        delete_later(filepath, 300)

        return Response({"url": file_url})

class ProgrammingLanguagesListView(View):

    def get(self, request):
        languages = ProgrammingLanguage.objects.all().order_by('id')
        data = []
        for lang in languages:
            courses_count = Course.objects.filter(language=lang).count()
            data.append({
                "id": lang.id,
                "name": lang.name,
                "courses": courses_count,
            })
        return JsonResponse(data, safe=False)

class ChatHistoryView(View):
    def get(self, request):
        chat, _ = Chat.objects.get_or_create(id=1)
        messages = [
            {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
            for msg in chat.messages.order_by('timestamp')
        ]
        return JsonResponse(messages, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class ChatWithAIView(View):
    def post(self, request):
        try:
            body = json.loads(request.body)
            user_message = body.get("message", "")
            if not user_message:
                return JsonResponse({"error": "No message provided"}, status=400)

            chat, _ = Chat.objects.get_or_create(id=1)
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in chat.messages.order_by('timestamp')
            ]
            messages.append({"role": "user", "content": user_message})

            answer = ask_ai(messages)

            ChatMessage.objects.create(chat=chat, role="user", content=user_message)
            ChatMessage.objects.create(chat=chat, role="assistant", content=answer)

            return JsonResponse({"text": answer})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class AllAppliesView(APIView):
    def get(self, request):
        authors = Author.objects.all().select_related('user')
        data = []
        for author in authors:
            data.append({
                "author_id": author.user.id,
                "author_username": author.user.username,
                "author_status": author.author_status,
                "author_reject_reason": author.author_reject_reason or "",
                "journalist_status": author.journalist_status,
                "journalist_reject_reason": author.journalist_reject_reason or "",
            })
        return Response(data)


class ApproveApplyView(APIView):
    def post(self, request, user_id, role):
        author = get_object_or_404(Author, user__id=user_id)
        if role == "author" and author.author_status == "pending":
            author.author_status = "approved"
            author.author_reject_reason = ""
            author.save()
            return Response({"message": "Author application approved."})
        elif role == "journalist" and author.journalist_status == "pending":
            author.journalist_status = "approved"
            author.journalist_reject_reason = ""
            author.save()
            return Response({"message": "Journalist application approved."})
        return Response({"error": "No pending application found."}, status=400)

class RejectApplyView(APIView):
    def post(self, request, user_id, role):
        author = get_object_or_404(Author, user__id=user_id)
        reason = request.data.get("reason", "")
        if role == "author" and author.author_status == "pending":
            author.author_status = "rejected"
            author.author_reject_reason = reason
            author.save()
            return Response({"message": "Author application rejected."})
        elif role == "journalist" and author.journalist_status == "pending":
            author.journalist_status = "rejected"
            author.journalist_reject_reason = reason
            author.save()
            return Response({"message": "Journalist application rejected."})
        return Response({"error": "No pending application found."}, status=400)


class ChangeRoleView(APIView):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        # Нельзя менять роль суперюзеру
        if user.is_superuser:
            return Response({"error": "You cannot change role of a superuser."}, status=403)

        # Нельзя менять роль модератору (у кого есть student.moderator_profile)
        is_moderator = hasattr(user, "student") and hasattr(user.student, "moderator_profile")
        if is_moderator:
            return Response({"error": "You cannot change role of a moderator."}, status=403)

        # Получить/создать Author
        author, _ = Author.objects.get_or_create(user=user)

        new_role = request.data.get("role")
        if new_role not in ["student", "author", "journalist", "author_journalist"]:
            return Response({"error": "Invalid role."}, status=400)

        if new_role == "student":
            author.author_status = "none"
            author.is_author = False
            author.journalist_status = "none"
            author.is_journalist = False
        elif new_role == "author":
            author.author_status = "approved"
            author.is_author = True
            author.journalist_status = "none"
            author.is_journalist = False
        elif new_role == "journalist":
            author.author_status = "none"
            author.is_author = False
            author.journalist_status = "approved"
            author.is_journalist = True
        elif new_role == "author_journalist":
            author.author_status = "approved"
            author.is_author = True
            author.journalist_status = "approved"
            author.is_journalist = True

        author.author_reject_reason = ""
        author.journalist_reject_reason = ""
        author.save()

        # Обновить роль у студента, если есть
        try:
            student = user.student
            if author.is_author and author.is_journalist:
                student.role = "author_journalist"
            elif author.is_author:
                student.role = "author"
            elif author.is_journalist:
                student.role = "journalist"
            else:
                student.role = "student"
            student.save()
        except Exception:
            pass

        return Response({"message": f"Role changed to {new_role}."})

class DeactivateUserView(APIView):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        try:
            student = user.student
        except Student.DoesNotExist:
            # Если нет student профиля, просто создаём его на лету
            student = Student.objects.create(user=user)
        if student.is_scheduled_for_deletion:
            return Response({"error": "User is already scheduled for deletion."}, status=400)
        user.is_active = False
        user.save()
        student.deletion_requested_at = timezone.now()
        student.is_scheduled_for_deletion = True
        student.save()
        send_mail(
            subject="Ваш аккаунт будет удалён через 7 дней",
            message="Ваш аккаунт деактивирован модератором и будет удалён через 7 дней. Если это ошибка, обратитесь к администрации.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
        return Response({"message": "User deactivated and scheduled for deletion."}, status=200)


class RestoreUserView(APIView):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        try:
            student = user.student
        except Student.DoesNotExist:
            return Response({"error": "No student profile."}, status=404)
        if not student.is_scheduled_for_deletion:
            return Response({"error": "User is not scheduled for deletion."}, status=400)
        user.is_active = True
        user.save()
        student.deletion_requested_at = None
        student.is_scheduled_for_deletion = False
        student.save()
        send_mail(
            subject="Ваш аккаунт восстановлен",
            message="Ваш аккаунт восстановлен модератором. Теперь вы можете снова пользоваться платформой.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
        return Response({"message": "User restored."})


class UsersListView(APIView):
    def get(self, request):
        users = User.objects.filter(is_superuser=False)
        data = []
        for user in users:
            is_moderator = hasattr(user, "student") and hasattr(user.student, "moderator_profile")
            if is_moderator:
                continue
            role = None
            try:
                role = user.student.role
                deactivation_status = user.student.is_scheduled_for_deletion
                deactivation_date = user.student.deletion_requested_at
            except Exception:
                role = "unknown"
            data.append({
                "id": user.id,
                "username": user.username,
                "role": role,
                "email": user.email,
                "deactivation_status": deactivation_status,
                "deactivation_date": deactivation_date
            })
        return Response(data)


class AdvertisementListCreateView(ListCreateAPIView):
    pagination_class = None
    queryset = Advertisement.objects.all().order_by('id')
    serializer_class = AdvertisementSerializer

class AdvertisementEditView(RetrieveUpdateDestroyAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

class FinalExamCreateView(APIView):
    def post(self, request, course_id):
        course = Course.objects.get(id=course_id)
        # Проверка: если экзамен уже есть, верни ошибку
        if hasattr(course, "final_exam"):
            return Response({"error": "Final exam for this course already exists."}, status=400)
        data = request.data
        exam = FinalExam.objects.create(
            course=course,
            title=data.get("title", ""),
            duration_minutes=data.get("duration_minutes", 30),
            max_attempts=data.get("max_attempts", 3)
        )
        for q in data.get("questions", []):
            question = FinalExamQuestion.objects.create(
                exam=exam,
                text=q["text"]
            )
            for opt in q.get("options", []):
                FinalExamOption.objects.create(
                    question=question,
                    text=opt["text"],
                    is_correct=opt["is_correct"]
                )
        return Response({"id": exam.id, "detail": "Exam created"}, status=201)

class FinalExamDetailView(RetrieveAPIView):
    queryset = FinalExam.objects.all()
    serializer_class = FinalExamSerializer

    def get_object(self):
        course_id = self.kwargs["course_id"]
        return FinalExam.objects.get(course_id=course_id)

class FinalExamStartView(APIView):
    def post(self, request, course_id):
        student = request.user.student
        course = Course.objects.get(id=course_id)
        exam = course.final_exam

        attempts_count = FinalExamAttempt.objects.filter(student=student, exam=exam).count()
        max_attempts = exam.max_attempts

        last_attempt = FinalExamAttempt.objects.filter(student=student, exam=exam).order_by('-attempt_number').first()
        max_attempts = exam.max_attempts
        if last_attempt and not last_attempt.is_completed:
            return Response({"error": "You already have an unfinished attempt."}, status=400)

        attempt_number = (last_attempt.attempt_number if last_attempt else 0) + 1

        if attempt_number > max_attempts:
            return Response({"error": "No more attempts available"}, status=403)

        attempt = FinalExamAttempt.objects.create(
            student=student,
            exam=exam,
            attempt_number=attempt_number
        )
        serializer = FinalExamAttemptSerializer(attempt)
        return Response(serializer.data, status=201)

class FinalExamSubmitView(APIView):
    def post(self, request, course_id):
        student = request.user.student
        exam = FinalExam.objects.get(course_id=course_id)
        # ищем текущий незавершённый attempt
        attempt = FinalExamAttempt.objects.filter(student=student, exam=exam, is_completed=False).order_by('-started_at').first()
        if not attempt:
            return Response({"error": "Нет активной попытки экзамена."}, status=400)

        data = request.data.get("answers", {})
        if not data:
            return Response({"error": "No answers."}, status=400)

        total = exam.questions.count()
        correct = 0
        detailed = []

        for question in exam.questions.all():
            q_id = str(question.id)
            selected_options = data.get(q_id, [])
            real_options = set([str(opt.id) for opt in question.options.filter(is_correct=True)])
            if set(selected_options) == real_options and real_options:
                correct += 1
                detailed.append({"question_id": q_id, "correct": True})
            else:
                detailed.append({"question_id": q_id, "correct": False})

        score = round((correct / total) * 100, 2) if total > 0 else 0
        attempt.answers = data
        attempt.score = score
        attempt.passed = True
        attempt.is_completed = True
        attempt.finished_at = timezone.now()
        attempt.save()

        num_attempts = FinalExamAttempt.objects.filter(student=student, exam=exam).count()
        can_retry = num_attempts < exam.max_attempts

        return Response({
            "score": score,
            "details": detailed,
            "max_score": 100,
            "attempt_number": attempt.attempt_number,
            "can_retry": can_retry,
        }, status=200)




class FinalExamAttemptsListView(ListAPIView):
    serializer_class = FinalExamAttemptSerializer

    def get(self, request, course_id):
        student = request.user.student
        exam = FinalExam.objects.get(course_id=course_id)
        attempts = FinalExamAttempt.objects.filter(student=student, exam=exam)
        serializer = FinalExamAttemptSerializer(attempts, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        student = self.request.user.student
        exam_id = self.kwargs['exam_id']
        return FinalExamAttempt.objects.filter(student=student, exam_id=exam_id).order_by('-started_at')