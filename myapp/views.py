from django.shortcuts import get_object_or_404, redirect
from django.utils.text import slugify
from django.urls import reverse
from django.http import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Course, Lesson, Student
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    CourseSerializer,
    LessonSerializer,
    ModuleSerializer,
)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    if 'Authorization' in request.headers:
        return Response({"message": "Вы уже зарегистрированы и авторизованы."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        Student.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Registration successful!",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if 'Authorization' in request.headers:
        return Response({"message": "Вы уже авторизованы."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            "message": "Login successful!",
            "access": access_token,
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='Strict'
        )

        response['Authorization'] = f'Bearer {access_token}'
        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

    response = Response({"message": "Вы успешно вышли из системы."}, status=status.HTTP_204_NO_CONTENT)
    response.delete_cookie('refresh_token')
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    if not request.user.is_authenticated:
        return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    student = getattr(request.user, 'student', None)
    if not student:
        return Response({"error": "Student profile not found"}, status=404)

    serializer = ProfileSerializer(student)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def course_list(request):
    courses = Course.objects.all()
    if not courses:
        return Response({'message': 'No courses available'})
    serializer = CourseSerializer(courses, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def course(request, id, title=None):
    course = get_object_or_404(Course.objects.prefetch_related('modules', 'modules__lessons'), id=id)
    course_data = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "course_image": course.course_image.url if course.course_image else None,
        "duration": course.duration,
        "students_count": course.students_count if hasattr(course, 'students_count') else 0,
        "lessons_count": course.lessons_count if hasattr(course, 'lessons_count') else 0,
        "level": course.level,
        "rating": str(course.rating) if course.rating else "N/A",
    }

    modules = course.modules.all()
    module_serializer = ModuleSerializer(modules, many=True)

    author_data = {
        "id": course.author.id if course.author else None,
        "username": course.author.user.username if course.author and course.author.user else None,
        "about": course.author.about if course.author else None,
        "avatar": course.author.avatar.url if course.author and course.author.avatar else None,
    }

    response_data = {
        "Overview": course_data,
        "Curriculum": module_serializer.data,
        "Author": author_data,
        "Reviews": "Soon..."
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def lesson(request, id, lessonid=None, name=None):
    course = get_object_or_404(Course, id=id)
    lesson = get_object_or_404(Lesson, id=lessonid, module__course=course)
    lesson_data = {
        "id": lesson.id,
        "name": lesson.name,
        "description": lesson.short_description,
        "content": lesson.content,
        "duration": lesson.duration,
        "video_url": lesson.video_url,
        "uploaded_video": lesson.uploaded_video.url if lesson.uploaded_video else None,
    }

    return Response(lesson_data, status=status.HTTP_200_OK)