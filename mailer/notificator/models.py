import datetime
import pytz

from django.db import models

from .models_datastruct import MessageStatus
from utils.time import now
from utils.validation import parse_mobile_provider_prefix


# noinspection PyUnresolvedReferences,PyMethodMayBeStatic
class Notification(models.Model):
    start_at = models.DateTimeField(verbose_name='Дата и время запуска рассылки')
    stop_at = models.DateTimeField(verbose_name='Дата и время окончания рассылки')
    message = models.CharField(verbose_name='Текст сообщения', max_length=300)
    mobile_provider_prefix = models.CharField(verbose_name='Код мобильного оператора клиента (фильтр)', max_length=3)
    tag = models.CharField(verbose_name='Тег клиента (фильтр)', max_length=30)

    class Meta:
        db_table = 'notification'
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['start_at']

    def __str__(self):
        return f'id {self.pk}, фильтр {self.mobile_provider_prefix}/{self.tag}, начать {self.start_at}, ' \
               f'завершить {self.stop_at}'

    def datetime_to_python(self, datetime_model_field: models.DateTimeField) -> datetime.datetime:
        return models.DateTimeField().to_python(datetime_model_field).astimezone(pytz.UTC)

    def requires_processing(self) -> bool:
        _now = now()
        return self.datetime_to_python(self.start_at) < _now < self.datetime_to_python(
            self.stop_at) and not self.messages.all().count()

    def can_be_altered(self) -> bool:
        return not self.messages.all().count()


class Customer(models.Model):
    phone = models.CharField(verbose_name='Номер телефона', max_length=11)
    mobile_provider_prefix = models.CharField(verbose_name='Код мобильного оператора', max_length=3)
    tag = models.CharField(verbose_name='Тег', max_length=30)
    time_zone = models.CharField(verbose_name='Часовой пояс', max_length=32)

    class Meta:
        db_table = 'customer'
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['id']

    def __str__(self):
        return f'id {self.pk}: тел {self.phone}, тег {self.tag}, часовой пояс {self.time_zone}'

    def save(self, *args, **kwargs):
        parsed_prefix = parse_mobile_provider_prefix(str(self.phone))
        if parsed_prefix:
            self.mobile_provider_prefix = parsed_prefix

        super().save(*args, **kwargs)


class Message(models.Model):
    created_at = models.DateTimeField(verbose_name='Дата и время создания (отправки)', auto_now_add=True)
    status = models.CharField(verbose_name='Статус', choices=MessageStatus.as_model_choices(), max_length=100)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='messages',
                                     verbose_name='Рассылка')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='messages', verbose_name='Клиент')

    class Meta:
        db_table = 'message'
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['id']

    # noinspection PyUnresolvedReferences
    def __str__(self):
        return f'id {self.pk}, дата и время создания {self.created_at}, статус {self.status}, ' \
               f'id рассылки: {self.notification_id}, id клиента: {self.customer_id}, '
