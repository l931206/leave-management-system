from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    ROLE_EMPLOYEE = "employee"
    ROLE_MANAGER = "manager"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_EMPLOYEE, "員工"),
        (ROLE_MANAGER, "主管"),
        (ROLE_ADMIN, "系統管理者"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_EMPLOYEE)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members",
        verbose_name="直屬主管",
    )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"


class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="假別名稱")
    requires_attachment = models.BooleanField(default=False, verbose_name="需附件")
    active = models.BooleanField(default=True, verbose_name="啟用")
    display_order = models.PositiveIntegerField(default=0, verbose_name="顯示順序")

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "假別"
        verbose_name_plural = "假別"

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_balances")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name="balances")
    year = models.PositiveIntegerField(default=timezone.localdate().year)
    total_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    used_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        unique_together = ("employee", "leave_type", "year")
        ordering = ["leave_type__display_order", "leave_type__id"]

    @property
    def remaining_hours(self):
        return max(Decimal("0.00"), self.total_hours - self.used_hours)

    def __str__(self):
        return f"{self.employee} / {self.leave_type} / {self.year}"


class LeaveRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "待審核"),
        (STATUS_APPROVED, "已核准"),
        (STATUS_REJECTED, "已退回"),
        (STATUS_CANCELLED, "已取消"),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_datetime = models.DateTimeField(verbose_name="開始時間")
    end_datetime = models.DateTimeField(verbose_name="結束時間")
    reason = models.TextField(verbose_name="請假原因")
    attachment = models.FileField(upload_to="leave_attachments/%Y/%m/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_leave_requests",
    )
    manager_comment = models.TextField(blank=True, verbose_name="主管備註")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    balance_applied = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    @property
    def duration_hours(self):
        if not self.start_datetime or not self.end_datetime:
            return Decimal("0.00")
        seconds = (self.end_datetime - self.start_datetime).total_seconds()
        return Decimal(str(max(seconds / 3600, 0))).quantize(Decimal("0.01"))

    def clean(self):
        if self.end_datetime <= self.start_datetime:
            raise ValidationError("結束時間必須晚於開始時間。")
        if self.leave_type_id and self.leave_type.requires_attachment and not self.attachment:
            raise ValidationError({"attachment": "此假別需要上傳附件。"})

    def __str__(self):
        return f"{self.employee} - {self.leave_type} - {self.get_status_display()}"


class ApprovalLog(models.Model):
    ACTION_APPROVE = "approve"
    ACTION_REJECT = "reject"
    ACTION_CHOICES = [
        (ACTION_APPROVE, "核准"),
        (ACTION_REJECT, "退回"),
    ]

    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name="approval_logs",
    )
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.leave_request_id} - {self.get_action_display()}"


class LateNotice(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="late_notices")
    date = models.DateField(default=timezone.localdate, verbose_name="晚到日期")
    expected_arrival = models.TimeField(verbose_name="預計到達時間")
    reason = models.TextField(verbose_name="晚到原因")
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_late_notices",
    )
    viewed = models.BooleanField(default=False, verbose_name="主管已查看")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.expected_arrival}"
