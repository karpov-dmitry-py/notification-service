from django.contrib import admin

from .models import Notification
from .models import Customer
from .models import Message

admin.site.register(Notification)
admin.site.register(Customer)
admin.site.register(Message)
