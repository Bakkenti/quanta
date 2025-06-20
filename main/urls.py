from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from dj_rest_auth.views import LoginView, LogoutView

from .views import (
    Registration, Login, GoogleLogin, GoogleCodeExchangeView, GithubLogin, GithubCodeExchangeView, Profile,
    CourseList, CourseDetail, LessonDetail, MostPopularCourseView, BestCourseView, AdvertisementView,
    AuthorCourseListCreate, AuthorCourseEdit, AuthorModuleListCreate, AuthorModuleEdit, AuthorLessonListCreate, AuthorLessonEdit,
    AuthorBlogListCreate, AuthorBlogEdit,
    MyCourses, EnrollCourse, UnenrollCourse, ProfileEdit, LessonImageUploadView,
    SiteStats, SiteReviewView, CategoryList, KeepInTouchView,
    ApplyAuthor, ApplyJournalist, AppliesStatus, WithdrawApplication, ConfirmEmail, SurveyRecommendationView,
    ConspectChatListView, ConspectHistoryView, ConspectSendMessageView, ConspectStartChatView,
    CodeExecutionView, CompilerFeaturesView, MyCertificatesView, CertificateVerifyView, TriggerCertificateView,
    ProjectToRSendMessageView, ProjectToRChatListView, ProjectToRHistoryView, ConspectPDFView, ProjectToRPDFView, ProgrammingLanguagesListView,
    ChatWithAIView, ChatHistoryView, AllAppliesView, ApproveApplyView, RejectApplyView, ChangeRoleView, DeactivateUserView, RestoreUserView, AdvertisementListCreateView,
    AdvertisementEditView, UsersListView, FinalExamDetailView,
    FinalExamStartView,
    FinalExamSubmitView,
    FinalExamAttemptsListView, FinalExamCreateView, LessonProgressView, CourseProgressView, FinalExamDeleteView
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
    path('advertisement/', AdvertisementView.as_view(), name='advertisement'),
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
    path("compiler-features/", CompilerFeaturesView.as_view(), name="compiler-features"),
    path("certificates/", MyCertificatesView.as_view(), name="my-certificates"),
    path("certificate/verify/<uuid:token>/", CertificateVerifyView.as_view(), name="certificate-verify"),
    path("certificates/generate/<int:course_id>/", TriggerCertificateView.as_view(), name="generate-certificate"),
    path('project_tor/', ProjectToRChatListView.as_view(), name='project_tor-list'),
    path('project_tor/<int:chat_id>/', ProjectToRHistoryView.as_view(), name='project_tor-history'),
    path('project_tor/<int:chat_id>/send-message/', ProjectToRSendMessageView.as_view(), name='project_tor-message'),
    path('conspect/<int:chat_id>/pdf/', ConspectPDFView.as_view()),
    path('project_tor/<int:chat_id>/pdf/', ProjectToRPDFView.as_view(), name='project_tor-pdf'),
    path('languages/', ProgrammingLanguagesListView.as_view()),
    path('ai-dialog/', ChatWithAIView.as_view()),
    path('ai-history/', ChatHistoryView.as_view()),
    path('applies/', AllAppliesView.as_view(), name='all_applies'),
    path('applies/<int:user_id>/<str:role>/approve/', ApproveApplyView.as_view(), name='approve_apply'),
    path('applies/<int:user_id>/<str:role>/reject/', RejectApplyView.as_view(), name='reject_apply'),
    path('change-role/<int:user_id>/', ChangeRoleView.as_view(), name='change_role'),
    path('users/<int:user_id>/deactivate/', DeactivateUserView.as_view(), name='deactivate_user'),
    path('users/<int:user_id>/restore/', RestoreUserView.as_view(), name='restore_user'),
    path('advertisements/', AdvertisementListCreateView.as_view(), name='advertisement_list_create'),
    path('advertisements/<int:pk>/', AdvertisementEditView.as_view(), name='advertisement_edit'),
    path('users-list/', UsersListView.as_view(), name='users_list'),
    path('courses/<int:course_id>/final-exam/', FinalExamDetailView.as_view(), name='final_exam_detail'),  # GET
    path('courses/<int:course_id>/final-exam/create/', FinalExamCreateView.as_view(), name='final_exam_create'),  # POST

    # Начать попытку
    path('courses/<int:course_id>/final-exam/start/', FinalExamStartView.as_view(), name='final_exam_start'),  # POST

    # Получить попытки студента
    path('courses/<int:course_id>/final-exam/attempts/', FinalExamAttemptsListView.as_view(),
         name='final_exam_attempts'),  # GET

    path('courses/<int:course_id>/final-exam/submit-answer/', FinalExamSubmitView.as_view(), name='final_exam_submit'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/progress/',
         LessonProgressView.as_view(), name='lesson_progress'),
    path('courses/<int:course_id>/final-exam/delete/', FinalExamDeleteView.as_view(), name='final_exam_delete'),
    # DELETE

    # Прогресс курса
    path('courses/<int:course_id>/progress/', CourseProgressView.as_view(), name='course_progress'),

]
