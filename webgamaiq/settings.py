import os
from pathlib import Path
import pymysql
from dotenv import load_dotenv
import dj_database_url

pymysql.install_as_MySQLdb()

# Proje ana dizini
BASE_DIR = Path(__file__).resolve().parent.parent

# .env dosyasını yükle
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Güvenlik anahtarı
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default-key")

# Debug modu (True/False string olarak .env'den okunur)
DEBUG = True

# İzin verilen hostlar
ALLOWED_HOSTS = ['webgamaiq-6c22c1463e92.herokuapp.com']

# Veritabanı ayarları
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'WEBgamaIQ_othershow',  # Oluşturacağınız veritabanı adı
        'USER': 'WEBgamaIQ_othershow',     # MySQL kullanıcı adınız (örn: root)
        'PASSWORD': '03965aa81d8b853fb5ed64776c51433d7e6af59b', # MySQL parolanız
        'HOST': '7rg3ai.h.filess.io',           # MySQL sunucunuzun adresi (genellikle localhost)
        'PORT': '3307',                # MySQL portu (varsayılan: 3306)
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}


# Yüklü uygulamalar
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap5',
    'crispy_forms',
    'crispy_bootstrap5',
    'user.apps.UserConfig',
    'inventory.apps.InventoryConfig',
    'company',
    'orders',
    'proforma',
    'documents',
    'quality',
]

AUTH_USER_MODEL = 'user.MyUserModel'

CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Middlewareler
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Statik dosya için
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL konfigürasyonu
ROOT_URLCONF = 'webgamaiq.urls'

# Template ayarları
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # global templates klasörü
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'orders.context_processors.cart_item_count',  # özel context processor
            ],
        },
    },
]

# WSGI ayarı
WSGI_APPLICATION = 'webgamaiq.wsgi.application'

# Parola doğrulama
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
]

# Yerelleştirme
LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Statik dosyalar
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Railway için HTTPS ayarı
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Varsayılan alan tipi
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
