from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils.text import slugify

urlpatterns = [
    path('courses/', views.course_list, name='course-list'),
    path('courses/<int:id>/', views.course, name='course-page'),
    path('courses/<int:id>/<int:lessonid>/', views.lesson, name='lesson'),
    path('signup/', views.signup, name='registration'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
