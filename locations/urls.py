from rest_framework.routers import DefaultRouter
from .views import CountyViewSet, SubCountyViewSet, ConstituencyViewSet, WardViewSet

router = DefaultRouter()
router.register(r'counties', CountyViewSet, basename='counties')
router.register(r'subcounties', SubCountyViewSet)
router.register(r'constituencies', ConstituencyViewSet)
router.register(r'wards', WardViewSet)

urlpatterns = router.urls
