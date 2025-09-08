"""
Management command to update search vectors for all existing tasks
"""

from django.core.management.base import BaseCommand
from django.db import connection
from tasks.models import Task


class Command(BaseCommand):
    help = 'Update search vectors for all existing tasks to enable full-text search'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of tasks to process in each batch (default: 100)',
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        
        self.stdout.write(
            self.style.SUCCESS('Starting search vector update for all tasks...')
        )
        
        try:
            # Get total count
            total_tasks = Task.objects.count()
            self.stdout.write(f'Found {total_tasks} tasks to process')
            
            if total_tasks == 0:
                self.stdout.write(
                    self.style.WARNING('No tasks found. Nothing to update.')
                )
                return
            
            # Update search vectors in batches using raw SQL for efficiency
            with connection.cursor() as cursor:
                self.stdout.write('Updating search vectors using PostgreSQL full-text search...')
                
                cursor.execute("""
                    UPDATE tasks_task 
                    SET search_vector = to_tsvector('english', 
                        COALESCE(title, '') || ' ' || COALESCE(description, '')
                    )
                    WHERE search_vector IS NULL OR search_vector = ''
                """)
                
                updated_rows = cursor.rowcount
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Successfully updated search vectors for {updated_rows} tasks'
                    )
                )
                
                # Create GIN index if it doesn't exist
                try:
                    cursor.execute("""
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS task_search_vector_gin_idx 
                        ON tasks_task USING gin(search_vector)
                    """)
                    self.stdout.write(
                        self.style.SUCCESS('✅ GIN index created/verified for search optimization')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Could not create GIN index: {e}')
                    )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error updating search vectors: {e}')
            )
            
            # Fallback: update using Django ORM (slower but more compatible)
            self.stdout.write('Falling back to Django ORM update...')
            
            updated = 0
            for task in Task.objects.all():
                try:
                    task.update_search_vector()
                    updated += 1
                    
                    if updated % batch_size == 0:
                        self.stdout.write(f'Processed {updated}/{total_tasks} tasks...')
                        
                except Exception as task_error:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Could not update task {task.id}: {task_error}'
                        )
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Fallback update completed for {updated} tasks')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                '🎉 Search vector update process completed! Full-text search is now optimized.'
            )
        )
