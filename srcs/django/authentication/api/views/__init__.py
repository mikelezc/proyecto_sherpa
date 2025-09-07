from .auth_views import LoginAPIView, LogoutAPIView, RegisterAPIView
from .gdpr_views import GDPRSettingsAPIView, ExportPersonalDataAPIView, PrivacyPolicyAPIView
from .profile_views import EditProfileAPIView, UserProfileAPIView, DeleteAccountAPIView
from .pass_reset_views import PasswordResetAPIView, PasswordResetConfirmAPIView
from .verify_email_views import VerifyEmailAPIView, VerifyEmailChangeAPIView

__all__ = [
    # Verification email views
    'VerifyEmailAPIView',
	'VerifyEmailChangeAPIView',

    # Auth views
    'LoginAPIView',
    'LogoutAPIView', 
    'RegisterAPIView',

    # GDPR views
    'GDPRSettingsAPIView',
    'ExportPersonalDataAPIView',
    'PrivacyPolicyAPIView',

    # Profile views
    'EditProfileAPIView',
	'UserProfileAPIView',
	'DeleteAccountAPIView',
    
    # Pass_reset views
    'PasswordResetAPIView',
    'PasswordResetConfirmAPIView'
]