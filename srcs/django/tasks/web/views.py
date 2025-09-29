from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..services import TaskFormAdapter, TaskQueryBuilder
from ..forms import TaskForm, TaskFilterForm


@login_required
def task_list(request):
    filter_form = TaskFilterForm(request.GET)
    filter_params = filter_form.get_filter_params() if filter_form.is_valid() else {}
    page = request.GET.get('page', 1)
    
    result = TaskFormAdapter.get_filtered_tasks_for_user(
        user=request.user,
        filter_params=filter_params,
        page=page,
        page_size=10
    )
    
    context = {
        'tasks': result['page_obj'],
        'filter_form': filter_form,
        'paginator': result['paginator'],
        'page_obj': result['page_obj']
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def dashboard(request):
    stats = TaskFormAdapter.get_dashboard_stats(request.user)
    
    recent_tasks_result = TaskFormAdapter.get_filtered_tasks_for_user(
        user=request.user,
        filter_params={'order_by': 'created_at', 'desc': True},
        page=1,
        page_size=5
    )
    
    context = {
        'stats': stats,
        'recent_tasks': recent_tasks_result['tasks']
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                task = TaskFormAdapter.create_task_from_form(form, request.user)
                messages.success(request, f'Task "{task.title}" created successfully!')
                return redirect('tasks_web:task_detail', task_id=task.id)
            except Exception as e:
                messages.error(request, f'Error creating task: {str(e)}')
    else:
        form = TaskForm()
    
    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': 'Create New Task',
        'action': 'Create'
    })


@login_required
def task_detail(request, task_id):
    try:
        result = TaskFormAdapter.get_task_detail_for_web(task_id, request.user)
        task = result['task']
    except Exception:
        messages.error(request, 'Task not found')
        return redirect('tasks_web:task_list')
    
    context = {
        'task': task,
        'assignments': result.get('assignments', []),
        'comments': result.get('comments', []),
        'history': result.get('history', [])
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_edit(request, task_id):
    try:
        task = TaskQueryBuilder.get_task_with_relations(task_id)
    except Exception:
        messages.error(request, 'Task not found')
        return redirect('tasks_web:task_list')
    
    # Check permissions - user must be creator or assigned to task
    if task.created_by != request.user and not task.assigned_to.filter(id=request.user.id).exists():
        messages.error(request, 'You do not have permission to edit this task')
        return redirect('tasks_web:task_detail', task_id=task.id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            try:
                updated_task = TaskFormAdapter.update_task_from_form(task, form, request.user)
                messages.success(request, f'Task "{updated_task.title}" updated successfully!')
                return redirect('tasks_web:task_detail', task_id=updated_task.id)
            except Exception as e:
                messages.error(request, f'Error updating task: {str(e)}')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {
        'form': form,
        'task': task,
        'title': 'Edit Task',
        'action': 'Update'
    })


@login_required
def my_tasks(request):
    filter_params = {'assigned_to_me': True}
    page = request.GET.get('page', 1)
    
    result = TaskFormAdapter.get_filtered_tasks_for_user(
        user=request.user,
        filter_params=filter_params,
        page=page,
        page_size=10
    )
    
    context = {
        'tasks': result['page_obj'],
        'title': 'My Tasks',
        'paginator': result['paginator'],
        'page_obj': result['page_obj']
    }
    return render(request, 'tasks/my_tasks.html', context)
