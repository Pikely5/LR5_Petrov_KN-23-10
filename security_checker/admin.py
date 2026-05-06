from django.contrib import admin
from .models import TestProtocol, SecurityFinding, TestDataset, SecurityCheckRule

@admin.register(TestProtocol)
class TestProtocolAdmin(admin.ModelAdmin):
    list_display = ['protocol_number', 'test_date', 'tester_name', 'status', 'risk_score']
    list_filter = ['status', 'test_date']
    search_fields = ['protocol_number']

@admin.register(SecurityFinding)
class SecurityFindingAdmin(admin.ModelAdmin):
    list_display = ['resource_name', 'severity', 'responsibility', 'detection_time', 'resolved']
    list_filter = ['severity', 'responsibility', 'resolved']
    search_fields = ['resource_name']

@admin.register(TestDataset)
class TestDatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'dataset_type', 'is_active', 'created_at']
    list_filter = ['dataset_type', 'is_active']

@admin.register(SecurityCheckRule)
class SecurityCheckRuleAdmin(admin.ModelAdmin):
    list_display = ['rule_id', 'name', 'category', 'severity', 'is_enabled', 'priority']
    list_filter = ['category', 'severity', 'is_enabled']
    list_editable = ['is_enabled']