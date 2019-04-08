"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    gdriveid = models.CharField(max_length=200)
    key = models.BinaryField()

    def __unicode__(self):
        return name

    def getUsers(self):
        users = Membership.objects.filter(group=self)
        userList = []
        for u in users:
            user = User.objects.get(id=u.user_id)
            if not user == self.owner: 
                userList.append(user)
        return userList

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

class ProxyUser(User):

    class Meta:
        proxy = True
        ordering = ('first_name', )

    def getGroups(self):
        groups = Membership.objects.filter(user=self)
        groupList = []
        for g in groups:
            groupList.append(Group.objects.get(id=g.group_id))
        return groupList