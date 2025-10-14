from rest_framework import serializers
from .models import County, SubCounty, Constituency, Ward


class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = ['id', 'name', 'code']


class ConstituencySerializer(serializers.ModelSerializer):
    wards = WardSerializer(many=True, read_only=True)

    class Meta:
        model = Constituency
        fields = ['id', 'name', 'code', 'wards']


class SubCountySerializer(serializers.ModelSerializer):
    constituencies = ConstituencySerializer(many=True, read_only=True)

    class Meta:
        model = SubCounty
        fields = ['id', 'name', 'code',  'constituencies']


class CountySerializer(serializers.ModelSerializer):
    county_id = serializers.IntegerField(source='code')
    county_name = serializers.CharField(source='name')

    class Meta:
        model = County
        fields = ['county_id', 'county_name']