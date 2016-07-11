from django.conf.urls import url
from . import api_views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^api/$', api_views.CustomerList.as_view(), name='apiCustomerList'),
    url(r'^api/(?P<pk>[0-9]+)/$', api_views.CustomerDetail.as_view(), name='apiCustomerDetail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
