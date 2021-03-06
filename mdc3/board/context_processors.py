from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db.models.signals import post_save
from django.db.models import Q,F

from mdc3.board.models import Thread, LastRead

def posting_users(request):
    return { 'posting_users': len(request.posting_users) }

def _thread_count_key(site):
    return "thread-count:%d"%site.id

def thread_count(request):
    key = _thread_count_key(Site.objects.get_current())

    count = cache.get(key, None)
    if count is None:
        count = Thread.objects.all().count()
        cache.set(key, count)
    
    return { 'thread_count': count }

def _invalidate_thread_count(sender, instance, signal, *args, **kwargs):
    cache.delete(_thread_count_key(Site.objects.get_current()))

post_save.connect(_invalidate_thread_count, sender=Thread)

