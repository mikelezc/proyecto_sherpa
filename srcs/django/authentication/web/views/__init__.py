from .auth_views import home, login, register, logout
from .gdpr_views import gdpr_settings, export_personal_data, privacy_policy
from .pass_reset_views import CustomPasswordResetView, CustomPasswordResetConfirmView
from .profile_views import EditProfileView, UserProfileView, DeleteAccountView
from .verify_email_views import verify_email, verify_email_change


__all__ = [
    "home",
    "login",
    "register",
    "logout",
    "gdpr_settings",
    "export_personal_data",
    "privacy_policy",
    "CustomPasswordResetView",
    "CustomPasswordResetConfirmView",
    "EditProfileView",
    "UserProfileView",
    "DeleteAccountView",
    "verify_email",
    "verify_email_change",
]
