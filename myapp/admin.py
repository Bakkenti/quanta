from django.contrib import admin
from .models import Course, Module, Lesson, Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__email']

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ('title',)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ('name', 'duration', 'video_url')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [ModuleInline]
    list_display = ('title', 'total_lessons', 'total_duration')
    search_fields = ('title',)
    list_filter = ('level', 'author')
    autocomplete_fields = ['author']



@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('module', 'course', 'get_total_duration')
    search_fields = ('module', 'course__title')
    list_filter = ('course',)

    def get_total_duration(self, obj):
        return obj.total_duration()

    get_total_duration.short_description = "Total Duration"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'module', 'duration', 'video_url')
    search_fields = ('name', 'module__module')
    list_filter = ('module',)
