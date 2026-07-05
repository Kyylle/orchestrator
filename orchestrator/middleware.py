from datetime import datetime
from django.db import connection

class DatabaseInitializationMiddleware:
    _db_initialized = False

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not DatabaseInitializationMiddleware._db_initialized:
            self.initialize_database()
            DatabaseInitializationMiddleware._db_initialized = True
        return self.get_response(request)

    def initialize_database(self):
        with connection.cursor() as cursor:
            # Check for standard Django session support
            cursor.execute(
                "SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE LOWER(TABLE_NAME) = 'django_session'"
            )
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE django_session (
                        session_key nvarchar(40) NOT NULL PRIMARY KEY,
                        session_data nvarchar(max) NOT NULL,
                        expire_date datetime2 NOT NULL
                    )
                """)

            # Seed default users with manual increment IDs if empty
            cursor.execute("SELECT COUNT(*) FROM m_orchestrator_users")
            if cursor.fetchone()[0] == 0:
                # Manually define primary key sequence entries 
                cursor.execute("""
                    INSERT INTO m_orchestrator_users (id, username, is_active, is_admin, local_sync_path, password) 
                    VALUES (1, %s, 1, 1, %s, %s)""",
                    ["admin", "C:\\Automations\\Admin", "admin123"]
                )
                cursor.execute("""
                    INSERT INTO m_orchestrator_users (id, username, is_active, is_admin, local_sync_path, password) 
                    VALUES (2, %s, 1, 0, %s, %s)""",
                    ["user1", "C:\\Automations\\User1", "user123"]
                )