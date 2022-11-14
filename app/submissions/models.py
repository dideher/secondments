from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User
from commons.models import Municipality, School


class Submission(models.Model):

    class SubmissionStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Πρόχειρη')
        DELETED = 'DELETED', _('Διαγραμμένη')
        SUBMITTED = 'SUBMITTED', _('Υποβεβλημένη')
        UNDER_REVIEW = 'UNDER_REVIEW', _('Υπο Εξέταση')
        FINALIZED = 'FINALIZED', _('Καταχωρημένη/Αποδεκτή')
        CANCELLED = 'CANCELLED', _('Ακυρωμένη')

    class HealthIssues50_67_80(models.TextChoices):
        FROM_50_TO_66 = 'FROM_50_TO_66', _('Αναπηρία 50-66%')
        FROM_67_TO_79 = 'FROM_67_TO_79', _('Αναπηρία 67-79%')
        FROM_80_TO_100 = 'FROM_80_TO_100', _('Αναπηρία 80% και άνω')

    class HealthIssues50_67(models.TextChoices):
        FROM_50_TO_66 = 'FROM_50_TO_66', _('Αναπηρία 50-66%')
        FROM_67_TO_100 = 'FROM_67_TO_100', _('Αναπηρία 67% και άνω')

    class HealthIssues67(models.TextChoices):
        FROM_67_TO_100 = 'FROM_67_TO_100', _('Αναπηρία 67% και άνω')

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    # 4
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, related_name='related_school_submission',
                               help_text=_('Οργανική Θέση'))
    effective_school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True,
                                         related_name='related_effective_school_submission',
                                         help_text=_('Σχολείο που Υπηρετεί'))
    year_of_appointment = models.PositiveSmallIntegerField(null=False, default=0)

    # 5. ΔΙΕΥΘΥΝΣΗ ΜΟΝΙΜΗΣ ΚΑΤΟΙΚΙΑΣ
    address_city = models.CharField(max_length=64, null=False, blank=False)
    address_line = models.CharField(max_length=128, null=False, blank=False)
    address_number = models.CharField(max_length=32, null=False, blank=False)
    address_zip_code = models.CharField(max_length=32, null=False, blank=False)
    telephone = models.CharField(max_length=32, null=False, blank=True)
    mobile = models.CharField(max_length=32, null=False, blank=True)

    status = models.CharField(
        max_length=32,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.DRAFT,
        null=False,
        blank=False,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    # 1. Συνολική Υπηρεσία
    work_experience_years = models.PositiveSmallIntegerField(null=False, default=0)
    work_experience_months = models.PositiveSmallIntegerField(null=False, default=0)
    work_experience_days = models.PositiveSmallIntegerField(null=False, default=0)

    # 2. Συνυπηρέτηση
    work_together = models.BooleanField(null=False, default=False, help_text=_('Συνυπηρέτηση'))
    work_together_municipality = models.ForeignKey(Municipality, null=True, default=None, on_delete=models.SET_NULL,
                                                   related_name='related_work_together_municipality_submission',
                                                   help_text=_('Δήμος Συνυπηρέτησης'))

    # 3. Εντοπιότητα
    locality = models.BooleanField(null=False, default=False, help_text=_('Εντοπιότητα'))
    locality_municipality = models.ForeignKey(Municipality, null=True, default=None, on_delete=models.SET_NULL,
                                              related_name='related_locality_municipality_submissions',
                                              help_text=_('Δήμος Εντοπιότητας'))

    # 4. Οικογενειακοί Λόγοι
    married = models.BooleanField(null=False, default=False, help_text=_('Έγγαμος'))
    divorced = models.BooleanField(null=False, default=False, help_text=_('Διαζευγμένος'))
    separated = models.BooleanField(null=False, default=False, help_text=_('Σε Διάσταση'))
    widowhood = models.BooleanField(null=False, default=False, help_text=_('Σε Χηρεία'))
    single_parent_family = models.BooleanField(null=False, default=False, help_text=_('Μονογονεϊκη Οικογένεια'))
    number_of_children = models.PositiveSmallIntegerField(null=False, default=0, help_text=_('Αριθμός Τέκνων'))
    child_custody = models.BooleanField(null=False, default=False, help_text=_('Επιμέλεια Τέκνων'))
    minor_child = models.BooleanField(null=False, default=False, help_text=_('Ανήλικο Τέκνο'))

    # 5. Σοβαροί Λόγοι Υγείας
    health_issues = models.CharField(
        max_length=32,
        choices=HealthIssues50_67_80.choices,
        default=None,
        null=True,
        help_text=_('Λόγοι Υγείας Ιδίων')
    )

    health_issues_partner = models.CharField(
        max_length=32,
        choices=HealthIssues50_67_80.choices,
        default=None,
        null=True,
        help_text=_('Λόγοι Υγείας Συζύγου')
    )

    health_issues_child = models.CharField(
        max_length=32,
        choices=HealthIssues50_67_80.choices,
        default=None,
        null=True,
        help_text=_('Λόγοι Υγείας Τέκνων')
    )

    health_issues_parent = models.CharField(
        max_length=32,
        choices=HealthIssues50_67.choices,
        default=None,
        null=True,
        help_text=_('Λόγοι Υγείας Γονέων')
    )

    health_issues_sibling = models.CharField(
        max_length=32,
        choices=HealthIssues67.choices,
        default=None,
        null=True,
        help_text=_('Λόγοι Υγείας Αδελφών')
    )

    parents_residence_municipality = models.ForeignKey(Municipality, null=True, default=None, on_delete=models.SET_NULL,
                                                       related_name='related_parents_residence_municipality_submission',
                                                       help_text=_('Δήμος Διαμονής Γονέων'))

    sibling_residence_municipality = models.ForeignKey(Municipality, null=True, default=None, on_delete=models.SET_NULL,
                                                       related_name='related_sibling_residence_municipality_submission',
                                                       help_text=_('Δήμος Διαμονής Αδελφού-(ων)'))

    # 6. Θεραπεία Εξωσωματικής Γονιμοποίησης
    ivf_treatment = models.BooleanField(null=False, default=False, help_text=_('Θεραπεία Εξωσωματικής Γονιμοποίησης'))

    # 7. Μεταπτυχιακές Σπουδές
    postgraduate_studies = models.BooleanField(null=False, default=False, help_text=_('Μεταπτυχιακές Σπουδές'))
    postgraduate_studies_municipality = models.ForeignKey(Municipality, null=True, default=None,
                                                          on_delete=models.SET_NULL,
                                                          related_name='related_postgraduate_studies_municipality_submission',
                                                                       help_text=_('Δήμος Σπουδών'))

    # Γ. Αποσπάσεις Κατα Προτεραιότητα
    has_many_children = models.BooleanField(null=False, default=False, help_text=_('Πολύτεκνος'))
    has_child_with_disabilities_67 = models.BooleanField(null=False, default=False,
                                                         help_text=_('Γονέας τέκνου με ποσοστό αναπηρίας 67%'))
    has_illness = models.BooleanField(null=False, default=False, help_text=_('Ασθένεια'))

    # DIMOS_ENTOPOIT -> DHMOI OLOU TOU NOMOU HRAKLEIOU
    # DIMOS_SYNIP -> DHMOI OLOU TOU NOMOU HRAKLEIOU
    # section 4 :
    # * prosthiki "Aggamos"
    # * note to slavikos -> mia epilogh
    # * an epiloskou diazeumenos h se diastash  kai exei paidia (pedio arithmos teknon) tote mporei na epileksei
    # "epimeleia teknon".
    # *to "anhliko tekno" to epilegei mono otan einai se xhreia  kai exei paidia  (pedio arithmos teknon)
    # label "anhliko tekno" => "anhliko/spoudazwn tekno"

    # dhmos spoudon -> mono hrakleio

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
        ]


class SubmissionEvent(models.Model):
    event_date = models.DateTimeField(auto_now_add=True, null=False)
    related_to = models.ForeignKey(Submission, on_delete=models.CASCADE)
    triggered_by = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['event_date', 'related_to', 'triggered_by']),
        ]

