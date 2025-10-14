# departments/urls.py
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentCategoryViewSet,
    DepartmentViewSet,
    DepartmentUnitViewSet,
    DepartmentOfficerViewSet,
    DepartmentContactViewSet
)

router = DefaultRouter()
router.register(r'categories', DepartmentCategoryViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'units', DepartmentUnitViewSet)
router.register(r'officers', DepartmentOfficerViewSet)
router.register(r'contacts', DepartmentContactViewSet)

urlpatterns = router.urls
