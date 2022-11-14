from django.contrib import admin
from .models import School, Prefecture, Municipality


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    pass


@admin.register(Prefecture)
class PrefecturesAdmin(admin.ModelAdmin):
    pass


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    pass

