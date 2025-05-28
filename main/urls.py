from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from dj_rest_auth.views import LoginView, LogoutView

from .views import (
    Logout,
    Profile,
    CourseList,
    CourseDetail,
    LessonDetail,
    MostPopularCourseView,
    BestCourseView,
    Advertisement,
    AuthorCourseListCreate, AuthorCourseEdit,
    AuthorModuleListCreate, AuthorModuleEdit,
    AuthorLessonListCreate, AuthorLessonEdit, Registration, Login, EnrollCourse, UnenrollCourse, MyCourses, ProfileEdit, CategoryList, SiteStats, LessonImageUploadView, SiteReviewView
)

urlpatterns = [
    path('login/', Login.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('signup/', Registration.as_view(), name='rest_signup'),
    path('profile/', Profile.as_view(), name='profile'),
    path('profile/edit/', ProfileEdit.as_view(), name='profile-edit'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/', LessonDetail.as_view(), name='lesson_detail'),
    path('courses/', CourseList.as_view(), name='course_list'),
    path('courses/<int:id>/', CourseDetail.as_view(), name='course_detail'),
    path('courses/<int:course_id>/enroll/', EnrollCourse.as_view(), name='enroll-course'),
    path('courses/<int:course_id>/unenroll/', UnenrollCourse.as_view(), name='unenroll-course'),
    path('mycourses/', MyCourses.as_view(), name='my-courses'),
    path('author/courses/', AuthorCourseListCreate.as_view(), name='author_course_list_create'),
    path('author/courses/<int:course_id>/', AuthorCourseEdit.as_view(), name='author_course_edit'),
    path('author/courses/<int:course_id>/modules/', AuthorModuleListCreate.as_view(), name='author_module_list_create'),
    path('author/courses/<int:course_id>/modules/<int:module_id>/', AuthorModuleEdit.as_view(), name='author_module_edit'),
    path('author/courses/<int:course_id>/modules/<int:module_id>/lessons/', AuthorLessonListCreate.as_view(), name='author_lesson_list_create'),
    path('author/courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/', AuthorLessonEdit.as_view(), name='author_lesson_edit'),
    path('mostpopularcourse/', MostPopularCourseView.as_view(), name='most_popular_course'),
    path('bestcourse/', BestCourseView.as_view(), name='best_course'),
    path('advertisement/', Advertisement.as_view(), name='advertisement'),
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('site-stats/', SiteStats.as_view(), name='site-stats'),
    path('image_upload/', LessonImageUploadView.as_view(), name='ckeditor5_image_upload'),
    path('site-reviews/', SiteReviewView.as_view(), name='site-reviews'),
]
