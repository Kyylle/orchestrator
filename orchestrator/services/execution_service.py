from . import db_helper

def queue_manual_run(user, folder_id):
    """User-triggered play button — creates a Pending job for their own agent."""
    folder = db_helper.get_folder_by_id(folder_id)
    if not folder or int(folder['user_id']) != int(user['id']):
        return False, "Cannot queue a run for a package you don't own."

    active_version = db_helper.get_active_versions_for_folder(folder_id)
    if not active_version:
        return False, "No active version set for this package."

    db_helper.create_execution_job(
        package_id=folder_id,
        package_name=folder['name'],
        version_number=active_version,
        target_user_id=user['id'],
        triggered_by_user_id=user['id'],
        trigger_type='Manual'
    )
    return True, f"Queued '{folder['name']}' for execution."


def get_pending_jobs_for_agent(user_id):
    """Called by the agent poll endpoint."""
    return db_helper.get_pending_jobs(target_user_id=user_id)


def report_job_status(job_id, status, log_output=None, error_message=None):
    """Called by the agent report endpoint."""
    db_helper.update_execution_job_status(job_id, status, log_output, error_message)