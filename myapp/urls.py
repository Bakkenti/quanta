from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import signup, login as custom_login, auth_logout, most_popular_course, best_course, advertisement

urlpatterns = [
    path('courses/', views.course_list, name='Список курсов'),
    path('courses/<int:id>/', views.course, name='Страница курса'),
    path('courses/<int:id>/<int:lessonid>/', views.lesson, name='Страница урока'),

    path('profile/', views.profile, name='Профиль'),
    path('login/', custom_login.as_view(), name='login'),
    path('signup/', signup.as_view(), name='signup'),

    path('logout/', auth_logout, name='logout'),

    path('accounts/', include('allauth.urls')),
    path('mostpopularcourse/', most_popular_course, name='most_popular_course'),
    path('bestcourse/', best_course, name='best_course'),
    path("advertisement/", advertisement.as_view(), name="advertisement"),
]
