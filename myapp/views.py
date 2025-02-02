from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Course, Lesson, Student, Review
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    CourseSerializer,
    LessonSerializer,
    ModuleSerializer,
    ReviewSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "message": "Registration successful!",
            "access": access_token,
            "refresh": str(refresh)
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "message": "Login successful!",
            "access": access_token,
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)

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
    student = getattr(request.user, 'student', None)
    if not student:
        return Response({"error": "Student profile not found"}, status=404)

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
@permission_classes([IsAuthenticated])
def course(request, id):
    try:
        course = get_object_or_404(Course.objects.prefetch_related('modules', 'modules__lessons', 'reviews'), id=id)
        student = request.user.student  # Get authenticated student

        # Handle review submission (POST)
        if request.method == 'POST':
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

        # Check if the student has already reviewed
        existing_review = Review.objects.filter(user=student, course=course).first()
        can_write_review = not existing_review and student.is_enrolled(course)

        write_review_section = {
            "allowed": can_write_review,
            "message": "You can write a review for this course" if can_write_review else "You have already reviewed this course",
            "form_fields": {
                "rating": "Integer (1-5)",
                "feedback": "Optional text"
            }
        } if can_write_review else None

        response_data = {
            "Overview": course_data,
            "Curriculum": module_serializer.data,
            "Author": author_data,
            "Reviews": {
                "existing_reviews": reviews_data,
                "write_review": write_review_section
            }
        }

        return Response(response_data, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


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
        "video_url": lesson.video_url if lesson.video_url else None,
        "uploaded_video": lesson.uploaded_video.url if lesson.uploaded_video else None,
    }

    return Response(lesson_data, status=status.HTTP_200_OK)
