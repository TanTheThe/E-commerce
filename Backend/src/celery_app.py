from celery import Celery
from kombu import Queue
from celery.schedules import crontab

celery_app = Celery('ecommerce_tasks')

celery_app.config_from_object({
    'broker_url': 'redis://localhost:6379/0',
    'result_backend': 'redis://localhost:6379/1',
    'timezone': 'Asia/Ho_Chi_Minh',
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'task_track_started': True,
    'task_time_limit': 30 * 60,
    'beat_schedule': {
        'cleanup-expired-offers-daily': {
            'task': 'cleanup_expired_offers',
            'schedule': crontab(hour=2, minute=0),  # 02:00 AM mỗi ngày
        },
    },
})



