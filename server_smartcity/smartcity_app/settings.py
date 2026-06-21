"""
Django settings for iet_24782031_2026 project.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-870@ab*a%8rsekdl6p!dm9(49o__+k2^^k!5urdd9s&lq0cc@%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*'] # Untuk pengembangan, izinkan semua host. Sesuaikan untuk produksi.


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',  # Penting untuk Feedback/Alert
    'django.contrib.staticfiles',
    'main_app',
    'about',
    'contacts',
    'usermanagement_24782031',
    'dashboard_24782031',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'django_scalar',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

AUTH_USER_MODEL = 'usermanagement_24782031.CustomUser'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', # Penting untuk Feedback/Alert
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smartcity_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # KETENTUAN LAB 5: Mendaftarkan folder templates global (sejajar manage.py)
        # Agar base.html yang berisi desain Konoha City terbaca oleh sistem
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smartcity_app.wsgi.application'


# Database
# Tetap menggunakan PostgreSQL sesuai konfigurasi project Anda
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'SmartCity_db',
        'USER': 'postgres',
        'PASSWORD': 'Admin12@',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
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


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SPECTACULAR_SETTINGS = {
    'TITLE': 'Smart City Portal API',
    'DESCRIPTION': 'Dokumentasi REST API resmi untuk Portal Pelaporan Laporan Warga',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

SCALAR_TITLE = 'Smart City Portal API'
