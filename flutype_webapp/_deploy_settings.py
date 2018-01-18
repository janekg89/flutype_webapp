"""
Django settings for flutype_webapp deployment
"""
DEFAULT_USER_PASSWORD = 'flutype_deploy'
DEBUG = True
SECRET_KEY = 'kqze_+en7mns%zl3m8qd7^r93*mif=b8(9*z*dcj!)bu!3qm__'
INTERNAL_IPS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'flutype',
        'USER': 'mkoenig',
        'HOST': 'localhost',
        'PASSWORD': 'abc7XVFDASD978739u0jklibasd_ac53',
        'PORT': 5432,
    }
}
