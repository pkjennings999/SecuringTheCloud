"""
Definition of views.
"""

import json
from os import path
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, reverse_lazy
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView
from app.models import ProxyUser, Group, User, Membership
from app.googledrive import GoogleDrive
from .forms import CreateGroupForm, AddUserForm
from django.http import HttpResponse
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'app/signup.html'

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def home(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'Securing the Cloud',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

def vote(request, poll_id):
    """Handles voting. Validates input and updates the repository."""
    poll = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'app/details.html', {
            'title': 'Poll',
            'year': datetime.now().year,
            'poll': poll,
            'error_message': "Please make a selection.",
    })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('app:results', args=(poll.id,)))

@login_required
def seed(request):
    """Seeds the database with sample polls."""
    samples_path = path.join(path.dirname(__file__), 'samples.json')
    with open(samples_path, 'r') as samples_file:
        samples_polls = json.load(samples_file)

    for sample_poll in samples_polls:
        poll = Poll()
        poll.text = sample_poll['text']
        poll.pub_date = timezone.now()
        poll.save()

        for sample_choice in sample_poll['choices']:
            choice = Choice()
            choice.poll = poll
            choice.text = sample_choice
            choice.votes = 0
            choice.save()

    return HttpResponseRedirect(reverse('app:home'))

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