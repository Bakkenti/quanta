from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from dj_rest_auth.views import LoginView, LogoutView

from .views import (
    Registration, Login, GoogleLogin, GoogleCodeExchangeView, GithubLogin, GithubCodeExchangeView, Profile,
    CourseList, CourseDetail, LessonDetail, MostPopularCourseView, BestCourseView, Advertisement,
    AuthorCourseListCreate, AuthorCourseEdit, AuthorModuleListCreate, AuthorModuleEdit, AuthorLessonListCreate, AuthorLessonEdit,
    AuthorBlogListCreate, AuthorBlogEdit,
    MyCourses, EnrollCourse, UnenrollCourse, ProfileEdit, LessonImageUploadView,
    SiteStats, SiteReviewView, CategoryList, KeepInTouchView,
    ApplyAuthor, ApplyJournalist, AppliesStatus, WithdrawApplication, ConfirmEmail, SurveyRecommendationView,
    ConspectChatListView, ConspectHistoryView, ConspectSendMessageView, ConspectStartChatView,
    CodeExecutionView, MyCertificatesView, CertificateVerifyView, TriggerCertificateView
)

urlpatterns = [
    path('login/', Login.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('signup/', Registration.as_view(), name='rest_signup'),
    path('account/confirm-email/', ConfirmEmail.as_view(), name='account_confirm_email'),
    path('profile/', Profile.as_view(), name='profile'),
    path('profile/edit/', ProfileEdit.as_view(), name='profile-edit'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/', LessonDetail.as_view(), name='lesson_detail'),
    path('courses/', CourseList.as_view(), name='course_list'),
    path('courses/<int:id>/', CourseDetail.as_view(), name='course_detail'),
    path('courses/<int:course_id>/enroll/', EnrollCourse.as_view(), name='enroll-course'),
    path('courses/<int:course_id>/unenroll/', UnenrollCourse.as_view(), name='unenroll-course'),
    path('mycourses/', MyCourses.as_view(), name='my-courses'),
    path('author/courses/', AuthorCourseListCreate.as_view(), name='author_course_list_create'),
    path('author/courses/<int:course_id>/', AuthorCourseEdit.as_view(), name='author_course_edit'),
    path('author/courses/<int:course_id>/modules/', AuthorModuleListCreate.as_view(), name='author_module_list_create'),
    path('author/courses/<int:course_id>/modules/<int:module_id>/', AuthorModuleEdit.as_view(), name='author_module_edit'),
    path('author/courses/<int:course_id>/modules/<int:module_id>/lessons/', AuthorLessonListCreate.as_view(), name='author_lesson_list_create'),
    path('author/courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/', AuthorLessonEdit.as_view(), name='author_lesson_edit'),
    path('mostpopularcourse/', MostPopularCourseView.as_view(), name='most_popular_course'),
    path('bestcourse/', BestCourseView.as_view(), name='best_course'),
    path('advertisement/', Advertisement.as_view(), name='advertisement'),
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('site-stats/', SiteStats.as_view(), name='site-stats'),
    path('image_upload/', LessonImageUploadView.as_view(), name='ckeditor5_image_upload'),
    path('site-reviews/', SiteReviewView.as_view(), name='site-reviews'),
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('auth/google/callback/', GoogleCodeExchangeView.as_view(), name='google_code_exchange'),
    path('auth/github/', GithubLogin.as_view(), name='github_login'),
    path('auth/github/callback/', GithubCodeExchangeView.as_view(), name='github_code_exchange'),
    path('accounts/', include('allauth.urls')),
    path('author/blogs/', AuthorBlogListCreate.as_view(), name='author_blog_list_create'),
    path('author/blogs/<int:blog_id>/', AuthorBlogEdit.as_view(), name='author_blog_edit'),
    path('keep-in-touch/', KeepInTouchView.as_view(), name='keep-in-touch'),
    path('author/apply-author/', ApplyAuthor.as_view(), name='apply_author'),
    path('author/apply-journalist/', ApplyJournalist.as_view(), name='apply_journalist'),
    path('author/applies-status/', AppliesStatus.as_view(), name='applies_status'),
    path('author/withdraw/<str:role>/', WithdrawApplication.as_view(), name='withdraw_application'),
    path('survey/', SurveyRecommendationView.as_view(), name='survey-recommendation'),
    path("conspect/", ConspectChatListView.as_view(), name="conspect-list"),
    path("conspect/start/", ConspectStartChatView.as_view(), name="conspect-start"),
    path("conspect/<int:chat_id>/", ConspectHistoryView.as_view(), name="conspect-history"),
    path("conspect/<int:chat_id>/send-message/", ConspectSendMessageView.as_view(), name="conspect-message"),
    path("compiler/", CodeExecutionView.as_view(), name="code-execute"),
    path("certificates/", MyCertificatesView.as_view(), name="my-certificates"),
    path("certificate/verify/<uuid:token>/", CertificateVerifyView.as_view(), name="certificate-verify"),
    path("certificates/generate/<int:course_id>/", TriggerCertificateView.as_view(), name="generate-certificate"),
]
