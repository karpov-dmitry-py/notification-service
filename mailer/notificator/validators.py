import re
from datetime import timedelta, datetime

import pytz
from rest_framework import serializers

from .models import Notification
from utils.time import now
from utils.validation import is_valid_phone_number


def validate_notification_schedule(start_at, stop_at: datetime) -> None:
    if start_at < now():
        raise serializers.ValidationError('start_at must be set to current/future date and time')

    if stop_at - start_at < timedelta(minutes=1):
        raise serializers.ValidationError('stop_at must be set to at least 1 minute after start_at')


# noinspection PyUnresolvedReferences
def validate_notification_update(notification_id: int) -> None:
    rows = Notification.objects.filter(pk=notification_id)
    if len(rows) and not rows[0].can_be_altered():
        raise serializers.ValidationError(f'notification {notification_id} has been/is being processed and '
                                          f'can not be altered')


def validate_customer_phone_number(phone: str) -> None:
    if not is_valid_phone_number(phone):
        raise serializers.ValidationError('phone number must be specified in the format of 79995556688 '
                                          '(11 digits starting with 7)')


def validate_customer_time_zone(tz: str) -> None:
    tzs = list(pytz.all_timezones)
    if tz not in tzs:
        raise serializers.ValidationError(f'time_zone must be a valid python time zone string, valid values: {tzs}')
