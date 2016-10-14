from django.conf.urls import url, include
from . import views, rest_urls

urlpatterns = [
    url(r'^$', views.index_v2, name='index'),
    url(r'^(?P<asset_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^report/$', views.report, name='report'),
    url(r'^event/$', views.event_log, name='event'),
    url(r'^software/$', views.software, name='software'),
    url(r'^storage/$', views.storage, name='storage'),
    url(r'^server/$', views.server, name='server'),
    url(r'^idc_contract_tags/$', views.idc_contract_tags, name='idc_contract_tags'),
    url(r'^asset_approval/$', views.asset_approval, name='asset_approval'),
    url(r'^virtual_machine/$', views.virtual_machine, name='virtual_machine'),
    url(r'^network_device/$', views.network_device, name='network_device'),
    url(r'^api/', include(rest_urls), name='api'),
    url(r'^get_detail/', views.get_asset_detail, name='get_asset_detail'),
    url(r'^ajax_get_asset_list/', views.ajax_get_asset_list, name='ajax_get_asset_list'),
    url(r'^ajax_get_asset_approval_list/', views.ajax_get_asset_approval_list, name='ajax_get_asset_approval_list'),
]

