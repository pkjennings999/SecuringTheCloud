"""
Definition of urls for SecuringTheCloud.
"""

from datetime import datetime
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from app.models import Group, ProxyUser, User

urlpatterns = [
    path('', include(('app.urls', "app"), "appurls")),
    path('contact', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('seed/', views.seed, name='seed'),
    path('login/', 
        LoginView.as_view
        (
            template_name='app/login.html', 
            authentication_form=forms.BootstrapAuthenticationForm,
            extra_context =
            {
                'title': 'Log in',
                'year': datetime.now().year,
            }
         ),
        name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('admin/', admin.site.urls),
    path('drive/', views.drive, name='drive'),
    path('drive/upload/', views.driveUpload, name='driveUpload'),
    path('drive/download/<id>/<title>/', views.driveDownload, name='driveDownload'),
    path('drive/<folder>/', views.driveFolder, name='driveFolder'),
    path('userpage/createGroup/<username>', views.createGroup, name='createGroup'),
    path('userpage/createGroup/', views.createGroup, name='createGroup'),
    #path('userpage/<username>',
    #    views.GroupsView.as_view(
    #        context_object_name='user',
    #        template_name='app/userpage.html',),
    #   name='userpage')
    path('userpage/<username>', views.userpage, name='userpage')
]
