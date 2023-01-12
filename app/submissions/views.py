from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView

from bootstrap_modal_forms.generic import BSModalCreateView

from .models import Submission

class LeaveCreateView(LoginRequiredMixin, PermissionRequiredMixin, JsonableResponseMixin, BSModalCreateView):
    permission_required = ['leaves.add_leave']
    model = Leave
    form_class = LeaveForm

    def dispatch(self, request, *args, **kwargs):
        """
        Overridden so we can make sure the `Ipsum` instance exists
        before going any further.
        """
        self.employee: Employee = get_object_or_404(Employee, pk=kwargs['employee_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(LeaveCreateView, self).get_form_kwargs()
        kwargs['employee_id'] = self.employee.id

        return kwargs

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        leave: Leave = form.instance
        leave.employee = self.employee
        leave.number_of_days = (leave.date_until - leave.date_from).days + 1
        leave.created_on = timezone.now()
        leave.minoas_id = None

        messages.success(self.request, f'Η άδεια καταχωρήθηκε επιτυχώς')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("leaves:employee-leaves-list", kwargs={"pk": self.employee.id})
