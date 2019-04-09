"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

#Authentication form which uses boostrap CSS.
class BootstrapAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

# Form for creating a group
class CreateGroupForm(forms.Form):
    name = forms.CharField(max_length=100, label='Name')

# Form for adding a user to a group
class AddUserForm(forms.Form):
    name = forms.CharField(max_length=100, label='Name')