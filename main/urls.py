from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from dj_rest_auth.views import LoginView, LogoutView

from .views import (
    Logout,
    Profile,
    CourseList,
    CourseDetail,
    LessonDetail,
    MostPopularCourse,
    BestCourse,
    Advertisement,
    AuthorCourseListCreate, AuthorCourseEdit,
    AuthorModuleListCreate, AuthorModuleEdit,
    AuthorLessonListCreate, AuthorLessonEdit, CustomLogin, EnrollCourse, UnenrollCourse, MyCourses
)

urlpatterns = [
    path('login/', CustomLogin.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('signup/', include('dj_rest_auth.registration.urls')),
    path('profile/', Profile.as_view(), name='profile'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/', LessonDetail.as_view(), name='lesson_detail'),
    path('courses/', CourseList.as_view(), name='course_list'),
    path('courses/<int:id>/', CourseDetail.as_view(), name='course_detail'),
    path('courses/<int:course_id>/enroll/', EnrollCourse.as_view(), name='enroll-course'),
    path('courses/<int:course_id>/unenroll/', UnenrollCourse.as_view(), name='unenroll-course'),
    path('mycourses/', MyCourses.as_view(), name='my-courses'),
    path('author/courses/', AuthorCourseListCreate.as_view(), name='author_course_list_create'),
    path('author/course/<int:course_id>/', AuthorCourseEdit.as_view(), name='author_course_edit'),
    path('author/course/<int:course_id>/modules/', AuthorModuleListCreate.as_view(), name='author_module_list_create'),
    path('author/course/<int:course_id>/module/<int:module_id>/', AuthorModuleEdit.as_view(), name='author_module_edit'),
    path('author/course/<int:course_id>/module/<int:module_id>/lessons/', AuthorLessonListCreate.as_view(), name='author_lesson_list_create'),
    path('author/course/<int:course_id>/module/<int:module_id>/lesson/<int:lesson_id>/', AuthorLessonEdit.as_view(), name='author_lesson_edit'),
    path('mostpopularcourse/', MostPopularCourse.as_view(), name='most_popular_course'),
    path('bestcourse/', BestCourse.as_view(), name='best_course'),
    path('advertisement/', Advertisement.as_view(), name='advertisement'),

]
