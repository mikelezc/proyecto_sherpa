from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import (
    # auth_views
    home,
    login,
    register,
    logout,
    # pass_reset_views
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    # profile_views
    EditProfileView,
    UserProfileView,
    DeleteAccountView,
    # verify_email_views
    verify_email,
    verify_email_change,
)

# auth_views
auth_patterns = [
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("register/", register, name="register"),
]

# pass_reset_views
password_patterns = [
    path("reset_password/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset_password/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="authentication/password_reset_done.html"
        ),
        name="password_reset_done",
    ),  # este metodo viene del modulo auth_views de django (no es propio)
    path(
        "reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="authentication/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),  # este metodo viene del modulo auth_views de django (no es propio)
]

# profile_views
profile_patterns = [
    path("profile/edit/", EditProfileView.as_view(), name="edit_profile"),
    path("profile/", UserProfileView.as_view(), name="user"),
    path("profile/delete/", DeleteAccountView.as_view(), name="delete_account"),
]

# verify_email_views
verify_email_patterns = [
    path("verify-email/<str:uidb64>/<str:token>/", verify_email, name="verify_email"),
    path(
        "verify-email-change/<str:uidb64>/<token>/",
        verify_email_change,
        name="verify_email_change",
    ),
]

urlpatterns = [
    path("", home, name="home"),
    *auth_patterns,
    *profile_patterns,
    *password_patterns,
    *verify_email_patterns,
]
