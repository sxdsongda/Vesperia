"""Vesperia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from MyAuth import views as auth_views
from assets import rest_urls as asset_api_urls


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', auth_views.index, name='index'),
    url(r'^login/$', auth_views.login_account, name='login'),
    url(r'^logout/$', auth_views.logout_account, name='logout'),
    url(r'^host/', include('hosts.urls', namespace='host')),
    url(r'^asset/', include('assets.urls', namespace='asset')),
    url(r'^monitor/', include('monitor.urls', namespace='monitor')),
    # url(r'^asset_api/', include(asset_api_urls)),
]
