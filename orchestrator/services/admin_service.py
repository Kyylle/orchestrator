# services/admin_service.py
from . import db_helper

def check_admin_clearance(user):
    """Verifies if the current user possesses administrative permissions."""
    return bool(user and user.get('is_admin'))


def get_user_management_context(search_query):
    """Fetches, maps, and groups system parameters required for the user configuration panel."""
    users_list = db_helper.search_and_get_users(search_query)
    departments = db_helper.get_all_departments()
    all_system_folders = db_helper.get_all_folders_with_users()

    for u in users_list:
        u['permitted_folders'] = db_helper.get_user_permitted_folders_list(u['id'])

    return {
        'users_list': users_list,
        'departments': departments,
        'all_system_folders': all_system_folders,
        'folders': all_system_folders, 
    }


def save_user_profile_mutation(post_data, user_id=None):
    """Parses incoming HTTP POST form parameters and commits changes to the database."""
    username = post_data.get('username')
    password = post_data.get('password')
    dept_id = post_data.get('department_id')
    
    # Parse checkboxes ('on' -> 1, otherwise 0)
    can_access_other_depts = 1 if post_data.get('can_access_other_depts') == 'on' else 0
    is_admin_flag = 1 if post_data.get('is_admin') == 'on' else 0
    
    # Extract multi-select folder array
    selected_folders = post_data.getlist('accessible_folders')

    # Sanitize department foreign key
    dept_id = int(dept_id) if dept_id and dept_id.isdigit() else None

    # Save to database via your moved helper
    db_helper.admin_save_orchestrator_user_profile(
        user_id=user_id,
        username=username,
        password=password,
        is_admin=is_admin_flag,
        department_id=dept_id,
        can_access_other_depts=can_access_other_depts,
        allowed_folder_ids=selected_folders
    )
    
    return username
