from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from bbcode.fields import BBCodeTextField
import datetime


class PM(models.Model):
    subject = models.CharField(max_length=100, blank=False)
    body = BBCodeTextField(default='')
    sender = models.ForeignKey(User, related_name='sent_pms',
                               default="(no subject)")
    recipients = models.ManyToManyField(User,
            related_name='recieved_pms',
            through='Recipient')
    created_at = models.DateTimeField(default=datetime.datetime.now)
    parent = models.ForeignKey('self',null=True,
        related_name ='parent_of')
    root_parent = models.ForeignKey('self',null=True,
        related_name ='root_parent_of')
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.subject

    #there is clearly a one line query for this but this will
    #work for now
    def get_rec_str(self):
        rec_list = Recipient.objects.filter(message=self)
        rec_str =''
        for rec in rec_list:
            rec_str += rec.recipient.username + ' '
        return rec_str
    
    def get_reply_all(self, user):
        reply_all = self.sender.username
        recips = Recipient.objects.filter(message=self).exclude(
            recipient=user).exclude(
            recipient=self.sender).select_related(
                'recipient__username')
        for recip in recips:
            reply_all = reply_all + ' ' + recip.recipient.username
        return reply_all

    def check_privacy(self, user):
        if self.sender==user:
            return True
        if Recipient.objects.filter(message=self,recipient=user):
            return True
        return False

    
class Recipient(models.Model):
    recipient = models.ForeignKey(User)
    message = models.ForeignKey(PM)
    read = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.recipient.username


def clear_pm_count(sender, instance, signal, *args, **kwargs):
    cache_key = "pm-count:%d:%d"%(
        Site.objects.get_current().id,
        instance.recipient.id,
    )
    cache.delete(cache_key)
   
post_save.connect(clear_pm_count, sender=Recipient)
