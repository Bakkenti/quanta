from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Exercise, ExerciseOption, Lesson, LessonAttempt, HintRequestLog
from .serializers import ExerciseSerializer, LessonAttemptSerializer
from .ai_helper import execute_code, get_code_hint
from django.utils.timezone import now, timedelta
from django.utils import timezone


class AuthorExerciseListCreate(generics.ListCreateAPIView):
    serializer_class = ExerciseSerializer
    pagination_class = None

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        module_id = self.kwargs["module_id"]
        lesson_id = self.kwargs["lesson_id"]
        return Exercise.objects.filter(
            lesson__lesson_id=lesson_id,
            lesson__module__module_id=module_id,
            lesson__module__course__id=course_id
        )

    def post(self, request, course_id, module_id, lesson_id, *args, **kwargs):
        lesson = Lesson.objects.get(
            module__course__id=course_id,
            module__module_id=module_id,
            lesson_id=lesson_id
        )
        type_ = request.data.get('type')
        exercises_data = request.data.get('exercises', [])
        common_description = request.data.get('description', '')
        if not type_ or not exercises_data:
            return Response({'detail': 'Specify type and exercises list.'}, status=status.HTTP_400_BAD_REQUEST)
        created = []
        errors = []
        for idx, item in enumerate(exercises_data):
            description = item.get('description', common_description)
            serializer = ExerciseSerializer(data={
                'type': type_,
                'title': item.get('title'),
                'description': description,
            })
            if serializer.is_valid():
                exercise = serializer.save(lesson=lesson)
                if type_ == 'mcq' and 'options' in item:
                    for opt in item['options']:
                        ExerciseOption.objects.create(exercise=exercise, **opt)
                elif type_ == 'code' and 'solution' in item:
                    from .models import ExerciseSolution
                    ExerciseSolution.objects.create(exercise=exercise, **item['solution'])
                created.append(ExerciseSerializer(exercise).data)
            else:
                errors.append({'index': idx, 'errors': serializer.errors})
        if errors:
            return Response({'created': created, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'created': created}, status=status.HTTP_201_CREATED)

class StudentExerciseList(generics.ListAPIView):
    serializer_class = ExerciseSerializer
    pagination_class = None

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        module_id = self.kwargs["module_id"]
        lesson_id = self.kwargs["lesson_id"]
        return Exercise.objects.filter(
            lesson__lesson_id=lesson_id,
            lesson__module__module_id=module_id,
            lesson__module__course__id=course_id
        )


class StudentExerciseDetail(generics.RetrieveAPIView):
    serializer_class = ExerciseSerializer
    lookup_field = 'pk'
    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        module_id = self.kwargs["module_id"]
        lesson_id = self.kwargs["lesson_id"]
        return Exercise.objects.filter(
            lesson__lesson_id=lesson_id,
            lesson__module__module_id=module_id,
            lesson__module__course__id=course_id
        )


class LessonBulkSubmit(APIView):
    def post(self, request, course_id, module_id, lesson_id):
        student = request.user.student
        lesson = Lesson.objects.get(
            lesson_id=lesson_id,
            module__module_id=module_id,
            module__course__id=course_id
        )
        answers = request.data.get('answers', [])
        exercises = {e.id: e for e in Exercise.objects.filter(lesson=lesson)}
        correct_count = 0
        results = []
        for ans in answers:
            ex_id = ans.get('exercise_id')
            exercise = exercises.get(ex_id)
            res = {'exercise_id': ex_id, 'is_correct': False}
            if exercise:
                if exercise.type == 'mcq':
                    selected_option = ans.get('selected_option')
                    try:
                        option = ExerciseOption.objects.get(id=selected_option, exercise=exercise)
                        res['is_correct'] = option.is_correct
                        if option.is_correct:
                            correct_count += 1
                    except ExerciseOption.DoesNotExist:
                        res['error'] = 'Option not found'
                elif exercise.type == 'code':
                    submitted_code = ans.get('submitted_code', '')
                    expected_output = (getattr(exercise.solution, 'expected_output', '') or '').strip()

                    if exercise.language and getattr(exercise.language, "name", None):
                        lang = exercise.language.name.lower()
                    elif hasattr(exercise.lesson.module.course, "language") and exercise.lesson.module.course.language:
                        lang = exercise.lesson.module.course.language.name.lower()
                    else:
                        lang = "python"
                    stdout, stderr, exit_code = execute_code(lang, submitted_code)
                    res['submitted_output'] = stdout.strip()
                    res['expected_output'] = expected_output
                    res['is_correct'] = (stdout.strip() == expected_output)
                    if res['is_correct']:
                        correct_count += 1
                    res['stderr'] = stderr
                    res['exit_code'] = exit_code
            results.append(res)

        lesson_attempt = LessonAttempt.objects.create(
            student=student,
            lesson=lesson,
            answers=answers,
            score=correct_count
        )
        return Response({
            'attempt_id': lesson_attempt.id,
            'score': correct_count,
            'results': results
        }, status=status.HTTP_201_CREATED)

class CodeHintView(APIView):

    def get(self, request, course_id, module_id, lesson_id, exercise_id):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=401)

        time_threshold = now() - timedelta(hours=12)
        recent_count = HintRequestLog.objects.filter(user=user, requested_at__gte=time_threshold).count()
        remaining = max(0, 5 - recent_count)
        next_available = None

        if remaining == 0:
            oldest = HintRequestLog.objects.filter(user=user).order_by('requested_at').first()
            if oldest:
                next_available = max(0, int((oldest.requested_at + timedelta(hours=12) - now()).total_seconds() // 60))

        return Response({
            "remaining": remaining,
            "limit": 5,
            "next_available_in_minutes": next_available if next_available is not None else 0
        })

    def post(self, request, course_id, module_id, lesson_id, exercise_id):
        user = request.user

        limit = 5
        window_start = timezone.now() - timedelta(hours=12)
        recent_requests = HintRequestLog.objects.filter(user=user, requested_at__gte=window_start)
        recent_count = recent_requests.count()
        remaining = max(0, limit - recent_count)

        if recent_count >= limit:
            next_available_time = recent_requests.earliest("requested_at").requested_at + timedelta(hours=12)
            wait_minutes = int((next_available_time - timezone.now()).total_seconds() // 60)

            return Response({
                "error": "You have reached the maximum number of hints allowed (5 per 12 hours).",
                "next_available_in_minutes": wait_minutes,
                "limit": limit,
                "remaining": 0
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            exercise = Exercise.objects.get(
                id=exercise_id, type='code',
                lesson__lesson_id=lesson_id,
                lesson__module__module_id=module_id,
                lesson__module__course__id=course_id
            )
        except Exercise.DoesNotExist:
            return Response({"error": "Exercise not found."}, status=404)

        submitted_code = request.data.get("submitted_code", "")
        question = f"{exercise.title}\n{exercise.description or ''}"

        if exercise.language and getattr(exercise.language, "name", None):
            prompt_language = exercise.language.name.lower()
        elif hasattr(exercise.lesson.module.course, "language") and exercise.lesson.module.course.language:
            prompt_language = exercise.lesson.module.course.language.name.lower()
        else:
            prompt_language = "python"

        hint_text, fixed_code = get_code_hint(
            input_code=submitted_code,
            question=question,
            prompt_language=prompt_language
        )

        HintRequestLog.objects.create(user=user)

        return Response({
            "hint": hint_text,
            "fixed_code": fixed_code,
            "limit": limit,
            "remaining": remaining - 1
        }, status=200)

class BulkDeleteExercises(APIView):
    def delete(self, request, course_id, module_id, lesson_id):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"detail": "No IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        exercises = Exercise.objects.filter(
            id__in=ids,
            lesson__lesson_id=lesson_id,
            lesson__module__module_id=module_id,
            lesson__module__course__id=course_id
        )
        deleted_count, _ = exercises.delete()
        return Response({"deleted": deleted_count}, status=status.HTTP_200_OK)

class EditMCQ(APIView):
    def patch(self, request, course_id, module_id, lesson_id):
        updates = request.data.get('exercises', [])
        updated = []
        for item in updates:
            ex_id = item.get('exercise_id')
            try:
                exercise = Exercise.objects.get(
                    id=ex_id, type='mcq',
                    lesson__lesson_id=lesson_id,
                    lesson__module__module_id=module_id,
                    lesson__module__course__id=course_id
                )
                if "title" in item:
                    exercise.title = item["title"]
                if "description" in item:
                    exercise.description = item["description"]
                exercise.save()
                if "options" in item:
                    for opt in item["options"]:
                        opt_id = opt.get("id")
                        if opt_id:
                            try:
                                option = ExerciseOption.objects.get(id=opt_id, exercise=exercise)
                                if "text" in opt:
                                    option.text = opt["text"]
                                if "is_correct" in opt:
                                    option.is_correct = opt["is_correct"]
                                option.save()
                            except ExerciseOption.DoesNotExist:
                                continue
                        else:
                            ExerciseOption.objects.create(
                                exercise=exercise,
                                text=opt.get("text", ""),
                                is_correct=opt.get("is_correct", False)
                            )
                updated.append(ex_id)
            except Exercise.DoesNotExist:
                continue
        return Response({"updated": updated}, status=status.HTTP_200_OK)

class EditCode(APIView):
    def patch(self, request, course_id, module_id, lesson_id):
        updates = request.data.get('exercises', [])
        updated = []
        from .models import ExerciseSolution

        for item in updates:
            ex_id = item.get('exercise_id')
            try:
                exercise = Exercise.objects.get(
                    id=ex_id, type='code',
                    lesson__lesson_id=lesson_id,
                    lesson__module__module_id=module_id,
                    lesson__module__course__id=course_id
                )
                if "title" in item:
                    exercise.title = item["title"]
                if "description" in item:
                    exercise.description = item["description"]
                exercise.save()
                if "solution" in item:
                    sol = item["solution"]
                    if hasattr(exercise, "solution") and exercise.solution:
                        solution = exercise.solution
                        if "sample_input" in sol:
                            solution.sample_input = sol["sample_input"]
                        if "expected_output" in sol:
                            solution.expected_output = sol["expected_output"]
                        if "initial_code" in sol:
                            solution.initial_code = sol["initial_code"]
                        solution.save()
                    else:
                        ExerciseSolution.objects.create(
                            exercise=exercise,
                            sample_input=sol.get("sample_input", ""),
                            expected_output=sol.get("expected_output", ""),
                            initial_code=sol.get("initial_code", "")
                        )
                updated.append(ex_id)
            except Exercise.DoesNotExist:
                continue
        return Response({"updated": updated}, status=status.HTTP_200_OK)
