"""
Django settings for flutype_webapp deployment
"""
DEFAULT_USER_PASSWORD = 'flutype_deploy'
DEBUG = True
SECRET_KEY = ')3=*+@k14$yy(*(by2yw11ff)hikowucv&hz+v8qq_8a4*@pm-'
INTERNAL_IPS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'flutype',
        'USER': 'mkoenig',
        'HOST': 'localhost',
        'PASSWORD': 'Xac53abc7X',
        'PORT': 5432,
    }
}
