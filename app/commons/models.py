from django.db import models
from django.utils.translation import gettext_lazy as _


class Prefecture(models.Model):

    name = models.CharField(max_length=128, null=False, blank=False, unique=True, help_text=_('Όνομα Νομού'))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name="unique_prefecture_name")
        ]

    def __str__(self):
        return f"{self.name}"


class Municipality(models.Model):

    prefecture = models.ForeignKey(Prefecture, null=False, on_delete=models.CASCADE, help_text=_('Νομός'))
    name = models.CharField(max_length=128, null=False, blank=False, help_text='Όνομα Δήμου')
    within_pysde = models.BooleanField(null=False, default=False, help_text='Εντός ΠΥΣΔΕ', db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['prefecture', 'name']),
            models.Index(fields=['within_pysde']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['prefecture', 'name'], name='unique_prefecture_and_name')
        ]

    def __str__(self):
        return f"{self.name}"


class School(models.Model):
    ministry_code = models.CharField(max_length=7, blank=False)
    name = models.CharField(max_length=80, blank=False)
    school_kind = models.CharField(max_length=80, blank=False)
    school_type = models.CharField(max_length=80, blank=False)
    telephone = models.CharField(max_length=32, blank=False)
    fax = models.CharField(max_length=32, blank=True)
    email = models.CharField(max_length=64, blank=False)
    is_eaep = models.BooleanField(null=False, default=False)
    is_nps = models.BooleanField(null=False, default=False)
    address = models.CharField(max_length=128, blank=True)
    zip_code = models.CharField(max_length=12, blank=True)
    prefecture = models.ForeignKey(Prefecture, null=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [
            models.Index(fields=['school_kind', 'school_type', 'prefecture']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['ministry_code'], name='unique_school_ministry_code'),
            models.UniqueConstraint(fields=['name'], name='unique_school_name')
        ]
