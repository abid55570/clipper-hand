from celery import Celery

celery_app = Celery("clipper_worker")
celery_app.config_from_object("worker.celeryconfig")
celery_app.autodiscover_tasks([
    "worker.tasks.clip_tasks",
    "worker.tasks.caption_tasks",
    "worker.tasks.ai_tasks",
    "worker.tasks.export_tasks",
    "worker.tasks.cleanup_tasks",
])
