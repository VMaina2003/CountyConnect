from rest_framework import viewsets
from .models import County, SubCounty, Constituency, Ward
from .serializers import CountySerializer, SubCountySerializer, ConstituencySerializer, WardSerializer



class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list of all counties.
    """
    queryset = County.objects.all().order_by('code')
    serializer_class = CountySerializer

class SubCountyViewSet(viewsets.ModelViewSet):
    queryset = SubCounty.objects.all()
    serializer_class = SubCountySerializer


class ConstituencyViewSet(viewsets.ModelViewSet):
    queryset = Constituency.objects.all()
    serializer_class = ConstituencySerializer


class WardViewSet(viewsets.ModelViewSet):
    queryset = Ward.objects.all()
    serializer_class = WardSerializer
