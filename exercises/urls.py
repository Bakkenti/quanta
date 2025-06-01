from django.urls import path
from .views import (
    AuthorExerciseListCreate,
    StudentExerciseList, StudentExerciseDetail, LessonBulkSubmit, CodeHintView, BulkDeleteExercises, EditMCQ,
    EditCode
)

urlpatterns = [
    path('author/courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/exercises/', AuthorExerciseListCreate.as_view(), name='author-exercise-list-create'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/exercises/', StudentExerciseList.as_view(), name='student-exercise-list'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/exercises/<int:pk>/', StudentExerciseDetail.as_view(), name='student-exercise-detail'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/submit-answer/', LessonBulkSubmit.as_view(), name='lesson-bulk-submit'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/exercises/<int:exercise_id>/hint/', CodeHintView.as_view(), name='code-hint'),
    path('author/courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/exercises/delete/', BulkDeleteExercises.as_view(), name='author-exercise-bulk-delete'),
    path('author/courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/exercises/edit-mcq/', EditMCQ.as_view(), name='bulk-edit-mcq-exercises'),
    path('author/courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/exercises/edit-code/', EditCode.as_view(), name='bulk-edit-code-exercises'),

]
