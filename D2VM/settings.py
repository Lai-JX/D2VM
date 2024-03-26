"""
Django settings for D2VM project.

Generated by 'django-admin startproject' using Django 4.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%cq5$25+8(6v__j$7_-@1m5f6j@f2hm6$*a3ib-&@g6$bxxj7y'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 用于配置能够访问当前站点的域名（IP地址），当 DEBUG = False 时，必须填写(如果是在本机的话，可能不用？)
# ALLOWED_HOSTS = ['10.249.43.60','192.168.1.104']
#部署到云服务上必备
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'container',
    'image',
    'user',
    'node',
    'django_q',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',        # 跨域访问
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS_ORIGIN_WHITELIST = (
#     'http://10.249.43.60:32326',
# )
# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOW_HEADERS = ('x-csrftoken', 'authorization', 'content-type', 'Content-Disposition')
# 跨域增加忽略
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = (
#     '*',
# )
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

ROOT_URLCONF = 'D2VM.urls'

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

WSGI_APPLICATION = 'D2VM.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        # 连接本地mysql数据库
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'D2VM',          #你的数据库名
        'USER': 'root',         # 你的用户名
        'PASSWORD': 'root',   #你的密码
        'HOST': 'localhost',    # 本地连接
        'PORT': '3306',         # 本地端口号

    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True
# true表示存储到数据库的时间是世界时间
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'static'), os.path.join(BASE_DIR, 'pod_config'), ]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 让 Django 能够识别使用自定义的用户模型
AUTH_USER_MODEL = 'user.user'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# 配置文件存储路径
POD_CONFIG = os.path.join(BASE_DIR, 'pod_config/')
MEDIA_ROOT = POD_CONFIG
MEDIA_URL = '/pod_config/'

# 配置密码哈希算法
AUTH_PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

# NFS_IP
NFS_IP = '10.249.41.228'                    # 用户workspace目录使用的nfs
NFS_IP_SHARE = '10.249.41.228'              # 用户share目录使用的nfs
NFS_SSH = 'ssh shuhanqi@10.249.41.228'      # 为用户创建workspace目录对应的ssh
NFS_DIR_PREFIX = '/volume1/VM/'             # 路径前缀

# SAVE_IMAGE_PATH 如'http://10.249.40.11:32325/image/save'
D2VM_IP = '10.249.40.11' # 发出save请求的终点IP
D2VM_PORT = 32325
TIME_WAIT_FOR_APPLY=5

DOCKER_PULL_PUSH_IP = '10.249.40.11' # 使用哪台机器拉取镜像
REGISTERY_IP = '192.158.0.10'      # 私有镜像仓库地址
REGISTERY_PATH = '192.158.0.10:5010'   

# 发送邮箱验证码
EMAIL_HOST = "smtp.163.com"     # 服务器
EMAIL_PORT = 25                 # 一般情况下都为25
EMAIL_HOST_USER = "hitsz_haios@163.com"     # 账号
EMAIL_HOST_PASSWORD = "*****"          # 密码 (注意：这里的密码指的是授权码)
EMAIL_USE_TLS = False       # 一般都为False
EMAIL_FROM = "hitsz_haios@163.com"      # 邮箱来自

# redis缓存
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }   
    }   
}

Q_CLUSTER = {
    'name': 'project_name',
    'workers': 4,
    'recycle': 500,
    'timeout': 7200,        # 超时时间两小时
    'retry': 7201,
    'compress': True,
    'cpu_affinity': 1,
    'save_limit': 250,
    'queue_limit': 500,
    'label': 'Django Q',
    'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
    }
}
