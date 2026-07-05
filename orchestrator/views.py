import os
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from orchestrator import services

@services.custom_login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

def homepage(request):
    if 'id' in request.session:
        return redirect('dashboard')
    return render(request, 'homepage.html')

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

    # 3. Query User Management configuration sub-context (Admins Only)
    if active_view == 'user_management' and is_admin:
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
def admin_user_management(request):
    # 1. Enforce access security via the service layer
    if not services.admin_service.check_admin_clearance(request.custom_user):
        messages.error(request, "Access Denied: Administrative Clearance Required.")
        return redirect('dashboard')

    # 2. Extract UI state queries
    search_query = request.GET.get('search', '')

    # 3. Retrieve system records from service package
    admin_data = services.admin_service.get_user_management_context(search_query)

    # 4. Synthesize final display context
    context = {
        'search_query': search_query,
        'is_admin': True,
        **admin_data  # Unpacks users_list, departments, folders, and all_system_folders safely
    }
    
    return render(request, 'adminpage/admin_user_management.html', context)

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

    return redirect('admin_user_management')

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