from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404, redirect
from .models import Course, Lesson
from .serializers import RegistrationSerializer, LoginSerializer, CourseSerializer, LessonSerializer, ModuleSerializer
from datetime import timedelta
from django.utils import timezone


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        student = serializer.save()
        refresh = RefreshToken.for_user(student)

        return Response({
            "message": "Registration successful!",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Respond with tokens
        response = Response({
            "message": "Login successful!",
            "access": access_token,
        }, status=status.HTTP_200_OK)

        # Set refresh_token in cookies
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='Strict'
        )

        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    return Response(status=204)

@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        return Response({"error": "Refresh token not provided"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        refresh = RefreshToken(refresh_token)
        new_access_token = refresh.access_token
        return Response({"access": str(new_access_token)}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def course_list(request):
    courses = Course.objects.all()
    if not courses:
        return Response({'message': 'No courses available'})
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def course(request, id, title=None):
    course = get_object_or_404(Course, id=id)
    if title is None or course.title != title:
        return redirect(f'/courses/{id}/{course.title}/')

    modules = course.modules.all()
    module_serializer = ModuleSerializer(modules, many=True)

    course_data = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "course_image": course.course_image.url if course.course_image else None,
        "duration": course.duration,
        "students_count": course.students_count,
        "lessons_count": course.lessons_count,
        "level": course.level,
        "rating": str(course.rating) if course.rating else "N/A",
    }

    author_data = {
        "id": course.author.id,
        "username": course.author.username,
        "about": course.author.about
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
def lesson(request, id, title, lessonid, name=None):
    course = get_object_or_404(Course, id=id, title=title)
    lesson = get_object_or_404(Lesson, id=lessonid, course=course)
    lesson_name_slug = lesson.name.replace(' ', '-').lower()
    if name is None or name != lesson_name_slug:
        return redirect(f'/courses/{id}/{title}/lesson/{lessonid}/{lesson_name_slug}/')

    video_source = lesson.video_url if lesson.video_url else (lesson.uploaded_video.url if lesson.uploaded_video else None)

    response_data = {
        "id": lesson.id,
        "name": lesson.name,
        "video_url": video_source,
        "content": lesson.content,
    }

    return Response(response_data, status=status.HTTP_200_OK)
