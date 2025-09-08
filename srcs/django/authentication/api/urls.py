from django.urls import path
from ninja import NinjaAPI
from authentication.api.controllers import router as auth_router
from authentication.api.controllers.user_controller import router as user_router

from .views import (
    # auth_views
    LoginAPIView,
    LogoutAPIView,
    RegisterAPIView,
    RefreshTokenAPIView,
    # pass_reset_views
    PasswordResetAPIView,
    PasswordResetConfirmAPIView,
    # profile_views
    EditProfileAPIView,
    UserProfileAPIView,
    DeleteAccountAPIView,
    # verify_email_views
    VerifyEmailAPIView,
    VerifyEmailChangeAPIView,
)

from .views.user_views import (
    UserListAPIView,
    UserDetailAPIView,
    UserMeAPIView,
)

# Django Ninja Configuration
api = NinjaAPI(
    title="Authentication API",
    version="2.0.0",
    description="API para autenticación",
    urls_namespace="auth_api",
    docs_url="/docs",
)

# Add authentication router to root level to match /api/auth/ routes
api.add_router("/", auth_router)

# Authentication views
auth_patterns = [
    path("login/", LoginAPIView.as_view(), name="api_login"),
    path("logout/", LogoutAPIView.as_view(), name="api_logout"),
    path("register/", RegisterAPIView.as_view(), name="api_register"),
    path("refresh/", RefreshTokenAPIView.as_view(), name="api_refresh"),
]

# Profile views
profile_patterns = [
    path("profile/", EditProfileAPIView.as_view(), name="api_profile"),
    path("profile/user/", UserProfileAPIView.as_view(), name="api_user_profile"),
    path(
        "profile/delete-account/",
        DeleteAccountAPIView.as_view(),
        name="api_delete_account",
    ),
]

# Password reset views
password_patterns = [
    path("password/reset/", PasswordResetAPIView.as_view(), name="api_password_reset"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmAPIView.as_view(),
        name="api_password_reset_confirm",
    ),
]

# Email verification views
verification_patterns = [
    path(
        "verify-email/<str:uidb64>/<str:token>/",
        VerifyEmailAPIView.as_view(),
        name="api_verify_email",
    ),
    path(
        "verify-email-change/<str:uidb64>/<str:token>/",
        VerifyEmailChangeAPIView.as_view(),
        name="api_verify_email_change",
    ),
]

# User management views
user_patterns = [
    path("users/", UserListAPIView.as_view(), name="api_users_list"),
    path("users/<int:user_id>/", UserDetailAPIView.as_view(), name="api_user_detail"),
    path("users/me/", UserMeAPIView.as_view(), name="api_user_me"),
]

urlpatterns = [
    *auth_patterns,
    *profile_patterns,
    *password_patterns,
    *verification_patterns,
    *user_patterns,
    path("", api.urls),  # Changed from "ninja/" to "" to match /api/auth/docs directly
]

"""
ABSOLUTE API URLs (Base: http://localhost:8000):

 AUTHENTICATION (Django URLs):
   * http://localhost:8000/api/login/
   * http://localhost:8000/api/logout/
   * http://localhost:8000/api/register/

 GDPR AND PRIVACY (Django URLs):
   * http://localhost:8000/api/gdpr/settings/
   * http://localhost:8000/api/gdpr/export-data/
   * http://localhost:8000/api/gdpr/privacy-policy/

 PROFILE (Django URLs):
   * http://localhost:8000/api/profile/
   * http://localhost:8000/api/profile/user/
   * http://localhost:8000/api/profile/delete-account/

 PASSWORD (Django URLs):
   * http://localhost:8000/api/password/reset/
   * http://localhost:8000/api/password/reset/confirm/

 EMAIL (Django URLs):
   * http://localhost:8000/api/verify-email/<str:uidb64>/<str:token>/
   * http://localhost:8000/api/verify-email-change/<str:uidb64>/<str:token>/

 QR AND 2FA (Django URLs):
   * http://localhost:8000/api/generate-qr/<str:username>/
   * http://localhost:8000/api/validate-qr/
   * http://localhost:8000/api/enable-2fa/
   * http://localhost:8000/api/verify-2fa/
   * http://localhost:8000/api/disable-2fa/

 DJANGO NINJA (New API):
   * http://localhost:8000/api/ninja/docs         -> Swagger/OpenAPI Documentation
   * http://localhost:8000/api/ninja/openapi.json -> OpenAPI Specification
"""
