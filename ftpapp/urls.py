from django.urls import re_path
from . import views

app_name = 'ftpapp'

urlpatterns = [
    # re_path(r'connectftp/(?P<date>\d{4}-\d{2}-\d{2})$', views.connectftp, name = 'connectftp')
    re_path(r'connectftp/fetchdata$', views.connectftp, name = 'connectftp'),
]

