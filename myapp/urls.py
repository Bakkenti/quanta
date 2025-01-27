from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('courses/', views.course_list, name='Список курсов'),
    path('courses/<int:id>/', views.course, name='Страница курса'),
    path('courses/<int:id>/<int:lessonid>/', views.lesson, name='Страница урока'),
    path('signup/', views.signup, name='Регистрация'),
    path('login/', views.login, name='Авторизация'),
    path('logout/', views.logout, name='Выход'),
    path('profile/', views.profile, name='Профиль'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
