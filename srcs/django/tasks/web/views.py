"""
Basic web views for task management using Django templates
Required by the technical test to demonstrate frontend functionality
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import Task, Tag, Team
from ..forms import TaskForm, TaskFilterForm


@login_required
def task_list(request):
    """Display list of tasks with filtering and pagination"""
    tasks = Task.objects.filter(is_archived=False).select_related('created_by', 'team')
    
    # Apply filters
    filter_form = TaskFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data['status']:
            tasks = tasks.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data['priority']:
            tasks = tasks.filter(priority=filter_form.cleaned_data['priority'])
        if filter_form.cleaned_data['assigned_to_me']:
            tasks = tasks.filter(assigned_to=request.user)
        if filter_form.cleaned_data['search']:
            search = filter_form.cleaned_data['search']
            tasks = tasks.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
    
    # Pagination
    paginator = Paginator(tasks, 10)  # 10 tasks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_tasks': tasks.count(),
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_detail(request, task_id):
    """Display task details"""
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all().select_related('author')
    history = task.history.all().select_related('user')[:10]  # Last 10 history entries
    
    context = {
        'task': task,
        'comments': comments,
        'history': history,
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_create(request):
    """Create a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            form.save_m2m()  # Save many-to-many relationships
            
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm()
    
    context = {
        'form': form,
        'title': 'Create New Task',
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_edit(request, task_id):
    """Edit an existing task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check permissions (only creator or assigned users can edit)
    if task.created_by != request.user and request.user not in task.assigned_to.all():
        messages.error(request, 'You do not have permission to edit this task.')
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'title': f'Edit Task: {task.title}',
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def dashboard(request):
    """Simple dashboard with task statistics"""
    user_tasks = Task.objects.filter(assigned_to=request.user, is_archived=False)
    
    stats = {
        'total_tasks': user_tasks.count(),
        'todo': user_tasks.filter(status='todo').count(),
        'in_progress': user_tasks.filter(status='in_progress').count(),
        'review': user_tasks.filter(status='review').count(),
        'done': user_tasks.filter(status='done').count(),
        'overdue': user_tasks.filter(is_overdue=True).count(),
    }
    
    # Recent tasks
    recent_tasks = user_tasks.order_by('-updated_at')[:5]
    
    context = {
        'stats': stats,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'tasks/dashboard.html', context)
