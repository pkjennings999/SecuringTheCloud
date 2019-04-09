"""
Definition of urls for SecuringTheCloud.
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views

#Routing settings for the project. At a most basic level it maps a url path to a view
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', 
        LoginView.as_view
        (
            template_name='app/login.html', 
            authentication_form=forms.BootstrapAuthenticationForm,
            extra_context =
            {
                'title': 'Log in',
            }
         ),
        name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('admin/', admin.site.urls),
    path('drive/', views.drive, name='drive'),
    path('drive/upload/<folder>/<groupId>', views.driveUpload, name='driveUpload'),
    path('drive/download/<id>/<title>/<folder>/<groupId>', views.driveDownload, name='driveDownload'),
    path('drive/<folder>/<groupId>', views.driveFolder, name='driveFolder'),
    path('drive/<folder>/', views.driveFolder, name='driveFolder'),
    path('userpage/createGroup/<username>', views.createGroup, name='createGroup'),
    path('userpage/createGroup/', views.createGroup, name='createGroup'),
    path('userpage/<username>', views.userpage, name='userpage'),
    path('manageUsers/<groupId>', views.manageUsers, name='manageUsers'),
    path('manageUsers/<groupId>/<userId>', views.removeUser, name='removeUser'),
    path('drive/deleteFile/<fileId>/<folder>/<groupId>/', views.driveDelete, name='deleteFile'),
    path('userpage/deleteGroup/<groupId>', views.deleteGroup, name='deleteGroup')
]
