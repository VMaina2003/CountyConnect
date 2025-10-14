from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Department,
    DepartmentCategory,
    DepartmentUnit,
    DepartmentOfficer,
    DepartmentContact,
)
from .serializers import (
    DepartmentSerializer,
    DepartmentCategorySerializer,
    DepartmentUnitSerializer,
    DepartmentOfficerSerializer,
    DepartmentContactSerializer,
)

# ============================================================
#   BASE BULK-CREATE MIXIN
# ============================================================
class BulkCreateMixin:
    """
    Mixin to allow bulk creation (POST list of objects).
    """

    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# ============================================================
#   DEPARTMENT VIEWSET
# ============================================================
class DepartmentViewSet(BulkCreateMixin, viewsets.ModelViewSet):
    """
    Handles listing, creating, updating, and deleting departments.
    - Anonymous users can only view departments.
    - Authenticated users (e.g., admins) can create/update/delete.
    - Supports filtering by county, category, or search query.
    """
    queryset = Department.objects.select_related("county", "category").prefetch_related("units", "officers")
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "county__name"]

    def get_queryset(self):
        qs = super().get_queryset()
        county_id = self.request.query_params.get("county")
        category_id = self.request.query_params.get("category")
        if county_id:
            qs = qs.filter(county_id=county_id)
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def perform_create(self, serializer):
        """
        Save and send email notification when a new department is created.
        """
        departments = serializer.save()
        # Handle both single and bulk cases
        if not isinstance(departments, list):
            departments = [departments]

        for department in departments:
            if department.email:
                send_mail(
                    subject=f"New Department Registered: {department.name}",
                    message=(
                        f"A new department has been created:\n\n"
                        f"Name: {department.name}\n"
                        f"County: {department.county}\n"
                        f"Category: {department.category}\n"
                        f"Description: {department.description or 'N/A'}\n\n"
                        f"Visit your CountyConnect dashboard for details."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[department.email],
                    fail_silently=True,
                )


# ============================================================
#   DEPARTMENT CATEGORY VIEWSET
# ============================================================
class DepartmentCategoryViewSet(BulkCreateMixin, viewsets.ModelViewSet):
    """
    Categories for grouping departments, e.g.:
    - Health
    - Infrastructure
    - Education
    """
    queryset = DepartmentCategory.objects.all().order_by("name")
    serializer_class = DepartmentCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


# ============================================================
#   DEPARTMENT UNIT VIEWSET
# ============================================================
class DepartmentUnitViewSet(BulkCreateMixin, viewsets.ModelViewSet):
    """
    Sub-units under departments, e.g.:
    - Roads Unit (under Infrastructure)
    - Public Health Unit (under Health)
    """
    queryset = DepartmentUnit.objects.select_related("department", "head").order_by("department__name", "name")
    serializer_class = DepartmentUnitSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "department__name"]

    def get_queryset(self):
        qs = super().get_queryset()
        dept_id = self.request.query_params.get("department")
        if dept_id:
            qs = qs.filter(department_id=dept_id)
        return qs


# ============================================================
#   DEPARTMENT OFFICER VIEWSET
# ============================================================
class DepartmentOfficerViewSet(BulkCreateMixin, viewsets.ModelViewSet):
    """
    Officers working in departments.
    - Links to Django Users.
    - Can be filtered by department, unit, or subcounty.
    """
    queryset = DepartmentOfficer.objects.select_related("user", "department", "unit", "subcounty")
    serializer_class = DepartmentOfficerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__username", "position", "department__name"]

    def get_queryset(self):
        qs = super().get_queryset()
        dept_id = self.request.query_params.get("department")
        unit_id = self.request.query_params.get("unit")
        subcounty_id = self.request.query_params.get("subcounty")
        if dept_id:
            qs = qs.filter(department_id=dept_id)
        if unit_id:
            qs = qs.filter(unit_id=unit_id)
        if subcounty_id:
            qs = qs.filter(subcounty_id=subcounty_id)
        return qs


# ============================================================
#   DEPARTMENT CONTACT VIEWSET
# ============================================================
class DepartmentContactViewSet(BulkCreateMixin, viewsets.ModelViewSet):
    """
    Manages extra department contact channels like:
    - Additional email
    - Social media handles
    - Phone numbers
    """
    queryset = DepartmentContact.objects.select_related("department")
    serializer_class = DepartmentContactSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["department__name", "contact_type", "value"]

    def get_queryset(self):
        qs = super().get_queryset()
        dept_id = self.request.query_params.get("department")
        if dept_id:
            qs = qs.filter(department_id=dept_id)
        return qs

    def perform_create(self, serializer):
        """
        Notify the department via email if a new contact channel is added.
        """
        contacts = serializer.save()
        # Handle both single and bulk cases
        if not isinstance(contacts, list):
            contacts = [contacts]

        for contact in contacts:
            department = contact.department
            if department and department.email:
                send_mail(
                    subject=f"New Contact Added for {department.name}",
                    message=(
                        f"A new contact has been added for your department.\n\n"
                        f"Type: {contact.contact_type}\n"
                        f"Value: {contact.value}\n"
                        f"Active: {contact.active}\n\n"
                        f"Visit your CountyConnect dashboard for details."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[department.email],
                    fail_silently=True,
                )
