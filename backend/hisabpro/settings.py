import os
from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Production settings
if not DEBUG:
    ALLOWED_HOSTS.extend([
        '.railway.app',
        '.vercel.app',
        'hisabpro.up.railway.app',  # Your Railway domain
    ])

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
    'rest_framework_simplejwt',
    'corsheaders',
    
    # Local apps
    'auth_app',
    'invoices',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hisabpro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'invoices', 'templates'),
        ],
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

WSGI_APPLICATION = 'hisabpro.wsgi.application'

# Database
# Use PostgreSQL in production, SQLite in development
if config('DATABASE_URL', default=None):
    # Production database (Railway PostgreSQL)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(config('DATABASE_URL'))
    }
else:
    # Development database (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Supabase Configuration
SUPABASE_URL = config('SUPABASE_URL', default='')
SUPABASE_KEY = config('SUPABASE_KEY', default='')

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
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS settings
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# Production CORS settings
if not DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        'https://hisabpro.vercel.app',  # Your Vercel domain
        'https://*.vercel.app',
    ])
    CORS_ALLOW_ALL_ORIGINS = False
else:
    CORS_ALLOW_ALL_ORIGINS = True

# Email settings (Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='nikhilbajantri86@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='efleuomllopzfcja')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='nikhilbajantri86@gmail.com')

# Razorpay settings - Complete Payment Gateway Configuration
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')
RAZORPAY_WEBHOOK_SECRET = config('RAZORPAY_WEBHOOK_SECRET', default='')

# Business Information (defined early for use in payment config)
BUSINESS_NAME = 'HisabPro'
BUSINESS_EMAIL = 'nikhilbajantri86@gmail.com'
BUSINESS_PHONE = '+91 9096471400'
BUSINESS_ADDRESS = 'Mangalore, Karnataka, India'

# Payment Gateway Configuration
PAYMENT_GATEWAY_CONFIG = {
    'enabled_methods': ['card', 'netbanking', 'wallet', 'upi'],
    'currency': 'INR',
    'theme_color': '#3399cc',
    'company_name': BUSINESS_NAME,
    'company_logo': '',  # Add your logo URL here
    'checkout_logo': '',  # Logo for checkout page
    'allow_rotation': True,
    'remember_customer': True,
    'timeout': 900,  # 15 minutes timeout
    'retry': {
        'enabled': True,
        'max_count': 3
    }
}

# Payment Link Configuration
PAYMENT_LINK_CONFIG = {
    'expire_by': 30,  # Days until payment link expires
    'send_sms': False,  # Keep cost-free
    'send_email': True,
    'reminder_enable': True,
    'callback_url': '',  # Will be set dynamically
    'callback_method': 'get'
}

# Celery settings
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# SMS Configuration (Disabled by default to keep system cost-free)
SMS_ENABLED = config('SMS_ENABLED', default=False, cast=bool)
SMS_API_KEY = config('SMS_API_KEY', default='')
SMS_SENDER_ID = config('SMS_SENDER_ID', default='HISABPRO')
SMS_API_URL = config('SMS_API_URL', default='')

# Reminder System Settings
REMINDER_EMAIL_ONLY = True  # Use email-only reminders to avoid SMS costs
DEFAULT_REMINDER_CHANNEL = 'email'  # Primary channel for reminders

# Additional Business Settings for Invoice Templates
BUSINESS_LOGO = None  # Path to logo file
PAYMENT_TERMS = 'Net 30 days'

# PDF Generation Settings
USE_PLAYWRIGHT_PDF = config('USE_PLAYWRIGHT_PDF', default=True, cast=bool)
USE_WEASYPRINT_PDF = config('USE_WEASYPRINT_PDF', default=True, cast=bool)
USE_REPORTLAB_PDF = config('USE_REPORTLAB_PDF', default=True, cast=bool)

# PDF Generation Options
PDF_GENERATION_OPTIONS = {
    'format': 'A4',
    'margin': {
        'top': '20mm',
        'right': '20mm',
        'bottom': '20mm',
        'left': '20mm'
    },
    'printBackground': True,
    'preferCSSPageSize': True,
    'scale': 1.0,
}

# Playwright Settings (for PDF generation)
PLAYWRIGHT_BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--no-first-run',
    '--no-zygote',
    '--disable-gpu',
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor',
]

SMS_API_KEY = 'your_sms_api_key'
SMS_SENDER_ID = 'HISABPRO'
SMS_API_URL = 'https://your-sms-provider.com/api/send'

BUSINESS_NAME = 'DailyDine'
BUSINESS_EMAIL = 'nikhilbajantri86@gmail.com'
BUSINESS_PHONE = '+91 9019647142'
BUSINESS_ADDRESS = 'Mangalore, Karnataka, India'