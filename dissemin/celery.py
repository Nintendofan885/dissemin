# This file has been copy-pasted from the docs of celery
# http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html



import os
import logging

from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dissemin.settings')

app = Celery('dissemin')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

logger = logging.getLogger('dissemin.' + __name__)

@app.task(bind=True)
def debug_task(self):
    logger.debug('Request: {0!r}'.format(self.request))
