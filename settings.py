import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")
DEBUG = os.environ.get('DEBUG', '0') == '1'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    if DEBUG: SECRET_KEY = 'local-development-only-do-not-use-in-production'
    else: raise RuntimeError('DJANGO_SECRET_KEY kiriting: admin sessiyalari uchun doimiy maxfiy kalit kerak')
if not DEBUG and (len(SECRET_KEY) < 50 or SECRET_KEY.startswith('replace-')):
    raise RuntimeError('DJANGO_SECRET_KEY kamida 50 belgili va haqiqiy tasodifiy qiymat bo‘lishi kerak')
ALLOWED_HOSTS = [x.strip() for x in os.environ.get('ALLOWED_HOSTS','localhost,127.0.0.1,[::1]').split(',') if x.strip()]
if os.environ.get('RAILWAY_PUBLIC_DOMAIN'): ALLOWED_HOSTS.append(os.environ['RAILWAY_PUBLIC_DOMAIN'])
CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.environ.get('CSRF_TRUSTED_ORIGINS','').split(',') if x.strip()]
ROOT_URLCONF = 'website.urls'
INSTALLED_APPS = ['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','website.apps.WebsiteConfig']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware']
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],
    'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
DATA_ROOT = Path(os.environ.get('DATA_ROOT', str(BASE_DIR/'var')))
DATA_ROOT.mkdir(parents=True, exist_ok=True)
DATABASES = {'default':{'ENGINE':'django.db.backends.sqlite3','NAME':os.environ.get('SQLITE_PATH',str(DATA_ROOT/'website.sqlite3'))}}
MEDIA_ROOT = os.environ.get('MEDIA_ROOT',str(DATA_ROOT/'media'))
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
STATIC_ROOT = DATA_ROOT/'static'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USE_TZ = True
TIME_ZONE = 'Asia/Tashkent'
LANGUAGE_CODE = 'uz'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO','https')
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
X_FRAME_OPTIONS = 'DENY'
AUTH_PASSWORD_VALIDATORS = [
 {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
 {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
 {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
 {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
