from django.urls import path
from . import views

app_name = 'useapp'

urlpatterns = [
    path('', views.list_notifications, name='list'),
    path('lue/<int:notification_id>/', views.marquer_lue, name='marquer_lue'),
    path('suprimer/<int:notification_id>/', views.suprimer_notification, name='suprimer'),
]
