import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alemethod.settings')

app = Celery('alemethod')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

#### **`alemethod/__init__.py`**
