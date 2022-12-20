from rest_framework import serializers

from .models import Notification
from .models import Customer
from .models import Message


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'start_at', 'stop_at', 'mobile_provider_prefix', 'tag', 'message']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'phone', 'mobile_provider_prefix', 'tag', 'time_zone']
        read_only_fields = ['mobile_provider_prefix', ]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'created_at', 'status', 'notification', 'customer']
