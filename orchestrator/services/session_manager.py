def create_user_session(request, user_data):
    """Populates session dictionary with authenticated user details."""
    request.session['id'] = user_data['id']
    request.session['username'] = user_data['username']
    request.session['is_admin'] = bool(user_data['is_admin'])

def clear_session(request):
    """Completely flushes out the current session data."""
    request.session.flush()
