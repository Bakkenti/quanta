from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    Signup,
    Signin,
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
    AuthorLessonListCreateView, AuthorLessonEditView
)

urlpatterns = [
    path('author/courses/', AuthorCourseListCreateView.as_view(), name='author_course_list_create'),  # Для GET и POST
    path('author/course/<int:course_id>/', AuthorCourseEditView.as_view(), name='author_course_edit'),
    path('author/course/<int:course_id>/modules/', AuthorModuleListCreateView.as_view(),
         name='author_module_list_create'),
    path('author/course/<int:course_id>/module/<int:module_id>/', AuthorModuleEditView.as_view(), name='author_module_edit'),
    path('author/course/<int:course_id>/module/<int:module_id>/lessons/', AuthorLessonListCreateView.as_view(),
         name='author_lesson_list_create'),
    path('author/course/<int:course_id>/module/<int:module_id>/lesson/<int:lesson_id>/', AuthorLessonEditView.as_view(), name='author_lesson_edit'),
    path('courses/', CourseList.as_view(), name='course_list'),
    path('courses/<int:id>/', CourseDetail.as_view(), name='course_detail'),
    path('courses/<int:id>/<int:lessonid>/', LessonDetail.as_view(), name='lesson_detail'),
    path('login/', Signin.as_view(), name='login'),
    path('signup/', Signup.as_view(), name='signup'),
    path('logout/', Logout.as_view(), name='logout'),
    path('profile/', Profile.as_view(), name='profile'),
    path('accounts/', include('allauth.urls')),
    path('mostpopularcourse/', MostPopularCourseView.as_view(), name='most_popular_course'),
    path('bestcourse/', BestCourseView.as_view(), name='best_course'),
    path('advertisement/', AdvertisementView.as_view(), name='advertisement'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
