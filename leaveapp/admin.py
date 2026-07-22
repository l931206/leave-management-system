from django.contrib import admin

from .models import ApprovalLog, LateNotice, LeaveBalance, LeaveRequest, LeaveType, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "manager")
    list_filter = ("role",)
    search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "requires_attachment", "active", "display_order")
    list_editable = ("requires_attachment", "active", "display_order")


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "year", "total_hours", "used_hours", "remaining_hours")
    list_filter = ("year", "leave_type")
    search_fields = ("employee__username", "employee__first_name", "employee__last_name")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "start_datetime",
        "end_datetime",
        "status",
        "manager",
        "created_at",
    )
    list_filter = ("status", "leave_type")
    search_fields = ("employee__username", "employee__first_name", "employee__last_name", "reason")


@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    list_display = ("leave_request", "reviewer", "action", "created_at")
    list_filter = ("action",)


@admin.register(LateNotice)
class LateNoticeAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "expected_arrival", "manager", "viewed", "created_at")
    list_filter = ("viewed", "date")
    search_fields = ("employee__username", "employee__first_name", "employee__last_name", "reason")
