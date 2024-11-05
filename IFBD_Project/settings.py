from pathlib import Path
import os
from datetime import timedelta
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config('SECRET_KEY')


IS_DEVELOPMENT = config('IS_DEVELOPMENT')


if IS_DEVELOPMENT == 'True':
    DEBUG = True
else:
    DEBUG = False



if DEBUG:
    ALLOWED_HOSTS = ["dd3a-2405-204-148c-769c-f5eb-41ec-da55-984a.ngrok-free.app", "127.0.0.1"]

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

    STATICFILES_DIRS = [ os.path.join(BASE_DIR, "static"), ]

else:
    ALLOWED_HOSTS = ["api.famousbusiness.com", "www.api.famousbusiness.in", "127.0.0.1", "*", "www.mdwebzotica.famousbusiness.in"]

    # SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    # SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    # CSRF_COOKIE_SAMESITE = "Lax"

    # CORS_ALLOW_CREDENTIALS = True
    # CORS_EXPOSE_HEADERS = ["Content-Type", "csrftoken"]


    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'http')

    MEDIA_URL = 'https://mdwebzotica.famousbusiness.in/'
    MEDIA_ROOT = BASE_DIR / '../webzoticafbmedia/'

    STATIC_ROOT = BASE_DIR / 'static'




STATIC_URL = 'static/'
INTERNAL_IPS = [
    "127.0.0.1",
]




INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps
    'users.apps.UsersConfig',
    'Listings.apps.ListingsConfig',
    'Messenger.apps.MessengerConfig',
    'JOB.apps.JobConfig',
    'Lead.apps.LeadConfig',
    'PremiumPlan.apps.PremiumplanConfig',
    'Brands.apps.BrandsConfig',
    'Banner.apps.BannerConfig',
    'Software.apps.SoftwareConfig',
    'ADS.apps.AdsConfig',
    'Tender.apps.TenderConfig',
    # 3rdparty apps
    'rest_framework',
    'rest_framework_simplejwt',
    "corsheaders",
    'rest_framework_simplejwt.token_blacklist',
    'django_celery_results',
    'django_extensions',
    'django_celery_beat',
    'crispy_forms',
    'crispy_bootstrap5',
    # 'debug_toolbar',
]

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'users.authenticate.EmailAuthBackend',
]

MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'IFBD_Project.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


WSGI_APPLICATION = 'IFBD_Project.wsgi.application'
ASGI_APPLICATION = 'IFBD_Project.asgi.application'


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432', 
    },



    # 'slave': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': config('DB_NAME_SLAVE'),
    #     'USER': config('DB_USER_SLAVE'),
    #     'PASSWORD': config('DB_PASSWORD_SLAVE'),
    #     'HOST': 'localhost',
    #     'PORT': '5432', 
    # },

}


# DATABASE_ROUTERS = ['IFBD_Project.routers.ReadWriteRouter']


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


TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Twilio Setup
# ACCOUNT_SID = config('ACCOUNT_SID')
# AUTH_TOKEN = config('AUTH_TOKEN')
# TWILIO_WHATSAPP_NUMBER = config('TWILIO_WHATSAPP_NUMBER')
# TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER')
# COUNTRY_CODE = config('COUNTRY_CODE')



REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100

}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "UPDATE_LAST_LOGIN": True,
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",

}


CORS_ALLOWED_ORIGINS = [
    "https://famousbusiness.in",
    "https://www.famousbusiness.in",
    "http://famousbusiness.in",
    "http://www.famousbusiness.in",
    "https://mdwebzotica.famousbusiness.in",
    "http://mdwebzotica.famousbusiness.in",
    "http://localhost:3000"
]


# Celery
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_RESULT_BACKEND = 'django-db'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_CACHE_BACKEND = 'default'
# CELERY_CACHE_BACKEND = 'django-cache'

# Celery Beat
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "famousbusiness_redis"
    }
}


#Password Reset 
PASSWORD_RESET_TIMEOUT = 900
# PASSWORD_RESET_TIMEOUT = 60 * 60 * 48


#Redis Caching
CACHE_TTL = 60 * 15

# SMTP Settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'customercare@famousbusiness.in'

AWS_SES_REGION_NAME = 'ap-south-1'
AWS_SES_REGION_ENDPOINT = 'email-smtp.ap-south-1.amazonaws.com'
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')




# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'ERROR',
#             'class': 'logging.FileHandler',
#             'filename': '/var/log/gunicorn/error.log',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],   
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     },
# }


RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET')


DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024

CRISPY_TEMPLATE_PACK = 'bootstrap5'

