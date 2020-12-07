from django.urls import path, include
from django.conf import settings
from . import viewsets as api
from . import views as views

app_name = 'leaves'

api_urlpatterns = [
    path('v1/my_leaves', api.MyLeavesList.as_view()), 
    path('v1/my_leaves/<int:pk>', api.LeaveDetailView.as_view()), 
    path('v1/global_leave_types', api.GlobalLeavesTypesList.as_view()), 
    path('v1/unauthorized_leave', api.MyUnauthorizedLeaveList.as_view()),
    path('v1/leave_overview', api.my_leave_overview),
    path('v1/financial_years', api.financial_years),
    path('v1/applied_leaves_queues', api.AppliedQueueLeaveListView.as_view()),
    path('v1/applied_leaves_queues/<int:pk>/', api.LeaveQueueDetailView.as_view()),
    path('v1/applied_leaves_queues/<int:pk>/approve', api.LeaveQueueApproveView.as_view()),
    path('v1/employee_leave_apply', api.apply_leave),
    path('v1/leave_status_list', api.leave_status_list),
]
urlpatterns = [
    path('all', views.leaves_all_list, name="leaves_all_list"), 
    path('<int:leave_id>/view', views.leave_view, name="leave_view"), 
    path('<int:leave_id>/approve', views.leave_approve, name="leave_approve"),


    path('leave_type/list', views.leave_type_list, name="leave_type_list"),
    path('leave_type/add', views.leave_type_add, name="leave_type_add"),
    path('leave_type/<int:leave_type_id>/edit/', views.leave_type_edit, name="leave_type_edit"),
    path('leave_type/<int:leave_type_id>/view/', views.leave_type_view, name="leave_type_view"),
    path('financial_year_leave/list', views.financial_year_leaves, name="financial_year_leaves"),
    path('financial_year_leave/add', views.financial_year_leave_add, name="financial_year_leave_add"),
    path('financial_year_leave/<int:fyl_id>/edit/', views.financial_year_leave_edit, name="financial_year_leave_edit"),
    path('financial_year_leave/<int:fyl_id>/view/', views.financial_year_leave_view, name="financial_year_leave_view"),
    path('finacial_year/list', views.financial_year_list, name="financial_year_list"),
    path('finacial_year/add', views.financial_year_add, name="financial_year_add"),
    path('leave/add', views.leave_add, name="leave_add"),
    path('leave/pending_leave/today', views.pending_leave_today, name="pending_leave_today"),
    path('leave/pending_leave/week', views.pending_leave_week, name="pending_leave_week"),
    path('leave/pending_leave/month', views.pending_leave_month, name="pending_leave_month"),
    path('leave/unauthorized_leave/today', views.unauthorized_leave_today, name="unauthorized_leave_today"),
    path('leave/unauthorized_leave/week', views.unauthorized_leave_week, name="unauthorized_leave_week"),
    path('leave/unauthorized_leave/month', views.unauthorized_leave_month, name="unauthorized_leave_month"),
    path('leave/approved/today', views.approved_leave_today, name="approved_leave_today"),
    path('leave/approved/week', views.approved_leave_week, name="approved_leave_week"),
    path('leave/approved/month', views.approved_leave_month, name="approved_leave_month"),

]

urlpatterns += [path('api/', include(api_urlpatterns))]
