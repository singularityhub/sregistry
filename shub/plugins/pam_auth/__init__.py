AUTHENTICATION_BACKENDS = (
    "django_pam.auth.backends.PAMBackend",
    "django.contrib.auth.backends.ModelBackend",
)
