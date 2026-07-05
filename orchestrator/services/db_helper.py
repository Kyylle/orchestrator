import datetime
from django.db import connection

def dict_fetch_all(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dict_fetch_one(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    if row:
        return dict(zip(columns, row))
    return None

# --- AUTHENTICATION & IDENTITY ENGINES ---

def authenticate_user(username, password):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.id, u.username, u.is_admin, u.local_sync_path, u.is_active,
                   p.department_id, p.can_access_other_depts
            FROM m_orchestrator_users u
            LEFT JOIN (
                SELECT DISTINCT user_id, department_id, can_access_other_depts 
                FROM r_orchestrator_user_permissions
            ) p ON u.id = p.user_id
            WHERE u.username = %s AND u.password = %s AND u.is_active = 1""", 
            [username, password]
        )
        return dict_fetch_one(cursor)

def get_user_by_id(user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.id, u.username, u.is_admin, u.local_sync_path, u.is_active,
                   p.department_id, p.can_access_other_depts
            FROM m_orchestrator_users u
            LEFT JOIN (
                SELECT DISTINCT user_id, department_id, can_access_other_depts 
                FROM r_orchestrator_user_permissions
            ) p ON u.id = p.user_id
            WHERE u.id = %s""", 
            [user_id]
        )
        return dict_fetch_one(cursor)

# --- REPLICA DEPARTMENTS & ACCESS OVERRIDES ---

def get_all_departments():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM m_departments")
        return dict_fetch_all(cursor)

def search_and_get_users(search_query=""):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.id, u.username, u.is_active, u.is_admin, u.local_sync_path, 
                   p.department_id, p.can_access_other_depts, d.name AS department_name
            FROM m_orchestrator_users u
            LEFT JOIN (
                SELECT DISTINCT user_id, department_id, can_access_other_depts 
                FROM r_orchestrator_user_permissions
            ) p ON u.id = p.user_id
            LEFT JOIN m_departments d ON p.department_id = d.id
            WHERE u.username LIKE %s""",
            [f"%{search_query}%"]
        )
        return dict_fetch_all(cursor)

def get_user_permitted_folders_list(user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT folder_id 
            FROM r_orchestrator_user_permissions 
            WHERE user_id = %s AND folder_id IS NOT NULL""",
            [user_id]
        )
        return [row[0] for row in cursor.fetchall()]

def admin_save_orchestrator_user_profile(user_id=None, username=None, password=None, is_admin=0, department_id=None, can_access_other_depts=0, allowed_folder_ids=None):
    if allowed_folder_ids is None:
        allowed_folder_ids = []
        
    with connection.cursor() as cursor:
        # Manage core credentials table mapping without ALTER/IDENTITY dependencies
        if user_id:
            if password and password.strip():
                cursor.execute("""
                    UPDATE m_orchestrator_users 
                    SET username = %s, password = %s, is_admin = %s 
                    WHERE id = %s""",
                    [username, password, is_admin, user_id]
                )
            else:
                cursor.execute("""
                    UPDATE m_orchestrator_users 
                    SET username = %s, is_admin = %s 
                    WHERE id = %s""",
                    [username, is_admin, user_id]
                )
            target_user_id = user_id
        else:
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM m_orchestrator_users")
            target_user_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO m_orchestrator_users (id, username, password, is_active, is_admin, created_date)
                VALUES (%s, %s, %s, 1, %s, GETDATE())""",
                [target_user_id, username, password, is_admin]
            )

        # Re-index individual access rule mappings inside our custom junction grid
        cursor.execute("DELETE FROM r_orchestrator_user_permissions WHERE user_id = %s", [target_user_id])

        if allowed_folder_ids:
            for f_id in allowed_folder_ids:
                if f_id:
                    cursor.execute("""
                        INSERT INTO r_orchestrator_user_permissions (user_id, department_id, can_access_other_depts, folder_id)
                        VALUES (%s, %s, %s, %s)""",
                        [target_user_id, department_id, can_access_other_depts, int(f_id)]
                    )
        else:
            cursor.execute("""
                INSERT INTO r_orchestrator_user_permissions (user_id, department_id, can_access_other_depts, folder_id)
                VALUES (%s, %s, %s, NULL)""",
                [target_user_id, department_id, can_access_other_depts]
            )

# --- RE-ENGINEERED AUTOMATION PACKAGE COMPONENT LOOKUPS ---

def get_folders_by_user(user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, package_name AS name, package_path AS physical_path, owner_user_id AS user_id 
            FROM m_automation_packages 
            WHERE owner_user_id = %s AND is_active = 1""", 
            [user_id]
        )
        return dict_fetch_all(cursor)

def get_all_folders_with_users():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ap.id, ap.package_name AS name, ap.package_path AS physical_path, 
                   ap.owner_user_id AS user_id, u.username
            FROM m_automation_packages ap
            JOIN m_orchestrator_users u ON ap.owner_user_id = u.id
            WHERE ap.is_active = 1"""
        )
        return dict_fetch_all(cursor)

def get_folder_by_id(folder_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, package_name AS name, package_path AS physical_path, owner_user_id AS user_id 
            FROM m_automation_packages 
            WHERE id = %s""", 
            [folder_id]
        )
        return dict_fetch_one(cursor)

def create_project_folder(user_id, name, physical_path):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM m_automation_packages")
        next_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO m_automation_packages (id, package_name, owner_user_id, package_path, is_published, is_active) 
            VALUES (%s, %s, %s, %s, 1, 1)""",
            [next_id, name, user_id, physical_path]
        )

def update_project_folder(folder_id, name, physical_path):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE m_automation_packages 
            SET package_name = %s, package_path = %s 
            WHERE id = %s""",
            [name, physical_path, folder_id]
        )

# --- PACKAGE HISTORICAL VERSION TRACKERS ---

def get_active_versions_for_folder(folder_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT version_number 
            FROM t_package_versions 
            WHERE package_id = %s AND is_current_version = 1""",
            [folder_id]
        )
        row = cursor.fetchone()
        return row[0] if row else None

def set_active_version(folder_id, package_name, version, user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE t_package_versions 
            SET is_current_version = 0 
            WHERE package_id = %s""", 
            [folder_id]
        )
        
        cursor.execute("""
            SELECT id 
            FROM t_package_versions 
            WHERE package_id = %s AND version_number = %s""",
            [folder_id, version]
        )
        row = cursor.fetchone()
        
        if row:
            cursor.execute("""
                UPDATE t_package_versions 
                SET is_current_version = 1 
                WHERE id = %s""",
                [row[0]]
            )
        else:
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM t_package_versions")
            next_version_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO t_package_versions (id, package_id, version_number, version_file_path, uploaded_by_user_id, is_current_version)
                VALUES (%s, %s, %s, %s, %s, 1)""",
                [next_version_id, folder_id, version, "Dynamic Direct Load", user_id]
            )
