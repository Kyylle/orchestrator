# services/folder_service.py
from . import db_helper

def create_user_folder(user, name, physical_path):
    """Validates parameters and provisions a new package directory for a regular user."""
    if bool(user['is_admin']):
        return False, "Global workspace configurations are modified only by local owners."
        
    if not name or not physical_path:
        return False, "Fields cannot be blank."
        
    db_helper.create_project_folder(user['id'], name, physical_path)
    return True, f"Registered Package environment '{name}'."


def update_user_folder(user, folder_id, name, physical_path):
    """Validates authorization rules and overrides folder directory configurations."""
    if bool(user['is_admin']):
        return False, "Global configurations cannot be edited in admin mode."

    if not name or not physical_path:
        return False, "Changes must contain values."

    folder = db_helper.get_folder_by_id(folder_id)
    # Check if folder exists and current user is the true record owner
    if not folder or int(folder['user_id']) != int(user['id']):
        return False, "Folder modification rejected."

    db_helper.update_project_folder(folder_id, name, physical_path)
    return True, "Configuration changes saved."


def deploy_package_version(user, folder_id, package_name, version):
    """Verifies ownership constraints and flags the target nupkg package version as active."""
    if bool(user['is_admin']) or not folder_id:
        return False, "Invalid method or insufficient permissions."

    folder = db_helper.get_folder_by_id(folder_id)
    if not folder or int(folder['user_id']) != int(user['id']):
        return False, "Change version command invalid."

    db_helper.set_active_version(folder_id, package_name, version, user['id'])
    return True, f"Deployed active package version {version} for '{package_name}'."
