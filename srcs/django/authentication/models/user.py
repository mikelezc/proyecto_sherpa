from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.apps import apps
import logging

# This model is used to store the user information and manage the user's account

logger = logging.getLogger(__name__)

class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True) # id is the primary key for the user

    # Add related_name to fix the conflict
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_users',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_users',
        help_text='Specific permissions for this user.',
    )

    # Core user fields (simplified)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    email_token_created_at = models.DateTimeField(null=True, blank=True)
    pending_email = models.EmailField(blank=True, null=True)
    pending_email_token = models.CharField(max_length=255, blank=True, null=True)
    inactivity_notified = models.BooleanField(default=False)
    inactivity_notification_date = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Add manager
    from .managers import CustomUserManager
    objects = CustomUserManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        """Save user - simplified without email encryption"""
        super().save(*args, **kwargs)

    def get_last_activity(self):
        """
        Returns the most recent activity time from last_login, sessions or date_joined.
        
        This method determines the user's most recent activity by comparing:
        - Last login timestamp
        - Session activity records
        - Account creation date (as fallback)
        
        This is used by cleanup tasks to determine if a user should be notified or deleted.
        """
        UserSession = apps.get_model('authentication', 'UserSession')
        
        # If user has never logged in, use date_joined
        last_activity = self.last_login or self.date_joined
        
        # Consider active sessions
        active_session = UserSession.objects.filter(
            user=self
        ).order_by('-last_activity').first()
        
        if active_session and active_session.last_activity > last_activity:
            return active_session.last_activity
        
        return last_activity

    def should_notify_inactivity(self):
        """ Check if user should receive inactivity warning."""
        if self.inactivity_notified or not self.last_login:
            return False
            
        last_activity = self.get_last_activity()
        inactive_seconds = (timezone.now() - last_activity).total_seconds()
        return inactive_seconds >= settings.INACTIVITY_WARNING

    def is_inactive_for_too_long(self):
        """ Check if user should be deleted due to inactivity."""
        if not self.inactivity_notified or not self.inactivity_notification_date:
            return False

        current_time = timezone.now()
        warning_age = (current_time - self.inactivity_notification_date).total_seconds()
        total_inactive = (current_time - self.get_last_activity()).total_seconds()

        return (warning_age >= settings.INACTIVITY_WARNING and 
                total_inactive >= settings.INACTIVITY_THRESHOLD)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username


class PreviousPassword(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="previous_passwords"
    )
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]
        verbose_name = "Contraseña anterior"
        verbose_name_plural = "Contraseñas anteriores"

    def save(self, *args, **kwargs):
        if self.__class__.objects.filter(user=self.user).count() >= 3:
            oldest = (
                self.__class__.objects.filter(user=self.user)
                .order_by("created_at")
                .first()
            )
            if oldest:
                oldest.delete()
        super().save(*args, **kwargs)
