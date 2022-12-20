from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .models import Notification
from .models import Customer
from .models import Message
from .models_datastruct import MessageStatus

from .serializers import NotificationSerializer
from .serializers import CustomerSerializer
from .serializers import MessageSerializer

from .validators import validate_notification_schedule
from .validators import validate_notification_update
from .validators import validate_customer_phone_number
from .validators import validate_customer_time_zone

from .tasks import process_notification

from .metrics import notifications_total_created
from .metrics import customers_total_created

from utils.logging import log


# noinspection PyUnresolvedReferences
class NotificationViewSet(ModelViewSet):
    stats_prefix = 'total_msgs'
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    http_method_names = ['get', 'post', 'list', 'put', 'delete', 'head']

    @action(methods=['GET'], detail=True)
    def messages(self, request, pk=None):
        instance = self.get_object()
        messages = instance.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def all_stats(self, request):
        stats = {self.stats_prefix: Message.objects.all().count()}
        for status_name in MessageStatus.as_names_list():
            stats[f'{self.stats_prefix}_with_status_{status_name}'] = Message.objects.filter(status=status_name).count()

        return Response(stats)

    @action(methods=['GET'], detail=True)
    def stats(self, request, pk=None):
        obj = self.get_object()
        stats = {self.stats_prefix: obj.messages.all().count()}
        for status_name in MessageStatus.as_names_list():
            stats[f'{self.stats_prefix}_with_status_{status_name}'] = obj.messages.filter(status=status_name).count()

        return Response(stats)

    @action(methods=['GET'], detail=True)
    def start(self, request, pk=None):
        instance = self.get_object()
        if instance and instance.pk:
            process_notification.delay(instance.pk)
            result = f'notification {instance.pk} set to processing'
            log(result)
            return Response({'result': result})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validate_notification_schedule(
            serializer.validated_data.get('start_at'),
            serializer.validated_data.get('stop_at'))

        result = super().create(request, *args, **kwargs)
        if result.status_code == 201:
            instance_id = result.data.get('id')
            log(f'notification {instance_id} successfully created')
            notifications_total_created.labels(tag=result.data.get('tag')).inc()
            process_notification.delay(instance_id)

        return result

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance_id = kwargs.get('pk', 0)

        validate_notification_schedule(
            serializer.validated_data.get('start_at'),
            serializer.validated_data.get('stop_at'))
        validate_notification_update(instance_id)

        result = super().update(request, *args, **kwargs)
        if result.status_code == 200:
            log(f'notification {instance_id} successfully updated')
            process_notification.delay(instance_id)

        return result


# noinspection PyUnresolvedReferences
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    http_method_names = ['get', 'post', 'list', 'put', 'delete', 'head']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validate_customer_phone_number(serializer.validated_data.get('phone'))
        validate_customer_time_zone(serializer.validated_data.get('time_zone'))

        result = super().create(request, *args, **kwargs)
        if result.status_code == 201:
            instance_id = result.data.get('id')
            log(f'customer {instance_id} successfully created')
            customers_total_created.labels(tag=result.data.get('tag')).inc()

        return result

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance_id = kwargs.get('pk', 0)

        validate_customer_phone_number(serializer.validated_data.get('phone'))
        validate_customer_time_zone(serializer.validated_data.get('time_zone'))

        result = super().update(request, *args, **kwargs)
        if result.status_code == 200:
            log(f'customer {instance_id} successfully updated')

        return result


# noinspection PyUnresolvedReferences
class MessageViewSet(ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


@require_http_methods(['GET'])
def health_check(request):
    return JsonResponse({'status': 'OK'})


def metrics_view(request):
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)
