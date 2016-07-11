__author__ = 'mukhar ranjan'

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from sms.api_views import SendSms


urlpatterns = [
    #url(r'^api/sms/$', SendSms.as_view({'post': 'send_sms'}),
        #name='send_sms'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)