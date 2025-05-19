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
    AdvertisementView,
    AuthorCourseListCreateView, AuthorCourseEditView,
    AuthorModuleListCreateView, AuthorModuleEditView,
    AuthorLessonListCreateView, AuthorLessonEditView, CustomLoginView
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('signup/', include('dj_rest_auth.registration.urls')),
    path('profile/', Profile.as_view(), name='profile'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/', LessonDetail.as_view(), name='lesson_detail'),
    path('courses/', CourseList.as_view(), name='course_list'),
    path('courses/<int:id>/', CourseDetail.as_view(), name='course_detail'),
    path('author/courses/', AuthorCourseListCreateView.as_view(), name='author_course_list_create'),
    path('author/course/<int:course_id>/', AuthorCourseEditView.as_view(), name='author_course_edit'),
    path('author/course/<int:course_id>/modules/', AuthorModuleListCreateView.as_view(), name='author_module_list_create'),
    path('author/course/<int:course_id>/module/<int:module_id>/', AuthorModuleEditView.as_view(), name='author_module_edit'),
    path('author/course/<int:course_id>/module/<int:module_id>/lessons/', AuthorLessonListCreateView.as_view(), name='author_lesson_list_create'),
    path('author/course/<int:course_id>/module/<int:module_id>/lesson/<int:lesson_id>/', AuthorLessonEditView.as_view(), name='author_lesson_edit'),
    path('mostpopularcourse/', MostPopularCourseView.as_view(), name='most_popular_course'),
    path('bestcourse/', BestCourseView.as_view(), name='best_course'),
    path('advertisement/', AdvertisementView.as_view(), name='advertisement'),
]
