from rest_framework import serializers
from .models import Exercise, ExerciseOption, ExerciseSolution, ExerciseAttempt

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

    class Meta:
        model = Exercise
        fields = [
            'id',
            'type',
            'title',
            'description',
            'options',
            'solution',
        ]

class ExerciseAttemptSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.user.username', read_only=True)
    exercise_title = serializers.CharField(source='exercise.title', read_only=True)

    class Meta:
        model = ExerciseAttempt
        fields = [
            'id',
            'student_username',
            'exercise_title',
            'selected_option',
            'submitted_code',
            'submitted_output',
            'is_correct',
            'checked_by_teacher',
            'created_at',
        ]
        read_only_fields = [
            'id', 'is_correct', 'checked_by_teacher', 'created_at', 'student_username', 'exercise_title'
        ]

    def validate(self, attrs):
        if attrs.get('selected_option') and (attrs.get('submitted_code') or attrs.get('submitted_output')):
            raise serializers.ValidationError("Choose only one: select option OR submit code/output.")
        return attrs

