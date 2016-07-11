from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.login_page, name='staff_login_page'),
    url(r'^dashboard/$', views.dashboard, name='staff_dashboard'),
    url(r'^dashboard/recharge/$', views.dashboard_recharge, name='staff_dashboard_recharge'),
    url(r'^dashboard/market/$', views.dashboard_market, name='staff_dashboard_market'),
    url(r'^dashboard/promosms/$', views.dashboard_promosms, name='staff_dashboard_promosms'),
    url(r'^dashboard/market/buy/(?P<pk>\d+)/$', views.dashboard_buy, name='staff_dashboard_buy'),
    url(r'^dashboard/reports/$', views.dashboard_reports, name='staff_dashboard_reports'),
    url(r'^dashboard/account/activation$', views.dashboard_account_activation,
        name='staff_dashboard_account_activation'),
    url(r'^dashboard/import/$', views.dashboard_import, name='staff_dashboard_import'),
    url(r'^dashboard/customers/b2c/$', views.dashboard_customers_b2c, name='staff_dashboard_customers_b2c'),
    url(r'^dashboard/customers/b2b/$', views.dashboard_customers_b2b, name='staff_dashboard_customers_b2b'),
    url(r'^dashboard/cache/$', views.dashboard_cache, name='staff_dashboard_cache'),
]
