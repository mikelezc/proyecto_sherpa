from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from .rate_limit_service import RateLimitService
from django.core.files.base import ContentFile
from .password_service import PasswordService
from authentication.models import UserSession
from .mail_service import MailSendingService
from .token_service import TokenService
from ..models import PreviousPassword
from .gdpr_service import GDPRService
from django.conf import settings
from ..models import CustomUser
from pathlib import Path
import logging
import base64
import time
import re
import os

logger = logging.getLogger(__name__)

class ProfileService:
    def __init__(self):
        self.rate_limiter = RateLimitService()

    @staticmethod
    def handle_image_restoration(user):
        """Simplified - no longer handles images"""
        return "Perfil actualizado"

    @staticmethod
    def handle_email_change(user, new_email):
        """Handles email change for manual users"""
        rate_limiter = RateLimitService()
        is_limited, remaining_time = rate_limiter.is_rate_limited(user.id, 'email_change')
        
        if is_limited:
            logger.warning(f"Rate limit exceeded for user {user.id} on email change")
            raise ValidationError(f"Please wait {remaining_time} seconds before requesting another email change")

        if re.match(r".*@student\.42.*\.com$", new_email.lower()):
            raise ValidationError(
                "Los correos con dominio @student.42*.com están reservados para usuarios de 42")

        if CustomUser.objects.exclude(id=user.id).filter(email=new_email).exists():
            raise ValidationError("Este email ya está en uso")

        token_data = TokenService.generate_email_verification_token(user)
        user.pending_email = new_email
        user.pending_email_token = token_data["token"]
        user.save()

        verification_data = {
            "uid": token_data["uid"], # id user
            "token": token_data["token"], # jwt_token (for email verification)
            "new_email": new_email,
            # send verification URL to user's email (id + jwt_token)
            "verification_url": f"{settings.SITE_URL}/verify-email-change/{token_data['uid']}/{token_data['token']}/"}

        MailSendingService.send_email_change_verification(user, verification_data)
        rate_limiter.reset_limit(user.id, 'email_change') # reset rate limit on successfull email change
        return "Te hemos enviado un email para confirmar el cambio"

    @staticmethod
    def handle_password_change(user, current_password, new_password1, new_password2):
        """Handles password change"""
        PasswordService.validate_password_change( # first check if the old password is correct
            user, current_password, new_password1, new_password2 )
        
        # set_password hashes the password and saves it in the database 
		# (see: https://docs.djangoproject.com/en/3.2/topics/auth/default/#changing-passwords)
        user.set_password(new_password1)
        user.save()

        PreviousPassword.objects.create(user=user, password=user.password)
        return True

    @staticmethod
    def update_profile(user, data, files=None):
        """Updates user profile"""
        rate_limiter = RateLimitService()
        is_limited, remaining_time = rate_limiter.is_rate_limited(user.id, 'profile_update')
        
        if is_limited: # if the user is rate limited, raise an error
            logger.warning(f"Rate limit exceeded for user {user.id} on profile update")
            raise ValidationError(f"Please wait {remaining_time} seconds before updating your profile again")

        try:
            if "email" in data: 
                # Process email changes (simplified - no 42 user restrictions)
                email = data.get("email")
                if email != user.email:
                    if re.match(r".*@student\.42.*\.com$", email.lower()):
                        raise ValidationError(
                            "Los correos con dominio @student.42*.com están reservados para usuarios de 42")

                    if (
                        CustomUser.objects.exclude(id=user.id)
                        .filter(email=email)
                        .exists()
                    ):
                        raise ValidationError("Este email ya está en uso")

                    user.email = email.lower()

            # Save user changes (simplified - no image handling)
            user.save()
            rate_limiter.reset_limit(user.id, 'profile_update') # reset rate limit on successful profile update

            return {
                "email": user.email
            }

        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            raise ValidationError(f"Error al actualizar perfil: {str(e)}")

    @staticmethod
    def restore_default_image(user):
        """Simplified - no longer handles images"""
        try:
            user.save()
            return True
        except Exception as e:
            raise ValidationError(f"Error al actualizar perfil: {str(e)}")

    @staticmethod
    def get_user_profile_data(user):
        """Gets user profile data to display in the profile view (simplified)"""
        if not user.is_authenticated:
            raise ValidationError("Usuario no autenticado")

        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "date_joined": user.date_joined.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
        return data

    @staticmethod
    def delete_user_account(user, password=None):
        """Manages account deletion"""
        # Disclaimer!
		# This method is not used in the current implementation of the project
        # because we use GDPR deletion instead (softer deletion)
		# This is used in the 8000 port development environment but was deprecated in production
        # We keep it here for reference purposes and avoid errors when is called when the project is running
        try:
            # Verify password for account deletion (simplified)
            if not password or not user.check_password(password):
                raise ValidationError("Contraseña incorrecta")
            
            # First delete user sessions
            UserSession.objects.filter(user=user).delete()
            
            # Then we delete the user data
            GDPRService.delete_user_data(user)
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user account: {str(e)}")
            raise ValidationError(f"Error al eliminar la cuenta: {str(e)}")
