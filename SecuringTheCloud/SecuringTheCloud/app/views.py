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

# Sign up form for the sign up page
class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'app/signup.html'

# Returns the 'about' page, which is the home page for the app
def home(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'Securing the Cloud',
        }
    )

# Gets the file list from the default folder in drive and displays it
# Prompts the user to log in if they haven't
@login_required
def drive(request):
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

# Gets the file list from a specified folder in the drive and displays it
# Prompts the user to log in if they haven't
@login_required
def driveFolder(request, folder, groupId):
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

# Uploads a file to the specified folder in the drive
# Prompts the user to log in if they haven't
@login_required
def driveUpload(request, folder, groupId):
    assert isinstance(request, HttpRequest)
    gDrive = GoogleDrive()
    gDrive.uploadFile(folder, groupId)
    return driveFolder(request, folder, groupId)

# Downloads a specified file from a specified folder in the drive
# Prompts the user to log in if they haven't
@login_required
def driveDownload(request, id, title, folder, groupId):
    assert isinstance(request, HttpRequest)
    gDrive = GoogleDrive()
    gDrive.downloadFile(id, title, groupId)
    return driveFolder(request, folder, groupId)

# Deletes a specified file from a specified folder in the drive
# Prompts the user to log in if they haven't
@login_required
def driveDelete(request, fileId, folder, groupId):
    assert isinstance(request, HttpRequest)
    gDrive = GoogleDrive()
    gDrive.deleteFile(fileId)
    return driveFolder(request, folder, groupId)

# Creates a group, adding the user who created the group as the owner
# Prompts the user to log in if they haven't
@login_required
def createGroup(request, username):
    assert isinstance(request, HttpRequest)
    # If the method is a POST request, check if it is a valid Create Group form
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            # If the group already exists, do nothing
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
            # If the group does not exists, make a new group
            else:
                user = User.objects.get_by_natural_key(username)
                gDrive = GoogleDrive()
                # Create a folder in the drive and get its id
                folderId = gDrive.createGroup(name)

                # Create a group in the db, setting the owner to be the user who created the group,
                # and the gdriveid to be the id of the newly created folder
                group = Group()
                group.name = name
                group.owner = user
                group.gdriveid = folderId
                # Create a random 16 byte key that will be used for encryption/decryption
                group.key = get_random_bytes(16)
                group.save()

                # Create a membership relationship between the new group and the user who created it
                membership = Membership()
                membership.group = group
                membership.user = user
                membership.save()

                # Redirect back to the user page
                return redirect('/userpage/'+username)
    else:
        # If there was no POST request, just render the userpage as normal
        return render(
            request,
            'app/createGroup.html',
            {
                'title': username,
                'form': CreateGroupForm()
            }
        )


# Deletes a group from the drive
# Prompts the user to log in if they haven't
@login_required
def deleteGroup(request, groupId):
    gdriveId = Group.objects.get(id=groupId).gdriveid
    gDrive = GoogleDrive()
    gDrive.deleteFile(gdriveId)
    Group.objects.filter(id=groupId).delete()
    return redirect('userpage', username=request.user)

# Render the userpage
# Prompts the user to log in if they haven't
@login_required
def userpage(request, username):
    assert isinstance(request, HttpRequest)
    # Need to cast the user to a ProxyUser to gain access to the method for finding which groups the user is a member of
    proxyuser = ProxyUser.objects.get_by_natural_key(username)
    return render(
            request,
            'app/userpage.html',
            {
                'title': 'Manage groups',
                'proxyuser': proxyuser
            }
        )

# Renders the manage users page, and performs the necessary actions if the form is submitted
# Prompts the user to log in if they haven't
@login_required
def manageUsers(request, groupId):
    assert isinstance(request, HttpRequest)
    group = Group.objects.get(id=groupId)
    # If the method is a POST request, check if it is a valid Add User form
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            # If the user doesn't exist, render an informative message
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
            # If the user is already a member of the group, render an informative message
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
                # Otherwise, create a membership realtionship between the user and the group
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
        # If the request is not a POST request, renser the page as normal
        return render(
                request,
                'app/manageUsers.html',
                {
                    'title': 'ManageUsers',
                    'form': AddUserForm(),
                    'group': group
                }
            )

# Delete the relationship between the user and the group if they are a member of that group
# Prompts the user to log in if they haven't
@login_required
def removeUser(request, groupId, userId):
    group = Group.objects.get(id=groupId)
    user = User.objects.get(id=userId)

    if Membership.objects.filter(user=user, group=group).exists():
        Membership.objects.filter(user=user, group=group).delete()

    return redirect('/manageUsers/'+groupId)