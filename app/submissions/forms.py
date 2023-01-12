from datetime import datetime, timedelta
from django import forms
from leaves.models import Leave, LeaveType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from employees.models import Employee, LegacyEmployeeType
from leaves.models import LeaveType
from bootstrap_modal_forms.forms import BSModalModelForm
from phaistos.commons.forms import EmptyChoiceField
from phaistos.commons.widgets import DatePickerInput


class LeaveForm(BSModalModelForm):
    class Meta:
        model = Leave
        fields = ['date_from', 'date_until', 'leave_type', 'comment', 'number_of_days', 'effective_number_of_days']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
            'date_from': DatePickerInput(format='%Y-%m-%d'),
            'date_until': DatePickerInput(format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        self.employee: Employee = get_object_or_404(Employee, pk=kwargs.pop('employee_id'))
        super().__init__(*args, **kwargs)

        self.fields['leave_type'].queryset = LeaveType.objects.filter(
            suitable_for_employee_type=self.employee.employee_type).order_by('legacy_code')
        self.fields['number_of_days'].widget.attrs['readonly'] = True

    def clean_leave_type(self):
        data: LeaveType = self.cleaned_data['leave_type']

        if data.suitable_for_employee_type != self.employee.employee_type:
            # ops! leave type is not good for the given employee type
            raise ValidationError(_("Ο τύπος άδειας δεν είναι συμβατός με τον συγκεκριμένο εργαζόμενο"))

        return data

    def clean_effective_number_of_days(self):
        data = self.cleaned_data['effective_number_of_days']

        if data <= 0:
            raise ValidationError(_("Η διάρκεια των ημερών άδειας πρέπει να είναι μεγαλύτερη του 0"))

        return data

    def clean_number_of_days(self):

        data = self.cleaned_data

        date_from: datetime.date = data.get("date_from")
        date_until: datetime.date = data.get("date_until")

        if date_from is not None and date_until is not None:
            data['number_of_days'] = ((date_until - date_from) + timedelta(days=1)).days

        return data['number_of_days']

    def clean(self):
        """
        Validates the leave's date_from and date_until
        """
        cleaned_data = super().clean()

        date_from = cleaned_data.get("date_from")
        date_until = cleaned_data.get("date_until")

        if date_from and date_until and date_from > date_until:
            self.add_error('date_until', _('Η ημ/νία λήξης της άδειας είναι προγενέστερη της έναρξης'))

        return cleaned_data
