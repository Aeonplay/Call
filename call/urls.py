from django.urls import path
from . import views

app_name = 'call'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('call/<str:code>/', views.IndexView.as_view(), name='call'),
    path('call_line_process/', views.callLineProcess, name='call_line_process'),
    path('call/<str:code>/call_line_process/', views.callLineProcess, name='call_line_process'),
]
