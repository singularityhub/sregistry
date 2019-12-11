from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(
        r"^login/$",
        auth_views.LoginView.as_view(template_name="pam_auth/login.html"),
        name="pam_auth-login",
    ),
    url(
        r"^logout/(?P<next>[\w\-\:/]+)?$",
        auth_views.LoginView.as_view(template_name="pam_auth/logout.html"),
        name="pam_auth-logout",
    ),
]
