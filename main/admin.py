from django.contrib import admin
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Author, Course, Module, Lesson, Student, Review, Advertisement, Category, ProgrammingLanguage
from exercises.models import Exercise, ExerciseOption, ExerciseSolution
import nested_admin
from django_ckeditor_5.fields import CKEditor5Field

User._meta.verbose_name, User._meta.verbose_name_plural = _("User"), _("Users")

admin.site.site_header = "Quanta Admin Panel"
admin.site.site_title = "Quanta Admin"
admin.site.index_title = "Manage Quanta Platform"

class MyAdminSite(admin.AdminSite):
    class Media:
        css = {
            'all': ('admin/custom.css',)
        }

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'role')
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Personal Info', {
            'classes': ('collapse',),
            'fields': ('about', 'birthday', 'phone_number', 'gender'),
        }),
    )
    search_fields = ('user__username', )
    ordering = ('user__username',)
    raw_id_fields = ('user',)

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'Username'

@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class AuthorAdminForm(forms.ModelForm):
    # Выбираем всех пользователей, которые имеют профиль студента и еще не являются авторами
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(student__isnull=False, author__isnull=True),
        label="Select Student to Promote",
        required=True
    )

    class Meta:
        model = Author
        fields = ['user']

    def clean_user(self):
        # Сюда попадёт именно User, а не Student!
        user = self.cleaned_data['user']
        # Прямая проверка: если у юзера уже есть связанный author, то нельзя повышать.
        if hasattr(user, 'author'):
            raise ValidationError("This user is already an author.")
        return user

    def save(self, commit=True):
        user = self.cleaned_data['user']
        # Создаём автора (Author.user = user)
        author = super().save(commit=False)
        author.user = user

        # Добавляем в группу "Author"
        author_group, created = Group.objects.get_or_create(name='Author')
        user.groups.add(author_group)
        user.save()

        # Промоутим роль у студента
        try:
            student = user.student
            student.role = "author"
            student.save()
        except Student.DoesNotExist:
            pass

        if commit:
            author.save()
        return author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_user_role']
    search_fields = ['user__username']
    form = AuthorAdminForm

    def get_user_role(self, obj):
        if hasattr(obj.user, "student"):
            return obj.user.student.role
        elif hasattr(obj.user, "author"):
            return "Author"
        return "No Role"

    get_user_role.short_description = "Role"

    def delete_model(self, request, obj):
        user = obj.user
        try:
            student = user.student
            student.role = "student"
            student.save()
        except Student.DoesNotExist:
            pass
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            user = obj.user
            try:
                student = user.student
                student.role = "student"
                student.save()
            except Student.DoesNotExist:
                pass
        super().delete_queryset(request, queryset)


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['module', 'name', 'short_description', 'video_url', 'uploaded_video']


    def clean(self):
        cleaned_data = super().clean()
        video_url = cleaned_data.get("video_url")
        uploaded_video = cleaned_data.get("uploaded_video")

        if video_url and uploaded_video:
            raise forms.ValidationError("You can provide either a video URL or upload a file, but not both.")
        return cleaned_data


LessonFormSet = inlineformset_factory(Module, Lesson, form=LessonForm, extra=1, can_delete=True)

class ExerciseOptionInline(nested_admin.NestedTabularInline):
    model = ExerciseOption
    extra = 1

class ExerciseSolutionInline(nested_admin.NestedStackedInline):
    model = ExerciseSolution
    extra = 0
    max_num = 1

class ExerciseInline(nested_admin.NestedStackedInline):
    model = Exercise
    extra = 0
    inlines = [ExerciseOptionInline, ExerciseSolutionInline]

class CourseAdminForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=True
    )

    class Meta:
        model = Course
        fields = '__all__'


class LessonInline(nested_admin.NestedTabularInline):
    model = Lesson
    extra = 0
    fields = ['name', 'short_description', 'video_url', 'uploaded_video']
    show_change_link = True
    classes = ['collapse']

class ModuleInline(nested_admin.NestedTabularInline):
    model = Module
    inlines = [LessonInline]  
    extra = 1
    fields = ['module', 'duration']
    show_change_link = True
    classes = ['collapse', 'module-collapse']


@admin.register(Course)
class CourseAdmin(nested_admin.NestedModelAdmin):
    form = CourseAdminForm
    inlines = [ModuleInline]  # Add ModuleInline here
    list_display = ['title', 'author', 'category', 'level', 'duration', 'course_image', 'language']
    search_fields = ['title', 'author__user__username']
    list_filter = ['category', 'level']
    autocomplete_fields = ['author']
    fieldsets = (
        (None, {'fields': ('title', 'author', 'language', 'category', 'level', 'duration', 'course_image', 'description')}),
    )


@admin.register(Lesson)
class LessonAdmin(nested_admin.NestedModelAdmin):
    form = LessonForm
    list_display = ['name', 'module', 'get_video_display']
    search_fields = ['name', 'module__module']
    list_filter = ['module']
    fieldsets = (
        (None, {'fields': ('module', 'name', 'short_description', 'video_url', 'uploaded_video', 'content')}),
    )
    inlines = [ExerciseInline]

    def get_video_display(self, obj):
        video_html = ""

        if obj.video_url:
            video_html += f"<strong>Video URL:</strong> {obj.video_url}<br>"

        if obj.uploaded_video:
            video_html += f"<strong>Uploaded Video:</strong> Currently: {obj.uploaded_video}"

        return format_html(video_html) if video_html else "-"

    get_video_display.short_description = "Video"

    def has_add_permission(self, request):
        return False

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'created_at']
    search_fields = ['user__username', 'course__title']
    list_filter = ['rating', 'created_at']
    autocomplete_fields = ['user', 'course']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = queryset.order_by('user__username')[:5]
        return queryset, use_distinct


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'preview_image', 'url')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('name', 'content', 'image', 'url')}),
        ('Metadata', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    readonly_fields = ('created_at',)

    def preview_image(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="100" height="auto" />')
        return "-"

    preview_image.short_description = "Preview"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'courses_count')
    search_fields = ('name',)

    def courses_count(self, obj):
        return obj.courses.count()
    courses_count.short_description = 'Courses Count'
