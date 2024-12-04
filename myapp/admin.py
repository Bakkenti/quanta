from django.contrib import admin
from django import forms
from .models import Author, Student, Course, Module, Lesson
from django_ckeditor_5.widgets import CKEditor5Widget


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ('module', 'duration')

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ('name', 'module', 'short_description', 'video_url')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            formset.form.base_fields['module'].queryset = Module.objects.filter(course=obj)
            formset.form.base_fields['module'].required = True
        return formset

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [ModuleInline, LessonInline]
    list_display = ('title', 'author', 'formatted_duration', 'students_count', 'lessons_count')
    readonly_fields = ('students_count', 'lessons_count')

    def formatted_duration(self, obj):
        return f"{obj.duration}"

    def students_count(self, obj):
        return obj.students_count

    def lessons_count(self, obj):
        return obj.lessons_count

    formatted_duration.short_description = "Duration"
    students_count.short_description = 'Subscribed students'
    lessons_count.short_description = 'Number of lessons'

class LessonAdminForm(forms.ModelForm):
    video_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'Enter a video link (e.g., YouTube URL)'})
    )
    uploaded_video = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'placeholder': 'Or upload a video file'})
    )
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))

    class Meta:
        model = Lesson
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.uploaded_video:
            self.fields['uploaded_video'].help_text = f"Current video: {self.instance.uploaded_video.name}"

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    list_display = ('name', 'course', 'module', 'short_description')

    def get_readonly_fields(self, request, obj=None):
        return ['course'] if obj else []

    def course(self, obj):
        return obj.module.course if obj and obj.module else None

    course.short_description = 'Course'

    def has_add_permission(self, request):
        return False

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('username', 'about')


class StudentAdminForm(forms.ModelForm):
    subscribe_to_course = forms.ModelChoiceField(queryset=Course.objects.all(), required=False)

    class Meta:
        model = Student
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        subscribe_to_course = self.cleaned_data.get('subscribe_to_course')

        if subscribe_to_course:
            # Add the student to the selected course
            subscribe_to_course.subscribe_to_course(instance)
            subscribe_to_course.save()  # Save the course after updating

        if commit:
            instance.save()  # Save the student

        return instance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    readonly_fields = ['get_subscribed_courses']

    def get_subscribed_courses(self, obj):
        # Display a comma-separated list of course titles
        courses = obj.subscribed_courses.all()
        return ", ".join([course.title for course in courses]) if courses else "No subscriptions"

    get_subscribed_courses.short_description = "Subscribed Courses"