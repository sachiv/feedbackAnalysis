from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from rest_framework.authtoken import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^', include('landing.urls')),
    url(r'^login/', auth_views.login, name='login'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/profile/', include('b2b.urls')),
    url(r'^b2c/', include('b2c.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^staff/', include('staff.urls')),
    url(r'^adminactions/', include('adminactions.urls')),
]
