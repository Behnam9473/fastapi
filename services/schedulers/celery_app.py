from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    'fekrooneh',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    include=['services.schedulers.tasks']  # Update the include path
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'archive-visits-daily': {
        'task': 'services.schedulers.tasks.archive_visit_data',  # Update task path
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}