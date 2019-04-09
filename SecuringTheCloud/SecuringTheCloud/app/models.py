"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User

# Group model
class Group(models.Model):
    # The owner will have extra permissions: managing users and deleting groups
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    # Id of the folder in which the group files are stored
    gdriveid = models.CharField(max_length=200)
    key = models.BinaryField()

    def __unicode__(self):
        return name

    # Returns all the users in the group
    def getUsers(self):
        users = Membership.objects.filter(group=self)
        userList = []
        for u in users:
            user = User.objects.get(id=u.user_id)
            if not user == self.owner: 
                userList.append(user)
        return userList

# Membership model. Maps users to groups
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


# Proxy user model. I wanted to add a getGroups method for users, 
# and the easiest way to do this is by using a proxy model. It inherits
# all the functionlity and data of the parent model
class ProxyUser(User):

    class Meta:
        proxy = True
        ordering = ('first_name', )

    # Returns all the groups that the user is in
    def getGroups(self):
        groups = Membership.objects.filter(user=self)
        groupList = []
        for g in groups:
            groupList.append(Group.objects.get(id=g.group_id))
        return groupList