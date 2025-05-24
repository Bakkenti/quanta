from django.urls import path
from . import views

urlpatterns = [
    path("courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/exercises/", views.ExerciseListCreate.as_view(), name="exercise-list-create"),
    path("courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/exercises/<int:pk>/", views.ExerciseDetail.as_view(), name="exercise-detail"),
    path("courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/exercises/attempts/", views.ExerciseAttemptListCreate.as_view(), name="exercise-attempt"),
    path('exercises/', views.AllExercises.as_view(), name='all-exercises')
]
