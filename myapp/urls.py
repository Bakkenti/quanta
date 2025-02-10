from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import signup, login, auth_logout

urlpatterns = [
    path('courses/', views.course_list, name='Список курсов'),
    path('courses/<int:id>/', views.course, name='Страница курса'),
    path('courses/<int:id>/<int:lessonid>/', views.lesson, name='Страница урока'),

    path('profile/', views.profile, name='Профиль'),

    path('login/', login.as_view(), name='login'),
    path('signup/', signup.as_view(), name='signup'),
    path('logout/', views.auth_logout, name='logout'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/', include('allauth.urls')),
]