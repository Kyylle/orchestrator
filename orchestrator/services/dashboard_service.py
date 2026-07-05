# services/dashboard_service.py
import os
import re
from . import db_helper

def get_permitted_folders(user):
    """Filters and sorts system folders based on user privileges."""
    is_admin = bool(user['is_admin'])
    all_system_folders = db_helper.get_all_folders_with_users()
    
    if is_admin:
        folders = all_system_folders
    else:
        user_id = user['id']
        user_dept_id = user.get('department_id')
        can_cross_access = bool(user.get('can_access_other_depts'))
        permitted_folder_ids = db_helper.get_user_permitted_folders_list(user_id)
        
        folders = []
        for folder in all_system_folders:
            is_owner = (int(folder['user_id']) == int(user_id))
            is_explicitly_permitted = (folder['id'] in permitted_folder_ids)
            
            owner_profile = db_helper.get_user_by_id(folder['user_id'])
            owner_dept = owner_profile.get('department_id') if owner_profile else None
            is_same_dept = (user_dept_id is not None and owner_dept == user_dept_id)

            if is_owner or is_explicitly_permitted or is_same_dept or can_cross_access:
                folders.append(folder)

    # Resolve department display names
    departments = db_helper.get_all_departments()
    dept_map = {d['id']: d['name'] for d in departments}

    for folder in folders:
        owner_profile = db_helper.get_user_by_id(folder['user_id'])
        dept_id = owner_profile.get('department_id') if owner_profile else None
        folder['department_name'] = dept_map.get(dept_id, 'Unassigned')

    folders.sort(key=lambda x: x.get('department_name', 'Unassigned'))
    return folders, all_system_folders


def load_user_management(search_query):
    """Fetches user information and associated folder permissions for admins."""
    users_list = db_helper.search_and_get_users(search_query)
    departments = db_helper.get_all_departments()
    
    for u in users_list:
        u['permitted_folders'] = db_helper.get_user_permitted_folders_list(u['id'])
        
    return users_list, departments


def scan_automation_packages(folder_id, physical_path):
    """Scans local operating system directories for nuget deployment packages."""
    automations = {}
    path_error = None

    if not os.path.exists(physical_path) or not os.path.isdir(physical_path):
        return automations, f"Directory not accessible or path invalid: '{physical_path}'"

    try:
        files = os.listdir(physical_path)
        pattern = re.compile(r"^(.+?)\.((?:\d+\.)*\d+.*?)\.nupkg$", re.IGNORECASE)
        
        raw_automations = {}
        for f in files:
            match = pattern.match(f)
            if match:
                package_name, version = match.groups()
                if package_name not in raw_automations:
                    raw_automations[package_name] = []
                raw_automations[package_name].append(version)
        
        active_version = db_helper.get_active_versions_for_folder(folder_id)
        
        for pkg_name, versions in raw_automations.items():
            sorted_versions = sorted(versions, reverse=True)
            active = active_version if (active_version in sorted_versions) else (sorted_versions[0] if sorted_versions else "N/A")
            
            automations[pkg_name] = {
                'versions': sorted_versions,
                'active': active
            }
    except Exception as e:
        path_error = f"Failed to list directory contents: {str(e)}"

    return automations, path_error
