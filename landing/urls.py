from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^robots\.txt/$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]