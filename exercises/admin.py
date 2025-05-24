from django.contrib import admin
from .models import Exercise, ExerciseOption, ExerciseSolution, ExerciseAttempt

class ExerciseOptionInline(admin.TabularInline):
    model = ExerciseOption
    extra = 2

class ExerciseSolutionInline(admin.StackedInline):
    model = ExerciseSolution
    extra = 0
    max_num = 1

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'lesson', 'type',)
    list_filter = ('type', 'lesson')
    search_fields = ('title', 'lesson__name')
    ordering = ('lesson', 'id')
    inlines = []

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.type == 'quiz':
                return [ExerciseOptionInline]
            elif obj.type == 'code':
                return [ExerciseSolutionInline]
        return [ExerciseOptionInline, ExerciseSolutionInline]

    def get_form(self, request, obj=None, **kwargs):
        self.inlines = self.get_inlines(request, obj)
        return super().get_form(request, obj, **kwargs)

@admin.register(ExerciseOption)
class ExerciseOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'exercise', 'text', 'is_correct')
    list_filter = ('exercise', 'is_correct')
    search_fields = ('text', 'exercise__title')

@admin.register(ExerciseSolution)
class ExerciseSolutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'exercise', 'expected_output')
    search_fields = ('exercise__title',)

@admin.register(ExerciseAttempt)
class ExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'exercise', 'is_correct', 'checked_by_teacher', 'created_at')
    list_filter = ('is_correct', 'checked_by_teacher', 'exercise')
    search_fields = ('student__user__username', 'exercise__title')
    readonly_fields = ('created_at',)
