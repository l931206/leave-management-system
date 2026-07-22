from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import LeaveRequest, LeaveType, Profile


class LeaveFlowTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username="manager", password="pass1234")
        self.manager.profile.role = Profile.ROLE_MANAGER
        self.manager.profile.save()

        self.employee = User.objects.create_user(username="employee", password="pass1234")
        self.employee.profile.manager = self.manager
        self.employee.profile.save()

        self.leave_type = LeaveType.objects.create(name="特休")

    def test_employee_can_submit_leave(self):
        self.client.login(username="employee", password="pass1234")
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=8)
        response = self.client.post(
            reverse("create_leave"),
            {
                "leave_type": self.leave_type.id,
                "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
                "reason": "家庭事務",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(LeaveRequest.objects.count(), 1)

    def test_manager_can_approve(self):
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            manager=self.manager,
            leave_type=self.leave_type,
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=8),
            reason="家庭事務",
        )
        self.client.login(username="manager", password="pass1234")
        response = self.client.post(reverse("approve_leave", args=[leave_request.id]), {"comment": ""})
        self.assertEqual(response.status_code, 302)
        leave_request.refresh_from_db()
        self.assertEqual(leave_request.status, LeaveRequest.STATUS_APPROVED)
