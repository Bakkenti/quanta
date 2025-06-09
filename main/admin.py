from django.contrib import admin, messages
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Author, Course, Module, Lesson, Student, Review, Advertisement, Category, ProgrammingLanguage, Certificate, ProjectToRChat, ProjectToRMessage
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


class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    fields = ('about', 'avatar', 'birthday', 'phone_number', 'gender')
    max_num = 1


class AuthorAdminForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        author_status = cleaned_data.get("author_status")
        author_reject_reason = cleaned_data.get("author_reject_reason")
        journalist_status = cleaned_data.get("journalist_status")
        journalist_reject_reason = cleaned_data.get("journalist_reject_reason")

        return cleaned_data

    def clean_user(self):
        user = self.cleaned_data.get('user')
        if not user:
            return user
        if hasattr(user, 'author'):
            raise forms.ValidationError("This user is already an author.")
        return user

    def save(self, commit=True):
        user = self.cleaned_data.get('user')
        author = super().save(commit=False)
        if user:
            author.user = user
            author_group, _ = Group.objects.get_or_create(name='Author')
            user.groups.add(author_group)
            user.save()
            try:
                student = user.student
                student.role = "author"
                student.save()
            except Exception:
                pass
        if commit:
            author.save()
        return author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    form = AuthorAdminForm
    list_display = [
        'user', 'get_user_role', 'author_status', 'journalist_status',
        'author_reject_reason_short', 'journalist_reject_reason_short'
    ]
    search_fields = ['user__username']

    # fieldsets: 'user' только для создания, не для изменения
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': (
                    # 'user' только если создаём нового автора
                    (('user',) if obj is None else ()) +
                    ('is_author', 'is_journalist'),
                    ('author_status', 'author_reject_reason'),
                    ('journalist_status', 'journalist_reject_reason'),
                )
            }),
        ]
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and "user" in form.base_fields:
            form.base_fields["user"].disabled = True  # или .widget = forms.HiddenInput() если совсем скрыть
        return form

    def get_user_role(self, obj):
        if hasattr(obj.user, "student"):
            return obj.user.student.role
        elif hasattr(obj.user, "author"):
            return "Author"
        return "No Role"
    get_user_role.short_description = "User Role"

    def author_reject_reason_short(self, obj):
        return (obj.author_reject_reason[:30] + '...') if obj.author_reject_reason and len(obj.author_reject_reason) > 30 else (obj.author_reject_reason or "")
    author_reject_reason_short.short_description = "Author Reject Reason"

    def journalist_reject_reason_short(self, obj):
        return (obj.journalist_reject_reason[:30] + '...') if obj.journalist_reject_reason and len(obj.journalist_reject_reason) > 30 else (obj.journalist_reject_reason or "")
    journalist_reject_reason_short.short_description = "Journalist Reject Reason"

    def save_model(self, request, obj, form, change):
        if obj.author_status == "approved":
            obj.author_reject_reason = ""
            obj.is_author = True
        if obj.author_status in ["none", "pending"]:
            obj.is_author = False

        if obj.journalist_status == "approved":
            obj.journalist_reject_reason = ""
            obj.is_journalist = True
        if obj.journalist_status in ["none", "pending"]:
            obj.is_journalist = False

        try:
            student = obj.user.student
            if obj.is_author and obj.is_journalist:
                student.role = "author_journalist"
            elif obj.is_author:
                student.role = "author"
            elif obj.is_journalist:
                student.role = "journalist"
            else:
                student.role = "student"
            student.save()
        except Exception:
            pass

        super().save_model(request, obj, form, change)




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

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'issued_at', 'token_short', 'has_pdf_and_hash')
    search_fields = ('user__username', 'course__title', 'token')
    list_filter = ('issued_at',)
    readonly_fields = ('user', 'course', 'pdf_file', 'token', 'hash_code', 'issued_at')

    def token_short(self, obj):
        return str(obj.token)[:8] + "..."
    token_short.short_description = "Token (short)"

    def has_pdf_and_hash(self, obj):
        return bool(obj.pdf_file and obj.hash_code)
    has_pdf_and_hash.boolean = True
    has_pdf_and_hash.short_description = "Valid?"

@admin.register(ProjectToRChat)
class ProjectToRChatAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'created_at']

@admin.register(ProjectToRMessage)
class ProjectToRMessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'role', 'timestamp']