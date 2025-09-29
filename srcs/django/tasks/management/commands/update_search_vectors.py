"""
Management command to update search vectors for all existing tasks

This command maintains PostgreSQL full-text search functionality by updating
the search_vector field (is like index) for existing tasks weekly.

This is used by weekly-search-maintenance task.

Simplified to use consolidated search.py functionality
"""

from django.core.management.base import BaseCommand
from tasks.core.search import update_all_search_vectors, rebuild_search_index


class Command(BaseCommand):
    help = 'Update search vectors for all existing tasks to enable full-text search'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of tasks to process in each batch (default: 100)',
        )
        parser.add_argument(
            '--rebuild',
            action='store_true',
            help='Force rebuild entire search index',
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        rebuild = options['rebuild']
        
        self.stdout.write(
            self.style.SUCCESS('Starting search vector update for all tasks...')
        )
        
        try:
            if rebuild:
                result = rebuild_search_index()
            else:
                result = update_all_search_vectors(batch_size)
            
            if result.get('success', True):  # update_all_search_vectors doesn't have success key
                self.stdout.write(
                    self.style.SUCCESS(result['message'])
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Error: {result['error']}")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )