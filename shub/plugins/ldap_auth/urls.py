from django.contrib.auth import views as auth_views
from django.urls import re_path

urlpatterns = [
    re_path(
        r"^login/$",
        auth_views.LoginView.as_view(template_name="ldap_auth/login.html"),
        name="ldap_auth-login",
    )
]
