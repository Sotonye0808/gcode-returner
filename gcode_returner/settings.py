"""
Django settings for the GCode Returner API.

This module contains all the settings and configurations for the Django backend API
that serves as the core service for SVG to G-code conversion and signature evaluation.

Features:
- SVG to G-code conversion endpoint
- Evaluation endpoints for signature analysis (SSIM, line smoothness, G-code execution error)
- RESTful API design using Django REST Framework
- CORS support for frontend integration

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
import socket 

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Get container hostname dynamically
def get_container_hostname():
    try:
        return socket.gethostname()
    except:
        return None

# ALLOWED_HOSTS configuration with dynamic container hostname
base_allowed_hosts = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
ALLOWED_HOSTS = [host.strip() for host in base_allowed_hosts if host.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'gcode_api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gcode_returner.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'gcode_returner.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Database configuration
if 'DATABASE_URL' in os.environ and dj_database_url:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL')) # type: ignore
    }
else:
    # Use SQLite with a path that works in both local and Docker environments
    if os.path.exists('/app'):
        # Running in Docker
        db_path = '/app/db/db.sqlite3'
    else:
        # Running locally
        db_path = BASE_DIR / 'db.sqlite3'
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_path,
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
    }
}

# CORS settings for frontend integration
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS', 
    'http://localhost:3000,http://127.0.0.1:3000,http://localhost:4200,http://127.0.0.1:4200'
).split(',')

CORS_ALLOW_CREDENTIALS = True

# Allow specific headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Allow specific methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# CORS preflight cache time
CORS_PREFLIGHT_MAX_AGE = 86400

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',},
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'gcode_api': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Signed request settings for trusted frontend origins
FRONTEND_SIGNING_KEY = os.getenv('FRONTEND_SIGNING_KEY', 'dev-signing-key-change-in-production')

TRUSTED_FRONTEND_ORIGINS = os.getenv(
    'TRUSTED_FRONTEND_ORIGINS',
    'https://signature-eu.web.app,http://localhost:4200,http://127.0.0.1:4200'
).split(',')

# Add container hostname dynamically for Docker environments
if os.path.exists('/app'):  # Running in Docker
    container_hostname = get_container_hostname()
    if container_hostname:
        ALLOWED_HOSTS.append(container_hostname)
    # Add wildcard for internal Docker networking
    ALLOWED_HOSTS.extend(['0.0.0.0', '*'])

# Back4App Production Configuration
BACK4APP_APP_ID = os.environ.get('BACK4APP_APP_ID')
if BACK4APP_APP_ID or os.environ.get('BACK4APP_DEPLOYMENT'):
    # Production settings for Back4App
    DEBUG = False
    # Filter out localhost for production
    #ALLOWED_HOSTS = [host.strip() for host in allowed_hosts if host.strip() and 'localhost' not in host and '127.0.0.1' not in host]
    
    # Add Back4App domains
    ALLOWED_HOSTS.extend([
        '.back4app.io',
        '.containers.back4app.com',
        '.parseapi.back4app.com'
    ])

    # Don't use wildcard in production, but allow container hostnames
    if '*' in ALLOWED_HOSTS:
        ALLOWED_HOSTS.remove('*')

    ALLOWED_HOSTS.append(get_container_hostname() or 'back4app-container')
    
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # CORS settings for production
    CORS_ALLOWED_ORIGINS = [
        'https://signature-eu.web.app',
    ]
    
    # Trusted frontend origins for production
    TRUSTED_FRONTEND_ORIGINS = [
        'https://signature-eu.web.app',
    ]
    
    # Static files configuration for production
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    
    # Logging for production
    LOGGING['loggers']['gcode_api']['level'] = 'WARNING'
    LOGGING['root']['level'] = 'WARNING'