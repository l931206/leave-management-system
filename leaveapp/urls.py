from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("leave/new/", views.create_leave, name="create_leave"),
    path("manager/leave/", views.manager_leave_list, name="manager_leave_list"),
    path("manager/late/", views.manager_late_list, name="manager_late_list"),
    path("leave/<int:pk>/", views.leave_detail, name="leave_detail"),
    path("leave/<int:pk>/attachment/", views.leave_attachment, name="leave_attachment"),
    path("leave/<int:pk>/cancel/", views.cancel_leave, name="cancel_leave"),
    path("leave/<int:pk>/approve/", views.approve_leave, name="approve_leave"),
    path("leave/<int:pk>/reject/", views.reject_leave, name="reject_leave"),
    path("late/new/", views.create_late_notice, name="create_late_notice"),
    path("late/<int:pk>/viewed/", views.mark_late_viewed, name="mark_late_viewed"),
    path("export/leave-requests.csv", views.export_csv, name="export_csv"),
]
