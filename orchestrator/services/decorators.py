from django.shortcuts import redirect
from django.contrib import messages
from . import db_helper  # Relative import from the same folder

def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'id' not in request.session:
            messages.warning(request, "Log in to access the control panel.")
            return redirect('homepage')
        
        # Use your moved db_helper
        request.custom_user = db_helper.get_user_by_id(request.session['id'])
        if not request.custom_user:
            return redirect('logout')
            
        return view_func(request, *args, **kwargs)
    return wrapper
