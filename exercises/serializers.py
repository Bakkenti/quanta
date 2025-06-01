from rest_framework import serializers
from .models import Exercise, ExerciseOption, ExerciseSolution, LessonAttempt

class ExerciseOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseOption
        fields = ['id', 'text', 'is_correct']

class ExerciseSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseSolution
        fields = ['id', 'sample_input', 'expected_output', 'initial_code']

class ExerciseSerializer(serializers.ModelSerializer):
    options = ExerciseOptionSerializer(many=True, read_only=True)
    solution = ExerciseSolutionSerializer(read_only=True)
    language = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            'id',
            'type',
            'title',
            'description',
            'language',
            'options',
            'solution',
        ]

    def get_language(self, obj):
        return obj.language.name if obj.language else None

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)
        language_name = self.initial_data.get('language')
        if language_name:
            try:
                lang = ProgrammingLanguage.objects.get(name__iexact=language_name)
                validated_data['language'] = lang
            except ProgrammingLanguage.DoesNotExist:
                raise serializers.ValidationError({'language': f"Language '{language_name}' does not exist."})
        else:
            validated_data['language'] = None
        return validated_data

class LessonAttemptSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.user.username', read_only=True)
    lesson_id = serializers.IntegerField(source='lesson.lesson_id', read_only=True)
    class Meta:
        model = LessonAttempt
        fields = [
            'id',
            'student_username',
            'lesson_id',
            'answers',
            'score',
            'created_at',
            'finished_at'
        ]
        read_only_fields = [
            'id', 'score', 'created_at', 'finished_at', 'student_username', 'lesson_id'
        ]
