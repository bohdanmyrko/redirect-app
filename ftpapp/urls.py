from django.urls import re_path
from . import views

app_name = 'ftpapp'

urlpatterns = [
    re_path(r'connectftp/fetchdata$', views.StatusesView.as_view(), name='connectftp'),
    re_path(r'byname$', views.PricesView.as_view(), name='byname'),
    re_path(r'statuses/withname$', views.StatusWthFilenameView.as_view(), name='withnames'),
]
