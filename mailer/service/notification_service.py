import datetime
import time
from abc import ABC, abstractmethod
from datetime import timedelta

import notificator.models
from notificator.models import Notification
from notificator.models import Customer
from notificator.models import Message
from notificator.models_datastruct import MessageStatus

from client.fbrq_client import FbrqClientInterface
from client.fbrq_client import FbrqClient
from client.fbrq_client_datastruct import NotificationMessage

from utils.logging import log
from utils.time import now


class NotificationServiceInterface(ABC):
    """
    Notification service interface
    """

    _fbrq_client: FbrqClientInterface

    def __init__(self):
        self._fbrq_client = FbrqClient()

    @abstractmethod
    def process_notifications(self) -> None:
        pass

    @abstractmethod
    def process_notification(self, notification_id: int) -> None:
        pass


# noinspection PyUnresolvedReferences,PyMethodMayBeStatic
class NotificationService(NotificationServiceInterface):
    """
    Notification service implementation
    """

    _notification_send_max_tries: int = 3

    def process_notifications(self) -> None:
        log(f'processing jobs (notifications) by scheduler')
        now = datetime.datetime.utcnow()
        jobs = Notification.objects. \
            filter(start_at__lte=now). \
            filter(stop_at__gt=now)

        job_count = len(jobs)
        log(f'total of {job_count} jobs are available for processing')
        if not job_count:
            return

        for job in jobs:
            self._process_notification(job)

    def process_notification(self, notification_id: int) -> None:
        try:
            instance = Notification.objects.get(pk=notification_id)
        except (notificator.models.Customer.DoesNotExist, Exception):
            log(f'job {notification_id} not found')
            return

        if instance:
            self._process_notification(instance)

    def _process_notification(self, notification: Notification) -> None:
        job_id = notification.pk
        log(f'processing job (notification) {job_id}')

        if not notification.requires_processing():
            log(f'job {job_id} does not need processing')
            return

        customers = Customer.objects. \
            filter(mobile_provider_prefix=notification.mobile_provider_prefix). \
            filter(tag=notification.tag)

        job_customer_count = len(customers)
        log(f'job {job_id} has total of {job_customer_count} customers to notify')

        if not job_customer_count:
            return

        job_processed_customer_count = 0
        for customer in customers:
            _now = now()
            if _now >= notification.datetime_to_python(notification.stop_at):
                log(f"job {job_id} has expired, total job's customers (messages) "
                    f"processed: {job_processed_customer_count}")
                return

            job_processed_customer_count += 1
            self._process_customer_notification(notification=notification, customer=customer)

        log(f'job {job_id} total customers (messages) processed: {job_processed_customer_count}')

    def _process_customer_notification(
            self,
            notification: Notification,
            customer: Customer) -> None:

        job_id = notification.pk
        msg = Message(status=MessageStatus.pending.name, notification=notification, customer=customer)
        msg.save()

        log(f'job {job_id}, customer {customer.pk}, processing message {msg.pk} ...')
        client_msg = NotificationMessage(id=msg.pk, phone=customer.phone, text=notification.message)

        for current_try_number in range(self._notification_send_max_tries):
            log(f'trying to send message {msg.pk} for a try # {current_try_number + 1}')
            status, _ = self._fbrq_client.send_notification(client_msg)
            if status == 200:
                msg.status = MessageStatus.sent.name
                msg.save()
                log(f'message {msg.pk} successfully sent on a try # {current_try_number + 1}')
                return

            time.sleep(1)

        msg.status = MessageStatus.failed.name
        msg.save()
        log(f'failed to send message {msg.pk} after {self._notification_send_max_tries} tries')
        return
