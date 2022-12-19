from __future__ import absolute_import, unicode_literals

from mailer.celery import app

from service.notification_service import NotificationService


@app.task()
def process_notifications():
    return NotificationService().process_notifications()


@app.task
def process_notification(notification_id):
    return NotificationService().process_notification(notification_id)
