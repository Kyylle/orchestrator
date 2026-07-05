from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('folder/create/', views.create_folder, name='create_folder'),
    # Change <int:folder_id> to <str:folder_id> to support UUIDs:
    path('folder/edit/<str:folder_id>/', views.edit_folder, name='edit_folder'),
    path('folder/version/select/', views.select_version, name='select_version'),
    
    # --- USER MANAGEMENT URLS ---
    path('admin/save-user/', views.admin_save_user, name='admin_save_user'),
    path('admin/save-user/<int:user_id>/', views.admin_save_user, name='admin_save_user'),
]