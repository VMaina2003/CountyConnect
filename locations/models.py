from django.db import models
from django.utils.translation import gettext_lazy as _


class County(models.Model):
    """
    Represents one of Kenya's 47 counties.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.PositiveSmallIntegerField(
    unique=True,
    null=True, blank=True,
    help_text=_("Official county code, e.g., 042 for Kisumu")
)

    

    class Meta:
        verbose_name_plural = "Counties"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} County"


class SubCounty(models.Model):
    """
    Represents sub-counties within a county.
    """
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name="subcounties")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True, null=True)
    population = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Sub-counties"
        unique_together = ("county", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.county.name})"


class Constituency(models.Model):
    """
    Represents constituencies within a sub-county.
    """
    sub_county = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name="constituencies")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Constituencies"
        unique_together = ("sub_county", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sub_county.name})"


class Ward(models.Model):
    constituency = models.ForeignKey(
        Constituency,
        on_delete=models.CASCADE,
        related_name="wards",
        null=True,  blank=True
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Wards"
        unique_together = ("constituency", "name")
        ordering = ["name"]


    def __str__(self):
        return f"{self.name} ({self.constituency.name})"
