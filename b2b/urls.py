from django.conf.urls import url
from . import views
from . import api_views
from django.views.decorators.csrf import csrf_exempt
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^json/$', views.dashboard_json, name='dashboard_json'),
    url(r'^feedbacks/$', views.dashboard_feedbacks, name='dashboard_feedbacks'),
    url(r'^dashboard_feedbacks_glimpse/$', views.dashboard_feedbacks_glimpse, name='dashboard_feedbacks_glimpse'),
    url(r'^feedbacks/post/$', views.dashboard_feedbacks_post, name='dashboard_feedbacks_post'),
    url(r'^register/$', views.dashboard_register, name='dashboard_register'),
    url(r'^profile/$', views.dashboard_profile, name='dashboard_profile'),
    url(r'^profile/edit/$', views.dashboard_profile_edit, name='dashboard_profile_edit'),
    url(r'^dashboard_custom_questions_edit/$',
        views.dashboard_custom_questions_edit, name='dashboard_custom_questions_edit'),
    url(r'^bentity/$', views.dashboard_bentity, name='dashboard_bentity'),
    url(r'^bentity/edit/$', views.dashboard_bentity_edit, name='dashboard_bentity_edit'),
    url(r'^employees/$', views.dashboard_employees, name='dashboard_employees'),
    url(r'^employee/(?P<pk>\d+)/edit/$', views.dashboard_employee_edit, name='dashboard_employee_edit'),
    url(r'^employee/(?P<pk>\d+)/remove/$', views.dashboard_employee_remove, name='dashboard_employee_remove'),
    url(r'^employee/(?P<pk>\d+)/$', views.dashboard_employee, name='dashboard_employee'),
    url(r'^employee/json/(?P<pk>\d+)/$', views.dashboard_employee_json, name='dashboard_employee_json'),
    url(r'^customers/$', views.dashboard_customers, name='dashboard_customers'),
    url(r'^customer/(?P<pk>\d+)/$', views.dashboard_customer, name='dashboard_customer'),
    url(r'^nfa/$', views.dashboard_nfa, name='dashboard_nfa'),
    url(r'^dashboard/promosms/$', views.dashboard_promosms, name='dashboard_promosms'),
    url(r'^dashboard/promosms/customers/$', views.dashboard_promosms_customers, name='dashboard_promosms_customers'),
    url(r'^dashboard/promosms/history/$', views.dashboard_promosms_history, name='dashboard_promosms_history'),

    # QWNER LINKS
    url(r'^owner/$', views.dashboard_owner, name='dashboard_owner'),
    url(r'^owner/json/$', views.dashboard_owner_json, name='dashboard_owner_json'),

    url(r'^(?P<pk>\d+)/$', views.dashboard, name='dashboard_pk'),
    url(r'^(?P<pk>\d+)/json/$', views.dashboard_json, name='dashboard_json_pk'),

    # API
    url(r'^api/bentity/$', csrf_exempt(api_views.b_entity)),
    url(r'^api/bentities/$', api_views.BEntityList.as_view(), name='apiBEntityList'),
    url(r'^api/bentities/(?P<pk>[0-9]+)/$', api_views.BEntityDetail.as_view(), name='apiBEntityDetail'),
    url(r'^api/bentities/stats/(?P<b_entity>[0-9]+)/$', api_views.StatsBEntityDetail.as_view(), name='apiStatsBEntityDetail'),
    url(r'^api/employees/(?P<b_entity>[0-9]+)/$', api_views.EmployeeList.as_view(), name='apiEmployeeList'),
    url(r'^api/employee/(?P<pk>[0-9]+)/$', api_views.EmployeeDetail.as_view(), name='apiEmployeeDetail'),
]
