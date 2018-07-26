from django.urls import re_path
from . import views

app_name = 'redirectapp'

urlpatterns = [
    # re_path(r'connectftp/(?P<date>\d{4}-\d{2}-\d{2})$', views.connectftp, name = 'connectftp')
    re_path(r'clients$', views.clients, name = 'clients'),
    re_path(r'bills$', views.bills, name = 'bills'),
    re_path(r'prices$', views.prices, name = 'prices'),
]

