from django import forms
from .models import Lesson, Student, Course

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['name', 'content', 'video_url', 'short_description']
