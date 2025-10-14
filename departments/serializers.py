# departments/serializers.py
from rest_framework import serializers
from .models import DepartmentCategory, Department, DepartmentUnit, DepartmentOfficer, DepartmentContact

class DepartmentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentCategory
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    county_name = serializers.CharField(source="county.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Department
        fields = '__all__'

class DepartmentUnitSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = DepartmentUnit
        fields = '__all__'

class DepartmentOfficerSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = DepartmentOfficer
        fields = '__all__'

class DepartmentContactSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = DepartmentContact
        fields = '__all__'
