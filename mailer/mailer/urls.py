from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from notificator import views

router = routers.DefaultRouter()
router.register(r'notification', views.NotificationViewSet)
router.register(r'customer', views.CustomerViewSet)
router.register(r'message', views.MessageViewSet)  # todo - remove

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
]
