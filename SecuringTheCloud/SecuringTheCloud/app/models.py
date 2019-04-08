"""
Definition of models.
"""

from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

class Poll(models.Model):
    """A poll object for use in the application views and repository."""
    text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def total_votes(self):
        """Calculates the total number of votes for this poll."""
        return self.choice_set.aggregate(Sum('votes'))['votes__sum']

    def __unicode__(self):
        """Returns a string representation of a poll."""
        return self.text

class Choice(models.Model):
    """A poll choice object for use in the application views and repository."""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def votes_percentage(self):
        """Calculates the percentage of votes for this choice."""
        total=self.poll.total_votes()
        return self.votes / float(total) * 100 if total > 0 else 0

    def __unicode__(self):
        """Returns a string representation of a choice."""
        return self.text

class Group(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    gdriveid = models.CharField(max_length=200)

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