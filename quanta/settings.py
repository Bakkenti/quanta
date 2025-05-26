from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'quant.up.railway.app', 'jasulan273.github.io/Quanta/']

INTERNAL_IPS = ('127.0.0.1', 'localhost:8000')

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = ['https://quant.up.railway.app', 'http://localhost:8000', 'http://127.0.0.1:8000', 'https://jasulan273.github.io/Quanta/']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'blog',
    'exercises',
    'rest_framework',
    'rest_framework_simplejwt',
    'whitenoise.runserver_nostatic',
    'django_ckeditor_5',
    'corsheaders',
    'nested_admin',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'dj_rest_auth',
]

REST_USE_JWT = True

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'main.serializers.UserSerializer',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=180),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_RETURN_EXPIRATION': True,
    'TOKEN_MODEL': None,
}


LOGIN_URL = '/login/'

SITE_ID = 1

ACCOUNT_LOGIN_METHODS = ['username', 'email']
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER



ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_ADAPTER = "main.adapters.MyAccountAdapter"


ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/login/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/profile/'
ACCOUNT_EMAIL_CONFIRMATION_URL = "https://jasulan273.github.io/Quanta/verify-email/?key={key}"
LOGIN_REDIRECT_URL = "/profile/"

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    "https://jasulan273.github.io",
    "https://quant.up.railway.app",
]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE"
]
CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = 'quanta.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },

    },
]

WSGI_APPLICATION = 'quanta.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

MEDIA_FOLDERS = ["avatars", "course_images", "lesson_videos", "blog_images", "images"]

for folder in MEDIA_FOLDERS:
    path = os.path.join(MEDIA_ROOT, folder)
    os.makedirs(path, exist_ok=True)

CKEDITOR_STORAGE_BACKEND = 'main.custom_storage.UniqueFilenameStorage'
CKEDITOR_5_UPLOADS = 'course_images/'
CKEDITOR_5_CONFIGS = {
    'default': {
        'language': 'en',
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'underline', 'link', 'bulletedList',
            'numberedList', 'blockQuote', '|', 'insertTable', 'tableColumn',
            'tableRow', 'mergeTableCells', '|', 'fontFamily', 'fontSize',
            'fontColor', 'fontBackgroundColor', '|', 'imageUpload', 'removeFormat',
            'undo', 'redo'
        ],
        'fontFamily': {
            'options': [
                'default',
                'Arial, sans-serif',
                'Courier New, Courier, monospace',
                'Georgia, serif',
                'Lucida Sans Unicode, Lucida Grande, sans-serif',
                'Tahoma, Geneva, sans-serif',
                'Times New Roman, Times, serif',
                'Verdana, Geneva, sans-serif'
            ],
        },
        'fontSize': {
            'options': [
                'default',
                'tiny',
                'small',
                'big',
                'huge'
            ],
        },
        'fontColor': {
            'columns': 5,
            'documentColors': 10,
            'colors': [
                {
                    'color': 'black',
                    'label': 'Black'
                },
                {
                    'color': 'red',
                    'label': 'Red'
                },
                {
                    'color': 'green',
                    'label': 'Green'
                },
                {
                    'color': 'blue',
                    'label': 'Blue'
                },
                {
                    'color': 'lightgray',
                    'label': 'Light Gray'
                },
            ]
        },
        'fontBackgroundColor': {
            'columns': 5,
            'documentColors': 10,
            'colors': [
                {
                    'color': 'lightgray',
                    'label': 'Light Gray'
                },
                {
                    'color': 'white',
                    'label': 'White'
                },
                {
                    'color': 'yellow',
                    'label': 'Yellow'
                },
                {
                    'color': 'lightblue',
                    'label': 'Light Blue'
                },
                {
                    'color': 'pink',
                    'label': 'Pink'
                },
            ]
        },
        'styles': {
            'default': {
                'color': 'black',
                'background-color': 'lightgray'
            }
        },
        'height': 300,
        'width': '100%',
        'skin': 'moon-dark',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
