from decimal import Decimal
from datetime import datetime, time, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from leaveapp.models import LeaveBalance, LeaveType, Profile, LeaveRequest, LateNotice, ApprovalLog


class Command(BaseCommand):
    help = "建立展示用帳號、假別與額度"

    def handle(self, *args, **options):
        admin_user, _ = User.objects.get_or_create(username="admin")
        admin_user.first_name = "系統"
        admin_user.last_name = "管理者"
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password("demo1234")
        admin_user.save()
        admin_user.profile.role = Profile.ROLE_ADMIN
        admin_user.profile.save()

        manager, _ = User.objects.get_or_create(username="manager")
        manager.first_name = "王"
        manager.last_name = "主管"
        manager.set_password("demo1234")
        manager.save()
        manager.profile.role = Profile.ROLE_MANAGER
        manager.profile.manager = admin_user
        manager.profile.save()

        employee, _ = User.objects.get_or_create(username="employee")
        employee.first_name = "陳"
        employee.last_name = "員工"
        employee.set_password("demo1234")
        employee.save()
        employee.profile.role = Profile.ROLE_EMPLOYEE
        employee.profile.manager = manager
        employee.profile.save()

        leave_types = [
            ("特休", False, 1, Decimal("80.00")),
            ("病假", True, 2, Decimal("240.00")),
            ("事假", False, 3, Decimal("112.00")),
            ("公假", True, 4, Decimal("0.00")),
            ("婚假", True, 5, Decimal("64.00")),
            ("喪假", True, 6, Decimal("64.00")),
        ]

        year = timezone.localdate().year
        for name, requires_attachment, order, total_hours in leave_types:
            leave_type, _ = LeaveType.objects.get_or_create(
                name=name,
                defaults={
                    "requires_attachment": requires_attachment,
                    "display_order": order,
                },
            )
            leave_type.requires_attachment = requires_attachment
            leave_type.display_order = order
            leave_type.active = True
            leave_type.save()
            LeaveBalance.objects.get_or_create(
                employee=employee,
                leave_type=leave_type,
                year=year,
                defaults={"total_hours": total_hours},
            )


        # 建立更多員工與展示資料，讓主管 Dashboard 一登入就有內容
        demo_employees = [
            ("employee2", "林", "怡君"),
            ("employee3", "張", "志豪"),
            ("employee4", "李", "佳穎"),
        ]
        employees = [employee]
        for username, last_name, first_name in demo_employees:
            user, _ = User.objects.get_or_create(username=username)
            user.last_name = last_name
            user.first_name = first_name
            user.set_password("demo1234")
            user.save()
            user.profile.role = Profile.ROLE_EMPLOYEE
            user.profile.manager = manager
            user.profile.save()
            employees.append(user)
            for leave_type in LeaveType.objects.all():
                LeaveBalance.objects.get_or_create(
                    employee=user,
                    leave_type=leave_type,
                    year=year,
                    defaults={"total_hours": Decimal("80.00") if leave_type.name == "特休" else Decimal("112.00")},
                )

        tz = timezone.get_current_timezone()
        now = timezone.now()
        special = LeaveType.objects.get(name="特休")
        personal = LeaveType.objects.get(name="事假")
        sick = LeaveType.objects.get(name="病假")

        if not LeaveRequest.objects.exists():
            pending1 = LeaveRequest.objects.create(
                employee=employee,
                manager=manager,
                leave_type=special,
                start_datetime=now + timedelta(days=2),
                end_datetime=now + timedelta(days=2, hours=8),
                reason="家庭行程安排",
            )
            pending2 = LeaveRequest.objects.create(
                employee=employees[1],
                manager=manager,
                leave_type=personal,
                start_datetime=now + timedelta(days=3),
                end_datetime=now + timedelta(days=3, hours=4),
                reason="辦理私人事務",
            )
            approved = LeaveRequest.objects.create(
                employee=employees[2], manager=manager, leave_type=special,
                start_datetime=now - timedelta(days=3), end_datetime=now - timedelta(days=3) + timedelta(hours=8),
                reason="家庭旅遊", status=LeaveRequest.STATUS_APPROVED,
                manager_comment="已確認工作交接", reviewed_at=now - timedelta(days=5), balance_applied=True,
            )
            ApprovalLog.objects.create(leave_request=approved, reviewer=manager, action=ApprovalLog.ACTION_APPROVE, comment="已確認工作交接")
            rejected = LeaveRequest.objects.create(
                employee=employees[3], manager=manager, leave_type=personal,
                start_datetime=now + timedelta(days=1), end_datetime=now + timedelta(days=1, hours=8),
                reason="個人行程", status=LeaveRequest.STATUS_REJECTED,
                manager_comment="當日已有重要會議，請調整日期", reviewed_at=now - timedelta(days=1),
            )
            ApprovalLog.objects.create(leave_request=rejected, reviewer=manager, action=ApprovalLog.ACTION_REJECT, comment="當日已有重要會議，請調整日期")

        if not LateNotice.objects.filter(date=timezone.localdate()).exists():
            LateNotice.objects.create(employee=employees[1], manager=manager, date=timezone.localdate(), expected_arrival=time(9, 35), reason="捷運設備異常，預計延誤約 30 分鐘")
            LateNotice.objects.create(employee=employees[3], manager=manager, date=timezone.localdate(), expected_arrival=time(9, 20), reason="臨時處理家中狀況", viewed=True)

        self.stdout.write(self.style.SUCCESS("展示資料建立完成"))
        self.stdout.write("管理者：admin / demo1234")
        self.stdout.write("主管：manager / demo1234")
        self.stdout.write("員工：employee / demo1234")
