from django.urls import path, include
from django.conf import settings
from . import viewsets as api
from . import views as views

app_name = 'accounts'

api_urlpatterns = [
    path('v1/login', api.LoginView.as_view(), name="api_v1_login"),
    path('v1/logout', api.LogoutView.as_view(), name="api_v1_logout"),
    path('v1/profile', api.ProfileAPIView.as_view(), name="api_v1_agent_profile"),
    path('v1/forgot_password', api.frogot_password, name="api_v1_forgot_password"),
    path('v1/verify_otp', api.verify_otp, name="api_v1_verify_otp"),
    path('v1/change_password', api.change_password, name="api_v1_change_password"),
    path('v1/change_old_password', api.change_old_password, name="api_v1_change_old_password"),
]

urlpatterns = [path('api/', include(api_urlpatterns))]

# views url
urlpatterns += [
    path("login/", views.login_request, name="main_login"),
    path("logout/", views.logout_request, name="main_logout"),
    path("forgot_password/", views.forgot_password, name="main_forgot_password"),
    path("forgot_password/otp_verify/", views.forgot_password_otp_verify,
         name="main_forgot_password_otp_verify"),
    path("new_password/<email_id>", views.new_password, name="main_new_password"),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_base_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path("verify_otp_with_email/", views.verify_otp_with_email, name="verify_otp_with_email"),
]