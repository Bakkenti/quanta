from django.contrib import admin
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Author, Course, Module, Lesson, AuthorCourse, Student
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

User._meta.verbose_name = _("Super User")
User._meta.verbose_name_plural = _("Super Users")
admin.site.unregister(Group)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('about', 'birthday', 'phone_number', 'gender')}),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(Student, StudentAdmin)


class AuthorAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        label="Select Student to Promote",
        required=True
    )

    class Meta:
        model = Author
        fields = ['user', 'published_courses']

    def save(self, commit=True):
        student = self.cleaned_data['user']
        student.role = "author"
        student.save()
        return super().save(commit=commit)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    form = AuthorAdminForm
    list_display = ['user', 'get_user_role']
    search_fields = ['user__username', 'user__email']

    def get_user_role(self, obj):
        return obj.user.role

    get_user_role.short_description = 'Role'


class CourseAdminForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Course
        fields = '__all__'


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ['module', 'duration']
    show_change_link = True


class LessonAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))  # CKEditor for content

    class Meta:
        model = Lesson
        fields = '__all__'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    inlines = [ModuleInline]
    list_display = ['title', 'level', 'rating']
    search_fields = ['title']
    list_filter = ['level']
    autocomplete_fields = ['author']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ['name', 'video_url', 'uploaded_video']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    list_display = ['name', 'module', 'video_url', 'uploaded_video']
    search_fields = ['name', 'module__module']
    list_filter = ['module']
