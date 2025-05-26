from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Exercise, ExerciseOption, ExerciseSolution, ExerciseAttempt
from .serializers import (
    ExerciseSerializer, ExerciseOptionSerializer,
    ExerciseSolutionSerializer, ExerciseAttemptSerializer
)
from main.models import Course, Lesson
from rest_framework import status
from exercises.ai_helper import get_code_hint

class ExerciseListCreate(generics.ListCreateAPIView):
    queryset = Exercise.objects.all().order_by('id')
    serializer_class = ExerciseSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        module_id = self.kwargs['module_id']
        lesson_id = self.kwargs['lesson_id']

        lesson = Lesson.objects.get(
            module__course__id=course_id,
            module__module_id=module_id,
            lesson_id=lesson_id
        )
        return Exercise.objects.filter(lesson=lesson)


class ExerciseDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExerciseSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        module_id = self.kwargs['module_id']
        lesson_id = self.kwargs['lesson_id']
        return Exercise.objects.filter(
            lesson__module__course__id=course_id,
            lesson__module__module_id=module_id,
            lesson__lesson_id=lesson_id
        )

class AllExercises(APIView):
    def get(self, request):
        courses = Course.objects.all()
        result = []
        for course in courses:
            course_modules = []
            modules = course.modules.all()
            for module in modules:
                module_lessons = []
                lessons = module.lessons.all()
                for lesson in lessons:
                    exercises = lesson.exercises.all()
                    if exercises.exists():
                        lesson_data = {
                            "lesson_id": lesson.lesson_id,
                            "lesson": lesson.name,
                            "exercises": [
                                {
                                    "id": exercise.id,
                                    "type": exercise.type,
                                    "title": exercise.title,
                                    "description": exercise.description,
                                }
                                for exercise in exercises
                            ]
                        }
                        module_lessons.append(lesson_data)
                if module_lessons:
                    module_data = {
                        "module_id": module.module_id,
                        "module": module.module,
                        "lessons": module_lessons
                    }
                    course_modules.append(module_data)
            if course_modules:
                course_data = {
                    "id": course.id,
                    "course": course.title,
                    "modules": course_modules
                }
                result.append(course_data)
        return Response(result)

class ExerciseOptionListCreate(generics.ListCreateAPIView):
    serializer_class = ExerciseOptionSerializer

    def get_queryset(self):
        exercise_id = self.kwargs['exercise_id']
        return ExerciseOption.objects.filter(exercise__id=exercise_id)

    def perform_create(self, serializer):
        exercise_id = self.kwargs['exercise_id']
        exercise = Exercise.objects.get(id=exercise_id)
        serializer.save(exercise=exercise)

class ExerciseOptionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExerciseOptionSerializer

    def get_queryset(self):
        exercise_id = self.kwargs['exercise_id']
        return ExerciseOption.objects.filter(exercise__id=exercise_id)

class ExerciseAttemptListCreate(APIView):
    def post(self, request, course_id, module_id, lesson_id, *args, **kwargs):
        attempts_data = request.data if isinstance(request.data, list) else request.data.get("attempts", [])
        user = request.user
        results = []
        correct_count = 0

        course = Course.objects.get(id=course_id)
        prompt_language = getattr(course.language, "code", None) if hasattr(course, "language") else None

        for attempt in attempts_data:
            exercise_id = attempt.get("exercise_id")
            selected_option = attempt.get("selected_option")
            submitted_code = attempt.get("submitted_code")
            submitted_output = attempt.get("submitted_output")
            request_hint = attempt.get("request_hint", False)

            try:
                exercise = Exercise.objects.get(
                    id=exercise_id,
                    lesson__lesson_id=lesson_id,
                    lesson__module__module_id=module_id,
                    lesson__module__course__id=course_id
                )
            except Exercise.DoesNotExist:
                continue

            is_correct = False
            hint = None

            if exercise.type == "quiz" and selected_option:
                is_correct = exercise.options.filter(id=selected_option, is_correct=True).exists()
                ExerciseAttempt.objects.create(
                    student=user.student,
                    exercise=exercise,
                    selected_option_id=selected_option,
                    is_correct=is_correct
                )
            elif exercise.type == "code" and submitted_output is not None:
                correct_output = exercise.solution.expected_output.strip()
                submitted = (submitted_output or "").strip()
                is_correct = correct_output == submitted
                ExerciseAttempt.objects.create(
                    student=user.student,
                    exercise=exercise,
                    submitted_code=submitted_code,
                    submitted_output=submitted_output,
                    is_correct=is_correct
                )
                if not is_correct and request_hint:
                    hint = get_code_hint(
                        student_code=submitted_code,
                        student_output=submitted_output,
                        expected_output=correct_output,
                        prompt_language=prompt_language
                    )
            results.append({
                "exercise_id": exercise.id,
                "is_correct": is_correct,
                "hint": hint,
            })
            if is_correct:
                correct_count += 1

        return Response({
            "results": results,
            "correct_count": correct_count,
            "total": len(attempts_data)
        }, status=status.HTTP_201_CREATED)



class ExerciseAttemptDetail(generics.RetrieveAPIView):
    serializer_class = ExerciseAttemptSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        module_id = self.kwargs['module_id']
        lesson_id = self.kwargs['lesson_id']
        exercise_id = self.kwargs['exercise_id']
        return ExerciseAttempt.objects.filter(
            exercise__id=exercise_id,
            exercise__lesson__lesson_id=lesson_id,
            exercise__lesson__module__module_id=module_id,
            exercise__lesson__module__course__id=course_id,
            student=self.request.user.student
        )