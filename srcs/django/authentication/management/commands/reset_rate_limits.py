from django.core.management.base import BaseCommand
from django.core.cache import cache
import redis
from django.conf import settings


class Command(BaseCommand):
    help = 'Reset all rate limits for demo purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Reset rate limits for specific user ID',
        )
        parser.add_argument(
            '--ip',
            type=str,
            help='Reset rate limits for specific IP address',
        )

    def handle(self, *args, **options):
        try:
            # Connect to Redis
            redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
            
            if options['user_id']:
                # Reset for specific user
                user_id = options['user_id']
                keys = redis_client.keys(f"rate_limit:{user_id}:*")
                if keys:
                    redis_client.delete(*keys)
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Rate limits reset for user {user_id}')
                    )
                else:
                    self.stdout.write(f'No rate limits found for user {user_id}')
                    
            elif options['ip']:
                # Reset for specific IP
                ip = options['ip']
                keys = redis_client.keys(f"rate_limit:{ip}:*")
                if keys:
                    redis_client.delete(*keys)
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Rate limits reset for IP {ip}')
                    )
                else:
                    self.stdout.write(f'No rate limits found for IP {ip}')
                    
            else:
                # Reset all rate limits
                keys = redis_client.keys("rate_limit:*")
                if keys:
                    redis_client.delete(*keys)
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ All rate limits reset ({len(keys)} keys cleared)')
                    )
                else:
                    self.stdout.write('No rate limits found to reset')
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error resetting rate limits: {e}')
            )
