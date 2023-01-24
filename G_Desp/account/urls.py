from django.urls import include, path

from . import views
from django.contrib.auth import views as auth_views

app_name = 'account'
urlpatterns = [
	path('sign_in', auth_views.LoginView.as_view(template_name='account/login.html'), name='sign_in'),
	path('sign_up', views.sign_up, name='sign_up'),
	path('sign_out', views.sign_out, name='sign_out'),
	path('user_details', views.user_details, name='user_details'),
    path('request_reset_password', views.request_reset_password, name='request_reset_password'),
    path('reset_password/<key>', views.reset_password, name='reset_password'),
	path('*', include('django.contrib.auth.urls')),
]
