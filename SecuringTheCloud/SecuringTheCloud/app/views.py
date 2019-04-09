"""
Definition of views.
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from app.models import ProxyUser, Group, User, Membership
from app.googledrive import GoogleDrive
from .forms import CreateGroupForm, AddUserForm
from Crypto.Random import get_random_bytes

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'app/signup.html'

def home(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'Securing the Cloud',
        }
    )

@login_required
def drive(request):
    """Drive login."""
    assert isinstance(request, HttpRequest)
    drive = GoogleDrive()
    file_list = drive.getFiles()
    return render(
        request,
        'app/drive.html',
        {
            'title':'Drive',
            'file_list': file_list,
            'folderId': '1a_ZOqi75h6nTvsUEPDi8NGUrb9Tk-dkh',
        }
    )

@login_required
def driveFolder(request, folder, groupId):
    """Drive login."""
    assert isinstance(request, HttpRequest)
    drive = GoogleDrive()
    file_list = drive.getFilesInFolder(folder)
    group = Group.objects.get(id=groupId)
    membersList =  []
    for m in Membership.objects.filter(group=group):
        membersList.append(m.user_id)
    return render(
        request,
        'app/drive.html',
        {
            'title':group.name,
            'file_list': file_list,
            'folderId': folder,
            'groupId': groupId,
            'membersList': membersList,
            'errorMessage': 'app/errors/403.html'
        }
    )

@login_required
def driveUpload(request, folder, groupId):
    assert isinstance(request, HttpRequest)
    gDrive = GoogleDrive()
    gDrive.uploadFile(folder, groupId)
    return driveFolder(request, folder, groupId)

@login_required
def driveDownload(request, id, title, folder, groupId):
    assert isinstance(request, HttpRequest)
    gDrive = GoogleDrive()
    gDrive.downloadFile(id, title, groupId)
    return driveFolder(request, folder, groupId)

@login_required
def createGroup(request, username):
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Group.objects.filter(name=name).exists():
                return render(
                    request,
                    'app/createGroup.html',
                    {
                        'title': username,
                        'form': CreateGroupForm(),
                        'error':'Group already exists'
                    }
                )
            else:
                user = User.objects.get_by_natural_key(username)
                gDrive = GoogleDrive()
                folderId = gDrive.createGroup(name)

                group = Group()
                group.name = name
                group.owner = user
                group.gdriveid = folderId
                group.key = get_random_bytes(16)
                group.save()

                membership = Membership()
                membership.group = group
                membership.user = user
                membership.save()
                return redirect('/userpage/'+username)
    else:
        return render(
            request,
            'app/createGroup.html',
            {
                'title': username,
                'form': CreateGroupForm()
            }
        )

@login_required
def userpage(request, username):
    assert isinstance(request, HttpRequest)
    proxyuser = ProxyUser.objects.get_by_natural_key(username)
    return render(
            request,
            'app/userpage.html',
            {
                'title': 'Manage groups',
                'proxyuser': proxyuser
            }
        )

@login_required
def manageUsers(request, groupId):
    assert isinstance(request, HttpRequest)
    group = Group.objects.get(id=groupId)
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if not User.objects.filter(username=name).exists():
                return render(
                    request,
                    'app/manageUsers.html',
                    {
                        'title': 'ManageUsers',
                        'form': AddUserForm(),
                        'error':'User doesn\'t exist',
                        'group': group
                    }
                )
            user = User.objects.get_by_natural_key(name)
            if Membership.objects.filter(user=user, group=group).exists():
                return render(
                    request,
                    'app/manageUsers.html',
                    {
                        'title': 'ManageUsers',
                        'form': AddUserForm(),
                        'error':'User is already a member',
                        'group': group
                    }
                )
            else:
                membership = Membership()
                membership.group = group
                membership.user = user
                membership.save()
                return render(
                    request,
                    'app/manageUsers.html',
                    {
                        'title': 'ManageUsers',
                        'form': AddUserForm(),
                        'group': group
                    }
                )
    else:
        return render(
                request,
                'app/manageUsers.html',
                {
                    'title': 'ManageUsers',
                    'form': AddUserForm(),
                    'group': group
                }
            )

@login_required
def removeUser(request, groupId, userId):
    group = Group.objects.get(id=groupId)
    user = User.objects.get(id=userId)

    if Membership.objects.filter(user=user, group=group).exists():
        Membership.objects.filter(user=user, group=group).delete()

    return redirect('/manageUsers/'+groupId)