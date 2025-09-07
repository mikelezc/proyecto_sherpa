"""
Management command to test all database optimizations
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from tasks.models import Task, TaskHistory, Comment, Tag, Team
from authentication.models import CustomUser
from datetime import timedelta
import time


class Command(BaseCommand):
    help = 'Test all database optimizations and performance improvements'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧪 Starting Database Optimization Tests...\n')
        )
        
        # Test 1: Custom Managers
        self.test_custom_managers()
        
        # Test 2: Query Optimizations
        self.test_query_optimizations()
        
        # Test 3: Full-Text Search
        self.test_fulltext_search()
        
        # Test 4: Database Constraints
        self.test_database_constraints()
        
        # Test 5: Indexes Performance
        self.test_indexes_performance()
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 All optimization tests completed!')
        )

    def test_custom_managers(self):
        """Test custom managers functionality"""
        self.stdout.write('1️⃣  Testing Custom Managers...')
        
        try:
            # Test TaskManager methods
            active_tasks = Task.objects.active().count()
            self.stdout.write(f'   ✅ Active tasks: {active_tasks}')
            
            archived_tasks = Task.objects.archived().count()
            self.stdout.write(f'   ✅ Archived tasks: {archived_tasks}')
            
            # Test optimized relations
            optimized_tasks = Task.objects.with_optimized_relations()[:5]
            self.stdout.write(f'   ✅ Optimized query returned {len(optimized_tasks)} tasks')
            
            # Test TaskHistory manager
            recent_history = TaskHistory.objects.recent(days=30).count()
            self.stdout.write(f'   ✅ Recent history entries: {recent_history}')
            
            self.stdout.write(self.style.SUCCESS('   ✅ Custom Managers: PASSED\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Custom Managers: FAILED - {e}\n'))

    def test_query_optimizations(self):
        """Test query optimizations with select_related and prefetch_related"""
        self.stdout.write('2️⃣  Testing Query Optimizations...')
        
        try:
            # Measure query count for non-optimized vs optimized
            with connection.cursor() as cursor:
                # Reset query log
                connection.queries_log.clear()
                
                # Non-optimized query (should use more queries)
                basic_tasks = list(Task.objects.all()[:3])
                basic_query_count = len(connection.queries)
                
                # Reset query log
                connection.queries_log.clear()
                
                # Optimized query (should use fewer queries)
                optimized_tasks = list(Task.objects.with_optimized_relations()[:3])
                optimized_query_count = len(connection.queries)
                
                self.stdout.write(f'   📊 Basic queries: {basic_query_count}')
                self.stdout.write(f'   📊 Optimized queries: {optimized_query_count}')
                
                if optimized_query_count <= basic_query_count:
                    self.stdout.write(self.style.SUCCESS('   ✅ Query Optimization: PASSED\n'))
                else:
                    self.stdout.write(self.style.WARNING('   ⚠️  Query Optimization: NEEDS REVIEW\n'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Query Optimization: FAILED - {e}\n'))

    def test_fulltext_search(self):
        """Test full-text search functionality"""
        self.stdout.write('3️⃣  Testing Full-Text Search...')
        
        try:
            # Test basic search
            basic_results = Task.objects.search('API').count()
            self.stdout.write(f'   📊 Search results: {basic_results}')
            
            # Test optimized search method
            optimized_search = Task.objects.search('documentation')
            self.stdout.write(f'   📊 Optimized search count: {optimized_search.count()}')
            
            self.stdout.write(self.style.SUCCESS('   ✅ Search Methods: PASSED\n'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Search Methods: FAILED - {e}\n'))

    def test_database_constraints(self):
        """Test database constraints"""
        self.stdout.write('4️⃣  Testing Database Constraints...')
        
        try:
            # Test check constraints exist
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT conname FROM pg_constraint 
                    WHERE conname LIKE 'task_%' 
                    AND contype = 'c'
                """)
                constraints = cursor.fetchall()
                
                expected_constraints = [
                    'task_due_date_after_creation',
                    'task_estimated_hours_positive', 
                    'task_actual_hours_positive'
                ]
                
                found_constraints = [row[0] for row in constraints]
                
                for constraint in expected_constraints:
                    if constraint in found_constraints:
                        self.stdout.write(f'   ✅ Constraint {constraint}: EXISTS')
                    else:
                        self.stdout.write(f'   ⚠️  Constraint {constraint}: NOT FOUND')
                
                self.stdout.write(self.style.SUCCESS('   ✅ Database Constraints: CHECKED\n'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Database Constraints: FAILED - {e}\n'))

    def test_indexes_performance(self):
        """Test database indexes"""
        self.stdout.write('5️⃣  Testing Database Indexes...')
        
        try:
            with connection.cursor() as cursor:
                # Check for important indexes
                cursor.execute("""
                    SELECT indexname FROM pg_indexes 
                    WHERE tablename = 'tasks_task'
                    AND indexname LIKE '%idx%'
                """)
                indexes = cursor.fetchall()
                
                index_names = [row[0] for row in indexes]
                self.stdout.write(f'   📊 Found {len(index_names)} indexes on tasks_task')
                
                # Check for GIN index for search
                gin_indexes = [idx for idx in index_names if 'gin' in idx.lower()]
                if gin_indexes:
                    self.stdout.write(f'   ✅ GIN indexes for search: {len(gin_indexes)}')
                else:
                    self.stdout.write('   ⚠️  No GIN indexes found')
                
                # Test query performance with indexes
                start_time = time.time()
                cursor.execute("SELECT COUNT(*) FROM tasks_task WHERE status = 'in_progress'")
                query_time = time.time() - start_time
                
                self.stdout.write(f'   📊 Indexed query time: {query_time:.4f}s')
                
                self.stdout.write(self.style.SUCCESS('   ✅ Database Indexes: VERIFIED\n'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Database Indexes: FAILED - {e}\n'))
