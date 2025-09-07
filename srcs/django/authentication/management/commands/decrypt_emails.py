from django.core.management.base import BaseCommand
from django.conf import settings
from authentication.models import CustomUser
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Decrypt all encrypted emails in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting email decryption process...'))
        
        if not hasattr(settings, 'ENCRYPTION_KEY') or not settings.ENCRYPTION_KEY:
            self.stdout.write(self.style.ERROR('ENCRYPTION_KEY not found in settings'))
            return
            
        cipher_suite = Fernet(settings.ENCRYPTION_KEY)
        users_updated = 0
        
        for user in CustomUser.objects.all():
            if user.email and user.email.startswith('gAAAAAB'):  # Encrypted email
                try:
                    decrypted_email = cipher_suite.decrypt(user.email.encode()).decode()
                    user.email = decrypted_email
                    user.save()
                    users_updated += 1
                    self.stdout.write(f'Decrypted email for user: {user.username}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to decrypt email for user {user.username}: {str(e)}')
                    )
                    
        self.stdout.write(
            self.style.SUCCESS(f'Successfully decrypted {users_updated} user emails')
        )
