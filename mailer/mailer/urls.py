from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers

from notificator import views
from .schema import schema_view

router = routers.DefaultRouter()
router.register(r'notification', views.NotificationViewSet)
router.register(r'customer', views.CustomerViewSet)
router.register(r'message', views.MessageViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health_check/', views.health_check),
    path('api/v1/', include(router.urls)),
    path("metrics/", views.metrics_view),
    re_path(r'^docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
