from .auth_views import LoginAPIView, LogoutAPIView, RegisterAPIView, RefreshTokenAPIView
from .profile_views import EditProfileAPIView, UserProfileAPIView, DeleteAccountAPIView
from .pass_reset_views import PasswordResetAPIView, PasswordResetConfirmAPIView
from .verify_email_views import VerifyEmailAPIView, VerifyEmailChangeAPIView
from .user_views import UserListAPIView, UserDetailAPIView, UserMeAPIView

__all__ = [
    # Verification email views
    'VerifyEmailAPIView',
	'VerifyEmailChangeAPIView',

    # Auth views
    'LoginAPIView',
    'LogoutAPIView', 
    'RegisterAPIView',
    'RefreshTokenAPIView',

    # User management views
    'UserListAPIView',
    'UserDetailAPIView',
    'UserMeAPIView',

    # Profile views
    'EditProfileAPIView',
	'UserProfileAPIView',
	'DeleteAccountAPIView',
    
    # Pass_reset views
    'PasswordResetAPIView',
    'PasswordResetConfirmAPIView'
]