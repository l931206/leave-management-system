from django import forms
from django.utils import timezone

from .models import LateNotice, LeaveRequest


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class TimeInput(forms.TimeInput):
    input_type = "time"


class DateInput(forms.DateInput):
    input_type = "date"


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = [
            "leave_type",
            "start_datetime",
            "end_datetime",
            "reason",
            "attachment",
        ]
        widgets = {
            "start_datetime": DateTimeLocalInput(format="%Y-%m-%dT%H:%M"),
            "end_datetime": DateTimeLocalInput(format="%Y-%m-%dT%H:%M"),
            "reason": forms.Textarea(attrs={"rows": 4, "placeholder": "請簡要填寫請假原因"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_datetime"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["end_datetime"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["leave_type"].queryset = self.fields["leave_type"].queryset.filter(active=True)

    def clean_attachment(self):
        file = self.cleaned_data.get("attachment")
        if not file:
            return file
        allowed = {
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/webp",
        }
        if getattr(file, "content_type", "") not in allowed:
            raise forms.ValidationError("附件只接受 PDF、JPG、PNG 或 WEBP。")
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("附件不可超過 5 MB。")
        return file


class LateNoticeForm(forms.ModelForm):
    class Meta:
        model = LateNotice
        fields = ["date", "expected_arrival", "reason"]
        widgets = {
            "date": DateInput(),
            "expected_arrival": TimeInput(),
            "reason": forms.Textarea(attrs={"rows": 4, "placeholder": "請填寫晚到原因"}),
        }

    def clean_date(self):
        value = self.cleaned_data["date"]
        today = timezone.localdate()
        if value < today:
            raise forms.ValidationError("晚到通知不可填寫過去日期。")
        return value


class ReviewForm(forms.Form):
    comment = forms.CharField(
        required=False,
        label="主管備註",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "核准可留空；退回時請填寫原因"}),
    )
