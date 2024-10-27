from django import forms
from django_select2.forms import ModelSelect2Widget
from .models import Lesson, Student, Course

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['name', 'content', 'video_url', 'short_description']

class StudentForm(forms.ModelForm):
    subscribed_courses = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=ModelSelect2Widget(
            model=Course,
            search_fields=['title__contains'],
            attrs={'data-placeholder': 'Search for a course...'}
        ),
        required=False,
        help_text='Search and select a course to subscribe the student to'
    )

    class Meta:
        model = Student
        fields = ['username', 'subscribed_courses']