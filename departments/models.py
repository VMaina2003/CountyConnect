from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from locations.models import County, SubCounty

User = get_user_model()


class DepartmentCategory(models.Model):
    """
    Categorizes departments (e.g. Social Services, Infrastructure, Finance).
    Helps with grouping at national or county level.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Department Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Department(models.Model):
    """
    Represents a department within a county government.
    """
    county = models.ForeignKey(
        County,
        on_delete=models.CASCADE,
        related_name="departments"
    )
    category = models.ForeignKey(
        DepartmentCategory,
        on_delete=models.SET_NULL,
        related_name="departments",
        blank=True,
        null=True
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, blank=True, null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    mandate = models.TextField(
        blank=True,
        null=True,
        help_text="Core functions and responsibilities of this department."
    )
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    head_office_location = models.CharField(max_length=200, blank=True, null=True)
    active = models.BooleanField(default=True)

    # Additional details
    budget_allocated = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    staff_count = models.PositiveIntegerField(default=0)
    date_established = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ("county", "name")
        ordering = ["county__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.county.name})"


class DepartmentUnit(models.Model):
    """
    Represents sub-units or sections within a department.
    E.g., Roads Department → Unit: Bridge Maintenance
    """
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="units"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    head = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_units"
    )

    class Meta:
        verbose_name_plural = "Department Units"
        unique_together = ("department", "name")

    def __str__(self):
        return f"{self.name} - {self.department.name}"


class DepartmentOfficer(models.Model):
    """
    Officers assigned to a department or unit.
    """
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="officers"
    )
    unit = models.ForeignKey(
        DepartmentUnit,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="officers"
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, blank=True, null=True)
    subcounty = models.ForeignKey(
        SubCounty,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Area officer oversees within the county."
    )
    is_head = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    date_assigned = models.DateField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Department Officers"
        ordering = ["department__name", "user__username"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.department.name})"


class DepartmentContact(models.Model):
    """
    Additional communication channels for a department.
    """
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="contacts"
    )
    contact_type = models.CharField(
        max_length=50,
        choices=[
            ("EMAIL", "Email"),
            ("PHONE", "Phone"),
            ("TWITTER", "Twitter"),
            ("FACEBOOK", "Facebook"),
            ("WEBSITE", "Website"),
        ]
    )
    value = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.contact_type}: {self.value}"
