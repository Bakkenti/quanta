from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.parsers import MultiPartParser, FormParser
from dj_rest_auth.views import LoginView
from .models import Course, Lesson, Student, Author, Review, Module, MostPopularCourse, BestCourse, Advertisement, Category, SiteReview
from .serializers import (RegistrationSerializer, CategorySerializer, CourseSerializer, LessonSerializer, ModuleSerializer, ReviewSerializer, ProfileSerializer, AdvertisementSerializer, UserSerializer, SiteReviewSerializer)
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.db.models import Avg

import logging


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
        response = super().post(request, *args, **kwargs)
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        else:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if 'user' in response.data:
                username = response.data['user'].get('username')
                user = User.objects.filter(username=username).first()
        if user:
            response.data['user'] = UserSerializer(user).data
        return response

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

    def get(self, request):
        user = request.user

        try:
            student = user.student
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        enrolled_courses = student.enrolled_courses.all()
        enrolled_courses_dict = {course.id: course.title for course in enrolled_courses}

        return Response({
            "username": user.username,
            "email": user.email,
            "avatar": student.avatar.url if student.avatar else None,
            "role": student.role,
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

class Advertisement(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Advertisement.objects.all().order_by("-created_at")
    serializer_class = AdvertisementSerializer


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
        average_site_rating = SiteReview.objects.aggregate(avg_rating=Avg('rating'))['avg_rating']
        average_site_rating = round(average_site_rating, 2) if average_site_rating is not None else None
        return Response({
            "total_students": students_count,
            "total_authors": authors_count,
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
