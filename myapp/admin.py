from django.contrib import admin
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Author, Course, Module, Lesson, Student, Review
import nested_admin
from django_ckeditor_5.fields import CKEditor5Field

User._meta.verbose_name = _("Super User")
User._meta.verbose_name_plural = _("Super Users")
admin.site.unregister(Group)

admin.site.site_header = "Quanta Admin Panel"
admin.site.site_title = "Quanta Admin"
admin.site.index_title = "Manage Courses & Lessons"

class MyAdminSite(admin.AdminSite):
    class Media:
        css = {
            'all': ('admin/custom.css',)
        }


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'role')
    fieldsets = (
        (None, {'fields': ('username','password')}),  # You may not need 'username' here if it's part of User
        ('Personal Info', {
            'classes': ('collapse',),
            'fields': ('about', 'birthday', 'phone_number', 'gender'),
        }),
    )
    search_fields = ('user__username', )  # Correct search reference
    ordering = ('user__username',)  # Correct ordering reference

    def get_username(self, obj):
        return obj.user.username  # Access username from the related User model

    get_username.short_description = 'Username'


class AuthorAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        label="Select Student to Promote",
        required=True
    )

    class Meta:
        model = Author
        fields = ['user']

    def save(self, commit=True):
        student = self.cleaned_data['user']
        student.role = "author"
        student.save()
        return super().save(commit=commit)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    form = AuthorAdminForm
    list_display = ['user', 'get_user_role']
    search_fields = ['user__username']

    def get_user_role(self, obj):
        return obj.user.role

    get_user_role.short_description = 'Role'

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
    extra = 1
    fields = ['name', 'short_description', 'video_url', 'uploaded_video']
    show_change_link = True
    classes = ['collapse']


class ModuleInline(nested_admin.NestedTabularInline):
    model = Module
    inlines = [LessonInline]
    extra = 1
    fields = ['module', 'duration']
    show_change_link = True
    classes = ['collapse']

@admin.register(Course)
class CourseAdmin(nested_admin.NestedModelAdmin):
    form = CourseAdminForm
    inlines = [ModuleInline]
    list_display = ['title', 'level', 'author', 'duration', 'course_image']
    search_fields = ['title', 'author__user__username']
    list_filter = ['level']
    autocomplete_fields = ['author']
    fieldsets = (
        (None, {'fields': ('title', 'level', 'author', 'duration', 'course_image', 'description')}),
    )

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonForm
    list_display = ['name', 'module', 'get_video_display']
    search_fields = ['name', 'module__module']
    list_filter = ['module']
    fieldsets = (
        (None, {'fields': ('module', 'name', 'short_description', 'video_url', 'uploaded_video', 'content')}),
    )

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
