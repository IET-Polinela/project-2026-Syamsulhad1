from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Report
        fields = [
            'id',
            'title',
            'category',
            'description',
            'location',
            'is_anonymous',
            'status',
            'reporter',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'status', 'reporter', 'created_at', 'updated_at']

    def get_reporter(self, obj):
        if obj.is_anonymous:
            return "Warga Anonim"
        if obj.reporter:
            return obj.reporter.username
        return "Tidak diketahui"
