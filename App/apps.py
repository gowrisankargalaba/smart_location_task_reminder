from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App'

    def ready(self):
        # Avoid running scheduler twice (Django reloader runs ready() twice in debug mode)
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return

        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from App.scheduler import send_task_reminders

            scheduler = BackgroundScheduler()
            scheduler.add_job(
                send_task_reminders,
                trigger='interval',
                seconds=60,           # checks every 60 seconds
                id='task_reminder',
                replace_existing=True,
                max_instances=1,
            )
            scheduler.start()
            logger.info("[Scheduler] ✅ Task reminder scheduler started — checking every 60 seconds.")
        except Exception as e:
            logger.error(f"[Scheduler] ❌ Failed to start scheduler: {e}")
