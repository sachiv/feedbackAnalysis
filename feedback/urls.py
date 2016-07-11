from django.conf.urls import url
from . import api_views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^post/$', csrf_exempt(api_views.feedback)),
    url(r'^(?P<b_entity>[0-9]+)/$', api_views.FeedbackDetail.as_view(), name='apiStatsFeedbackDetail'),
]
