from django.contrib import admin
from .models import (
    DepartmentCategory, Department, DepartmentUnit,
    DepartmentOfficer, DepartmentContact
)

admin.site.register(DepartmentCategory)
admin.site.register(DepartmentContact)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "county", "category", "email", "active")
    list_filter = ("county", "category", "active")
    search_fields = ("name", "county__name", "category__name")


@admin.register(DepartmentUnit)
class DepartmentUnitAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "head")
    list_filter = ("department",)
    search_fields = ("name", "department__name")


@admin.register(DepartmentOfficer)
class DepartmentOfficerAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "subcounty", "is_head", "active")
    list_filter = ("department", "is_head", "active")
    search_fields = ("user__username", "department__name", "subcounty__constituency_name")
