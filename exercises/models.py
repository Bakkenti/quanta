from django.db import models
from django.contrib.auth.models import User
from main.models import Lesson, Student, ProgrammingLanguage

class Exercise(models.Model):
    EXERCISE_TYPE_CHOICES = [
        ('mcq', 'Question & Answer'),
        ('code', 'Code Exercise'),
    ]
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="exercises"
    )
    type = models.CharField(max_length=10, choices=EXERCISE_TYPE_CHOICES)
    title = models.CharField(max_length=255, verbose_name="Title or Question")
    description = models.TextField(blank=True, null=True)
    language = models.ForeignKey(
        ProgrammingLanguage, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="exercises"
    )
    def save(self, *args, **kwargs):
        if not self.language and self.lesson and self.lesson.module and self.lesson.module.course:
            self.language = self.lesson.module.course.language
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"

class ExerciseOption(models.Model):
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"

class ExerciseSolution(models.Model):
    exercise = models.OneToOneField(
        Exercise, on_delete=models.CASCADE, related_name="solution"
    )
    sample_input = models.TextField(blank=True, null=True)
    expected_output = models.TextField()
    initial_code = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Solution for {self.exercise.title}"

class LessonAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    answers = models.JSONField()
    score = models.IntegerField(default=0)
    def __str__(self):
        return f"LessonAttempt by {self.student} on {self.lesson}"

class HintRequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} @ {self.requested_at}"