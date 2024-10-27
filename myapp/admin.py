from django.contrib import admin
from .models import Author, Student, Course, Module, Lesson

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ('module', 'duration')

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
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
        return obj.student_set.count()

    def lesson_count(self, obj):
        return Lesson.objects.filter(module__course=obj).count()

    formatted_duration.short_description = "Duration"
    students_count.short_description = 'Subscribed students'
    lesson_count.short_description = 'Number of lessons'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'module', 'short_description')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['module'].required = True

        if obj and obj.module:
            form.base_fields['module'].queryset = Module.objects.filter(course=obj.module.course)
        else:
            form.base_fields['module'].queryset = Module.objects.none()
        return form

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

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['username']

    def save_model(self, request, obj, form, change):
        # Добавляем выбранный курс в список подписанных курсов
        subscribed_course = form.cleaned_data.get('subscribed_courses')
        if subscribed_course:
            obj.subscribed_courses[str(subscribed_course.id)] = {
                "subscribed_on": timezone.now().strftime('%Y-%m-%d'),
                "progress": "0%"
            }
        super().save_model(request, obj, form, change)