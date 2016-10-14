from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^multi_cmd/$', views.multi_cmd, name='multi_cmd'),
    url(r'^multi_file_transfer/$', views.multi_file_transfer, name='multi_file_transfer'),
    url(r'^mission_plan/$', views.mission_plan, name='mission_plan'),
    url(r'^audit/$', views.audit, name='audit'),
    url(r'^submit_task/$', views.submit_task, name='submit_task'),
    url(r'^get_task_result/$', views.get_task_result, name='get_task_result'),
    url(r'^file_upload/$', views.file_upload, name='file_upload'),

]

