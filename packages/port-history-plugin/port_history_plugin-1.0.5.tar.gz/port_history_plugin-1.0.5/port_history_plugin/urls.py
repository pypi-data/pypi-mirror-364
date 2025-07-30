from django.urls import path

from port_history_plugin import views

app_name = "port_history_plugin"

urlpatterns = [
    path('history/', views.PortHistoryView.as_view(), name='history'),
]