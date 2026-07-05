import os
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from orchestrator import services
from django.views.decorators.csrf import csrf_exempt


@services.custom_login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

def homepage(request):
    if 'id' in request.session:
        return redirect('dashboard')
    return render(request, 'homepage.html')


def _authenticate_agent(request):
    token = request.headers.get('X-Agent-Token')
    if not token:
        return None
    return db_helper.get_user_by_agent_token(token)

@csrf_exempt
def agent_poll_jobs(request):
    user = _authenticate_agent(request)
    if not user:
        return JsonResponse({'error': 'Invalid or missing agent token'}, status=401)

    jobs = services.execution_service.get_pending_jobs_for_agent(user['id'])
    return JsonResponse({'jobs': jobs})

@csrf_exempt
def agent_report_status(request, job_id):
    user = _authenticate_agent(request)
    if not user:
        return JsonResponse({'error': 'Invalid or missing agent token'}, status=401)

    if request.method == 'POST':
        services.execution_service.report_job_status(
            job_id=job_id,
            status=request.POST.get('status'),
            log_output=request.POST.get('log_output'),
            error_message=request.POST.get('error_message')
        )
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'POST required'}, status=405)


# ---------------------------- START USER AUTH SERVICE --------------------------- 
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user_data = services.authenticate_credentials(username, password)
        
        if user_data:
            services.create_user_session(request, user_data)
            return JsonResponse({'success': True, 'redirect_url': reverse('dashboard')})
        
        return JsonResponse({
            'success': False, 
            'error_message': "Invalid username or password configuration."
        }, status=401)
        
    return redirect('homepage')


# ---------------------------- END USER AUTH SERVICE --------------------------- 

def logout_view(request):
    # Core logic delegated completely
    services.clear_session(request)
    return redirect('homepage')


# ---------------------------- START DASHBOARD SERVICE --------------------------- 

@services.custom_login_required
def dashboard(request):
    user = request.custom_user
    is_admin = bool(user['is_admin'])
    
    # 1. Fetch authorized folder lists
    folders, all_system_folders = services.dashboard_service.get_permitted_folders(user)

    # 2. Extract UI state routing parameters
    active_view = request.GET.get('view', 'home')
    selected_folder_id = request.GET.get('folder_id')

    if selected_folder_id:
        active_view = 'automations'

    context = {
        'folders': folders,
        'is_admin': is_admin,
        'active_view': active_view,
    }

    # 3. Admin user-management context is ALWAYS loaded for admins now,
    #    since the panel is a JS-toggled tab embedded in dashboard.html
    #    (not a separate server-rendered route). There is no follow-up
    #    request when the tab is clicked, so the data must be present
    #    on initial page load regardless of which tab starts active.
    if is_admin:
        search_query = request.GET.get('search', '')
        users_list, departments = services.dashboard_service.load_user_management(search_query)

        context.update({
            'users_list': users_list,
            'departments': departments,
            'all_system_folders': all_system_folders,
            'search_query': search_query,
        })

    # 4. Handle localized automation file parsing
    selected_folder = None
    automations = {}
    path_error = None

    if selected_folder_id:
        # Secure safety check inside the pre-filtered permitted collection
        allowed_folder = next(
            (f for f in folders if int(f['id']) == int(selected_folder_id)), 
            None
        )
        
        if allowed_folder:
            selected_folder = allowed_folder
            automations, path_error = services.dashboard_service.scan_automation_packages(
                folder_id=selected_folder['id'],
                physical_path=selected_folder['physical_path']
            )

    context.update({
        'selected_folder': selected_folder,
        'automations': automations,
        'path_error': path_error,
    })
    
    return render(request, 'dashboard.html', context)

# ---------------------------- END DASHBOARD SERVICE --------------------------- 


# ---------------------------- START ADMIN SERVICE --------------------------- 

@services.custom_login_required
def admin_save_user(request, user_id=None):
    # 1. Enforce access security via the service layer
    if not services.admin_service.check_admin_clearance(request.custom_user):
        messages.error(request, "Access Denied: Action Rejected.")
        return redirect('dashboard')

    # 2. Extract and process form mutations via services
    if request.method == 'POST':
        try:
            username = services.admin_service.save_user_profile_mutation(
                post_data=request.POST, 
                user_id=user_id
            )
            messages.success(request, f"Permissions map updated for '{username}'.")
        except Exception as e:
            messages.error(request, f"Database operational failure: {str(e)}")

    # Redirect back into the dashboard with the user-management tab
    # selected, instead of the old standalone admin page route.
    return redirect(f"{reverse('dashboard')}?view=user_management")

# ---------------------------- END ADMIN SERVICE --------------------------- 



# ---------------------------- START FOLDER SERVICE --------------------------- 

@services.custom_login_required
def create_folder(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        physical_path = request.POST.get('physical_path')
        
        # Delegate business logic completely
        success, message = services.folder_service.create_user_folder(
            user=request.custom_user, 
            name=name, 
            physical_path=physical_path
        )
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
            
    return redirect('dashboard')


@services.custom_login_required
def edit_folder(request, folder_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        physical_path = request.POST.get('physical_path')

        # Trigger update rules through service 
        success, message = services.folder_service.update_user_folder(
            user=request.custom_user,
            folder_id=folder_id,
            name=name,
            physical_path=physical_path
        )

        if success:
            messages.success(request, message)
            return redirect(f"{reverse('dashboard')}?folder_id={folder_id}")
        else:
            messages.error(request, message)
            
    return redirect('dashboard')


@services.custom_login_required
def select_version(request):
    if request.method != 'POST':
        messages.error(request, "Invalid method or insufficient permissions.")
        return redirect('dashboard')

    folder_id = request.POST.get('folder_id')
    package_name = request.POST.get('package_name')
    version = request.POST.get('version')

    # Trigger version mutation route inside service layer
    success, message = services.folder_service.deploy_package_version(
        user=request.custom_user,
        folder_id=folder_id,
        package_name=package_name,
        version=version
    )

    if success:
        messages.success(request, message)
        return redirect(f"{reverse('dashboard')}?folder_id={folder_id}")
    else:
        messages.error(request, message)
        return redirect('dashboard')
    

# ---------------------------- END FOLDER SERVICE ---------------------------