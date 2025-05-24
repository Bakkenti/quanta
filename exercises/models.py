from django.db import models
from main.models import Lesson, Student, ProgrammingLanguage



class Exercise(models.Model):
    EXERCISE_TYPE_CHOICES = [
        ('quiz', 'Question & Answer'),
        ('code', 'Code Exercise'),
    ]

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="exercises"
    )
    type = models.CharField(
        max_length=10, choices=EXERCISE_TYPE_CHOICES
    )
    title = models.CharField(max_length=255, verbose_name="Title or Question")
    description = models.TextField(blank=True, null=True, verbose_name="Description (optional)")
    language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exercises"
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
    sample_input = models.TextField(blank=True, null=True, verbose_name="Sample Input (optional)")
    expected_output = models.TextField(verbose_name="Expected Output (Required)")
    initial_code = models.TextField(blank=True, null=True, verbose_name="Starter Code (optional)")

    def __str__(self):
        return f"Solution for {self.exercise.title}"

class ExerciseAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(ExerciseOption, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_code = models.TextField(blank=True, null=True)
    submitted_output = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    checked_by_teacher = models.BooleanField(default=False)

    def __str__(self):
        return f"Attempt by {self.student} for {self.exercise}"
