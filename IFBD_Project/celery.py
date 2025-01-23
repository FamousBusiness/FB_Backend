from __future__ import absolute_import, unicode_literals
import os
from celery.schedules import crontab
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IFBD_Project.settings')

app = Celery('IFBD_Project')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')
app.config_from_object('django.conf:settings', namespace='CELERY')



# Celery Beat Settings
app.conf.beat_schedule = {
    'Send_lead_generate_mail_in_particular_time_interval': {
        'task': 'Lead.task.beat_task_to_send_lead_mail_every_10_minute',
        'schedule': crontab(minute='*/4'),
        # 'args': ()
    },
    'transfer_fund_from_immature_to_mature': {
        'task': 'Ecommerce.tasks.transfer_funds_from_immature_to_mature',
        'schedule': crontab(hour=0, minute=0), 
    },
 }


app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
