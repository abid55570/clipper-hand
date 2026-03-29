import os

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "UTC"
enable_utc = True

# Task execution settings
task_acks_late = True
task_reject_on_worker_lost = True
worker_prefetch_multiplier = 1

# Time limits
task_soft_time_limit = 3600  # 1 hour soft limit
task_time_limit = 4200       # 1h10m hard limit

# Task routing
task_routes = {
    "worker.tasks.clip_tasks.*": {"queue": "video_processing"},
    "worker.tasks.export_tasks.*": {"queue": "video_processing"},
    "worker.tasks.caption_tasks.*": {"queue": "transcription"},
    "worker.tasks.ai_tasks.*": {"queue": "ai_analysis"},
    "worker.tasks.cleanup_tasks.*": {"queue": "maintenance"},
}

# Beat schedule for periodic tasks
beat_schedule = {
    "cleanup-temp-files": {
        "task": "worker.tasks.cleanup_tasks.cleanup_temp_files",
        "schedule": 86400.0,  # Daily
    },
}

# Result expiry
result_expires = 3600  # 1 hour
