from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('courses/', views.course_list, name='course-list'),
    path('courses/<int:id>/', views.course, name='course-page'),
    path('courses/<int:id>/<str:title>/', views.course, name='course-page'),
    path('courses/<int:id>/<str:title>/lesson/', views.course, name='course-page'),
    path('courses/<int:id>/<str:title>/lesson/<int:lessonid>/', views.lesson, name='lesson'),
    path('courses/<int:id>/<str:title>/lesson/<int:lessonid>/<str:name>/', views.lesson, name='lesson-detail'),
    path('signup/', views.signup, name='registration'),
    path('login/', views.login, name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
