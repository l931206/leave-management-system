import csv
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import employee_required, manager_required
from .forms import LateNoticeForm, LeaveRequestForm, ReviewForm
from .models import (
    ApprovalLog,
    LateNotice,
    LeaveBalance,
    LeaveRequest,
    Profile,
)


def _is_manager_for(user, employee):
    if user.profile.role == Profile.ROLE_ADMIN:
        return True
    return employee.profile.manager_id == user.id


@login_required
def dashboard(request):
    profile = request.user.profile
    today = timezone.localdate()
    month_start = today.replace(day=1)

    context = {
        "profile": profile,
        "my_requests": request.user.leave_requests.select_related("leave_type", "manager")[:8],
        "my_late_notices": request.user.late_notices.select_related("manager")[:8],
        "balances": request.user.leave_balances.select_related("leave_type").filter(year=today.year),
    }

    if profile.role in {Profile.ROLE_MANAGER, Profile.ROLE_ADMIN}:
        if profile.role == Profile.ROLE_ADMIN:
            team_users = Profile.objects.filter(role=Profile.ROLE_EMPLOYEE).select_related("user")
            team_requests = LeaveRequest.objects.all()
            late_notices = LateNotice.objects.filter(date=today)
        else:
            team_users = Profile.objects.filter(manager=request.user).select_related("user")
            team_requests = LeaveRequest.objects.filter(manager=request.user)
            late_notices = LateNotice.objects.filter(manager=request.user, date=today)

        pending = team_requests.filter(status=LeaveRequest.STATUS_PENDING)
        month_requests = team_requests.filter(created_at__date__gte=month_start)
        approved_month = month_requests.filter(status=LeaveRequest.STATUS_APPROVED).count()
        rejected_month = month_requests.filter(status=LeaveRequest.STATUS_REJECTED).count()
        total_month = month_requests.count()
        approval_rate = round(approved_month / total_month * 100) if total_month else 0

        context.update({
            "pending_requests": pending.select_related("employee", "leave_type")[:20],
            "today_late_notices": late_notices.select_related("employee")[:20],
            "team_members_count": team_users.count(),
            "pending_count": pending.count(),
            "late_today_count": late_notices.count(),
            "approved_month_count": approved_month,
            "rejected_month_count": rejected_month,
            "approval_rate": approval_rate,
            "recent_team_requests": team_requests.select_related("employee", "leave_type").exclude(
                status=LeaveRequest.STATUS_PENDING
            ).order_by("-reviewed_at", "-created_at")[:6],
            "team_on_leave_today": team_requests.filter(
                status=LeaveRequest.STATUS_APPROVED,
                start_datetime__date__lte=today,
                end_datetime__date__gte=today,
            ).select_related("employee", "leave_type")[:8],
        })

    return render(request, "leaveapp/dashboard.html", context)


@login_required
@employee_required
def create_leave(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST, request.FILES)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = request.user
            leave_request.manager = request.user.profile.manager
            if not leave_request.manager:
                messages.error(request, "尚未設定直屬主管，請聯絡系統管理者。")
            else:
                leave_request.full_clean()
                leave_request.save()
                messages.success(request, "請假申請已送出。")
                return redirect("leave_detail", pk=leave_request.pk)
    else:
        form = LeaveRequestForm()

    return render(request, "leaveapp/leave_form.html", {"form": form})


@login_required
def leave_detail(request, pk):
    leave_request = get_object_or_404(
        LeaveRequest.objects.select_related("employee", "manager", "leave_type"),
        pk=pk,
    )
    allowed = (
        leave_request.employee_id == request.user.id
        or _is_manager_for(request.user, leave_request.employee)
    )
    if not allowed:
        messages.error(request, "你沒有權限查看這筆申請。")
        return redirect("dashboard")

    return render(
        request,
        "leaveapp/leave_detail.html",
        {"leave_request": leave_request, "review_form": ReviewForm()},
    )


@login_required
@require_POST
def cancel_leave(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk, employee=request.user)
    if leave_request.status != LeaveRequest.STATUS_PENDING:
        messages.error(request, "只有待審核申請可以取消。")
        return redirect("leave_detail", pk=pk)
    leave_request.status = LeaveRequest.STATUS_CANCELLED
    leave_request.save(update_fields=["status"])
    messages.success(request, "申請已取消。")
    return redirect("leave_detail", pk=pk)


@login_required
@manager_required
@require_POST
def approve_leave(request, pk):
    form = ReviewForm(request.POST)
    if not form.is_valid():
        messages.error(request, "表單內容有誤。")
        return redirect("leave_detail", pk=pk)

    with transaction.atomic():
        leave_request = get_object_or_404(
            LeaveRequest.objects.select_for_update().select_related("employee", "leave_type"),
            pk=pk,
        )
        if not _is_manager_for(request.user, leave_request.employee):
            messages.error(request, "你不是此員工的直屬主管。")
            return redirect("dashboard")
        if leave_request.status != LeaveRequest.STATUS_PENDING:
            messages.error(request, "這筆申請已經處理過。")
            return redirect("leave_detail", pk=pk)

        leave_request.status = LeaveRequest.STATUS_APPROVED
        leave_request.manager = request.user
        leave_request.manager_comment = form.cleaned_data["comment"]
        leave_request.reviewed_at = timezone.now()

        if not leave_request.balance_applied:
            balance, _ = LeaveBalance.objects.select_for_update().get_or_create(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=leave_request.start_datetime.year,
                defaults={"total_hours": Decimal("0.00")},
            )
            balance.used_hours += leave_request.duration_hours
            balance.save(update_fields=["used_hours"])
            leave_request.balance_applied = True

        leave_request.save()
        ApprovalLog.objects.create(
            leave_request=leave_request,
            reviewer=request.user,
            action=ApprovalLog.ACTION_APPROVE,
            comment=form.cleaned_data["comment"],
        )

    messages.success(request, "請假申請已核准。")
    return redirect("leave_detail", pk=pk)


@login_required
@manager_required
@require_POST
def reject_leave(request, pk):
    form = ReviewForm(request.POST)
    if not form.is_valid():
        messages.error(request, "表單內容有誤。")
        return redirect("leave_detail", pk=pk)

    comment = form.cleaned_data["comment"].strip()
    if not comment:
        messages.error(request, "退回申請時必須填寫原因。")
        return redirect("leave_detail", pk=pk)

    with transaction.atomic():
        leave_request = get_object_or_404(
            LeaveRequest.objects.select_for_update().select_related("employee"),
            pk=pk,
        )
        if not _is_manager_for(request.user, leave_request.employee):
            messages.error(request, "你不是此員工的直屬主管。")
            return redirect("dashboard")
        if leave_request.status != LeaveRequest.STATUS_PENDING:
            messages.error(request, "這筆申請已經處理過。")
            return redirect("leave_detail", pk=pk)

        leave_request.status = LeaveRequest.STATUS_REJECTED
        leave_request.manager = request.user
        leave_request.manager_comment = comment
        leave_request.reviewed_at = timezone.now()
        leave_request.save()
        ApprovalLog.objects.create(
            leave_request=leave_request,
            reviewer=request.user,
            action=ApprovalLog.ACTION_REJECT,
            comment=comment,
        )

    messages.success(request, "請假申請已退回。")
    return redirect("leave_detail", pk=pk)


@login_required
@employee_required
def create_late_notice(request):
    if request.method == "POST":
        form = LateNoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.employee = request.user
            notice.manager = request.user.profile.manager
            if not notice.manager:
                messages.error(request, "尚未設定直屬主管，請聯絡系統管理者。")
            else:
                notice.save()
                messages.success(request, "晚到通知已送出給主管。")
                return redirect("dashboard")
    else:
        form = LateNoticeForm(initial={"date": timezone.localdate()})

    return render(request, "leaveapp/late_notice_form.html", {"form": form})


@login_required
@manager_required
@require_POST
def mark_late_viewed(request, pk):
    notice = get_object_or_404(LateNotice, pk=pk)
    if request.user.profile.role != Profile.ROLE_ADMIN and notice.manager_id != request.user.id:
        messages.error(request, "你沒有權限處理這筆通知。")
        return redirect("dashboard")
    notice.viewed = True
    notice.save(update_fields=["viewed"])
    messages.success(request, "已標記為查看。")
    next_url = request.POST.get("next", "").strip()
    if next_url.startswith("/"):
        return redirect(next_url)
    return redirect("manager_late_list")



def _manager_leave_queryset(user):
    """Return leave requests visible to the current manager or administrator."""
    if user.profile.role == Profile.ROLE_ADMIN:
        return LeaveRequest.objects.all()
    return LeaveRequest.objects.filter(manager=user)


def _manager_late_queryset(user):
    """Return late notices visible to the current manager or administrator."""
    if user.profile.role == Profile.ROLE_ADMIN:
        return LateNotice.objects.all()
    return LateNotice.objects.filter(manager=user)


@login_required
@manager_required
def manager_leave_list(request):
    """Manager leave-management page with search and status filtering."""
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "all").strip()

    requests_qs = _manager_leave_queryset(request.user).select_related(
        "employee",
        "leave_type",
        "manager",
    )

    if query:
        requests_qs = requests_qs.filter(
            Q(employee__username__icontains=query)
            | Q(employee__first_name__icontains=query)
            | Q(employee__last_name__icontains=query)
            | Q(leave_type__name__icontains=query)
            | Q(reason__icontains=query)
        )

    valid_statuses = {
        LeaveRequest.STATUS_PENDING,
        LeaveRequest.STATUS_APPROVED,
        LeaveRequest.STATUS_REJECTED,
        LeaveRequest.STATUS_CANCELLED,
    }
    if status in valid_statuses:
        requests_qs = requests_qs.filter(status=status)

    all_visible = _manager_leave_queryset(request.user)
    counts = {
        "all": all_visible.count(),
        "pending": all_visible.filter(status=LeaveRequest.STATUS_PENDING).count(),
        "approved": all_visible.filter(status=LeaveRequest.STATUS_APPROVED).count(),
        "rejected": all_visible.filter(status=LeaveRequest.STATUS_REJECTED).count(),
        "cancelled": all_visible.filter(status=LeaveRequest.STATUS_CANCELLED).count(),
    }

    return render(
        request,
        "leaveapp/manager_leave_list.html",
        {
            "leave_requests": requests_qs.order_by("-created_at"),
            "query": query,
            "status_filter": status,
            "counts": counts,
        },
    )


@login_required
@manager_required
def manager_late_list(request):
    """Manager late-notice page with search and viewed-state filtering."""
    query = request.GET.get("q", "").strip()
    viewed = request.GET.get("viewed", "all").strip()
    date_filter = request.GET.get("date", "all").strip()
    today = timezone.localdate()

    notices = _manager_late_queryset(request.user).select_related(
        "employee",
        "manager",
    )

    if query:
        notices = notices.filter(
            Q(employee__username__icontains=query)
            | Q(employee__first_name__icontains=query)
            | Q(employee__last_name__icontains=query)
            | Q(reason__icontains=query)
        )

    if viewed == "viewed":
        notices = notices.filter(viewed=True)
    elif viewed == "unviewed":
        notices = notices.filter(viewed=False)

    if date_filter == "today":
        notices = notices.filter(date=today)

    all_visible = _manager_late_queryset(request.user)
    counts = {
        "all": all_visible.count(),
        "today": all_visible.filter(date=today).count(),
        "viewed": all_visible.filter(viewed=True).count(),
        "unviewed": all_visible.filter(viewed=False).count(),
    }

    return render(
        request,
        "leaveapp/manager_late_list.html",
        {
            "late_notices": notices.order_by("-date", "-created_at"),
            "query": query,
            "viewed_filter": viewed,
            "date_filter": date_filter,
            "counts": counts,
        },
    )

@login_required
@manager_required
def export_csv(request):
    profile = request.user.profile
    if profile.role == Profile.ROLE_ADMIN:
        requests_qs = LeaveRequest.objects.all()
    else:
        requests_qs = LeaveRequest.objects.filter(manager=request.user)

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="leave_requests.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "員工",
        "假別",
        "開始時間",
        "結束時間",
        "時數",
        "原因",
        "狀態",
        "主管",
        "送出時間",
        "審核時間",
    ])

    for item in requests_qs.select_related("employee", "leave_type", "manager").order_by("-created_at"):
        writer.writerow([
            item.employee.get_full_name() or item.employee.username,
            item.leave_type.name,
            timezone.localtime(item.start_datetime).strftime("%Y-%m-%d %H:%M"),
            timezone.localtime(item.end_datetime).strftime("%Y-%m-%d %H:%M"),
            item.duration_hours,
            item.reason,
            item.get_status_display(),
            (item.manager.get_full_name() or item.manager.username) if item.manager else "",
            timezone.localtime(item.created_at).strftime("%Y-%m-%d %H:%M"),
            timezone.localtime(item.reviewed_at).strftime("%Y-%m-%d %H:%M") if item.reviewed_at else "",
        ])
    return response
