"""
Task Search & Indexing

Full-text search functionality and batch indexing operations.
Consolidates search queries and search vector management.
"""

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db import connection


def search_tasks(task_model_class, query):
    """
    Perform full-text search on tasks (moved from Task.search_tasks)
    """
    if not query:
        return task_model_class.objects.all()
    
    search_query = SearchQuery(query, config='english')
    return task_model_class.objects.filter(
        search_vector=search_query
    ).annotate(
        rank=SearchRank('search_vector', search_query)
    ).order_by('-rank', '-created_at')


def update_all_search_vectors(batch_size=100):
    """
    Update search vectors for all existing tasks in batches
    Moved from management command for reusability
    """
    from .models import Task
    
    total_tasks = Task.objects.count()
    if total_tasks == 0:
        return {"updated": 0, "message": "No tasks found"}
    
    try:
        # Update search vectors in batches using raw SQL for efficiency
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE tasks_task 
                SET search_vector = to_tsvector('english', 
                    COALESCE(title, '') || ' ' || COALESCE(description, '')
                )
                WHERE search_vector IS NULL OR search_vector = ''
            """)
            
            updated_rows = cursor.rowcount
            
            return {
                "updated": updated_rows,
                "total": total_tasks, 
                "message": f"Successfully updated search vectors for {updated_rows} tasks"
            }
            
    except Exception as e:
        return {"error": str(e), "updated": 0}


def rebuild_search_index():
    """
    Force rebuild of entire search index
    """
    from .models import Task
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE tasks_task 
                SET search_vector = to_tsvector('english', 
                    COALESCE(title, '') || ' ' || COALESCE(description, '')
                )
            """)
            
            updated_rows = cursor.rowcount
            
            return {
                "success": True,
                "updated": updated_rows,
                "message": f"Rebuilt search index for {updated_rows} tasks"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}