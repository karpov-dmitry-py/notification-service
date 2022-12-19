from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .models import Customer
from .models import Message

from .serializers import NotificationSerializer
from .serializers import CustomerSerializer
from .serializers import MessageSerializer

from .models_datastruct import MessageStatus

from .tasks import process_notification


# noinspection PyUnresolvedReferences
class NotificationViewSet(ModelViewSet):
    stats_prefix = 'total_msgs'
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

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

    @action(methods=['POST'], detail=True)
    def start(self, request, pk=None):
        obj = self.get_object()
        instance = self.get_object()
        if instance and instance.pk:
            process_notification.delay(instance.pk)
            return Response({'result': 'pending for processing'})

    def create(self, request, *args, **kwargs):
        print('creating notification')
        result = super().create(request, *args, **kwargs)

        for attr in dir(result):
            print(attr)

        for attr in dir(self.get_object()):
            print(attr)

        return result

    def update(self, request, *args, **kwargs):
        # todo - start_at/stop_at validation
        result = super().update(request, *args, **kwargs)
        instance = self.get_object()
        if instance and instance.pk:
            process_notification.delay(instance.pk)

        return result


# noinspection PyUnresolvedReferences
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    # todo - phone number validation, time zone validation, parse phone code from phone


# noinspection PyUnresolvedReferences
# class MessageViewSet(ReadOnlyModelViewSet): # todo
class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
