from django.contrib import admin
from .models import Exercise, ExerciseOption, ExerciseSolution, LessonAttempt
from django.utils.safestring import mark_safe

class ExerciseOptionInline(admin.TabularInline):
    model = ExerciseOption
    extra = 2

class ExerciseSolutionInline(admin.StackedInline):
    model = ExerciseSolution
    extra = 0
    max_num = 1

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'lesson', 'type', 'language')
    list_filter = ('type', 'lesson')
    search_fields = ('title', 'lesson__name')
    ordering = ('lesson', 'id')
    inlines = []

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.type == 'mcq':
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

@admin.action(description="Сбросить лимит подсказок")
def reset_hints(modeladmin, request, queryset):
     updated = queryset.update(hints_left=3)
     admin_message = f"Сброшено подсказок для {updated} попыток."
     modeladmin.message_user(request, admin_message, messages.SUCCESS)

@admin.register(LessonAttempt)
class LessonAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'lesson', 'score', 'created_at', 'get_answers_preview', 'hints_left')
    list_filter = ('lesson', 'student')
    search_fields = ('student__user__username', 'lesson__name')
    readonly_fields = ('student', 'lesson', 'created_at', 'score', 'formatted_answers')
    actions = [reset_hints]
    exclude = ('finished_at',)



    def get_answers_preview(self, obj):
        return str(obj.answers)[:150]
    get_answers_preview.short_description = 'Answers (preview)'

    def formatted_answers(self, obj):
        html = ""
        from .models import Exercise, ExerciseOption
        answers = obj.answers
        if not answers:
            return "-"
        html += "<ul>"
        for ans in answers:
            ex_id = ans.get('exercise_id')
            opt_id = ans.get('selected_option')
            try:
                exercise = Exercise.objects.get(id=ex_id)
                option = ExerciseOption.objects.get(id=opt_id, exercise=exercise)
                is_correct = "✅" if option.is_correct else "❌"
                html += f"<li><b>Question:</b> {exercise.title}<br>"
                html += f"<b>Answer:</b> {option.text} {is_correct}</li><br>"
            except Exception:
                html += f"<li>Invalid data: {ans}</li>"
        html += "</ul>"
        return mark_safe(html)
    formatted_answers.short_description = "Answers"


