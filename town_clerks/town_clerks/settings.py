import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-change-me')
DEBUG = os.environ.get('DEBUG', '1') == '1'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,apps.easthartfordct.gov').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clerks',
    'django_auth_adfs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'clerks.middleware.ActivityLogMiddleware',
]

ROOT_URLCONF = 'town_clerks.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        BASE_DIR / 'clerks' / 'templates',
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
}]

WSGI_APPLICATION = 'town_clerks.wsgi.application'

# Shared Connection Details for TOEHSQL1
DB_HOST = os.environ.get('DB_HOST', 'TOEHSQL1')
DB_PORT = os.environ.get('DB_PORT', '1433')
DB_USER = os.environ.get('DB_USER', 'Michael')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'D3lt@kil0')
DB_DRIVER_OPTIONS = {
    'driver': 'ODBC Driver 18 for SQL Server',
    'extra_params': 'Encrypt=yes;TrustServerCertificate=yes;'
}

DATABASES = {
    # 1. 'default' (Clerk): Main Django App DB for Auth, Sessions, and new app tables.
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.environ.get('DB_NAME', 'Clerk'), 
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': DB_DRIVER_OPTIONS,
    },

    # 2. 'marriage' (Legacy Data): Marriage Licenses
    'marriage': {
        'ENGINE': 'mssql',
        'NAME': 'Marriage',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': DB_DRIVER_OPTIONS,
    },

    # 3. 'vets' (Legacy Data): Veteran Records
    'vets': {
        'ENGINE': 'mssql',
        'NAME': 'Vets',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': DB_DRIVER_OPTIONS,
    },

    # 4. 'vitals' (Legacy Data): Death Vitals
    'vitals': {
        'ENGINE': 'mssql',
        'NAME': 'DeathVitals',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': DB_DRIVER_OPTIONS,
    },

    # 5. 'transmitel' (Legacy Data): Clerk Transmittal
    'transmitel': {
        'ENGINE': 'mssql',
        'NAME': 'Clerk_Transmittal',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': DB_DRIVER_OPTIONS,
    },
}

AUTHENTICATION_BACKENDS = [
    'django_auth_adfs.backend.AdfsAuthCodeBackend',
    'django.contrib.auth.backends.ModelBackend',
]

DATABASE_ROUTERS = ['town_clerks.db_routers.ClerkRouter']

# Disable migrations for unmanaged 'permits' app
MIGRATION_MODULES = {
    # Legacy tables use managed=False; keep migrations enabled so we can add app-owned tables like ActivityLog.
}

LOGIN_URL = 'django_auth_adfs:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

LOGIN_EXEMPT_URLS = [
    r'^oauth2/.*',
    r'^static/.*',
    r'^favicon\.ico$',
]

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'clerks' / 'static']

AUTH_ADFS = {
    'TENANT_ID': os.environ.get('ADFS_TENANT_ID',''),
    'CLIENT_ID': os.environ.get('ADFS_CLIENT_ID',''),
    'CLIENT_SECRET': os.environ.get('ADFS_CLIENT_SECRET',''),
    'REDIR_URI': os.environ.get('ADFS_REDIRECT_URI','http://localhost:8000/oauth2/callback/'),
    'SCOPES': ['openid','profile','email','offline_access','User.Read'],
    'CLAIM_MAPPING': {'first_name':'given_name','last_name':'family_name','email':'email'},
    'USERNAME_CLAIM':'upn',
    'GROUPS_CLAIM':'roles',
    'MIRROR_GROUPS': True,
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = False  # Set to False for local troubleshooting
CSRF_COOKIE_SECURE = False     # Set to False for local troubleshooting

_csrf_env = os.environ.get('CSRF_TRUSTED_ORIGINS')
if _csrf_env:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_env.split(',') if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        f"https://{h.strip()}" for h in ALLOWED_HOSTS
        if h and h.strip() not in ('localhost','127.0.0.1') and not h.startswith('*.')
    ]
