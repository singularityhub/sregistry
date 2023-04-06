from django.contrib.auth import views as auth_views
from django.urls import re_path

urlpatterns = [
    re_path(
        r"^login/$",
        auth_views.LoginView.as_view(template_name="pam_auth/login.html"),
        name="pam_auth-login",
    ),
    re_path(
        r"^logout/(?P<next>[\w\-\:/]+)?$",
        auth_views.LoginView.as_view(template_name="pam_auth/logout.html"),
        name="pam_auth-logout",
    ),
]
