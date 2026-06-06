from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
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
            'is_owner',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'status',
            'reporter',
            'is_owner',
            'created_at',
            'updated_at',
        ]

    def get_reporter(self, obj):
        request = self.context.get('request')
        is_feed_tab = (
            request
            and request.query_params.get('tab') == 'feed'
        )

        if obj.is_anonymous or is_feed_tab:
            return "Warga Anonim"

        if obj.reporter:
            return obj.reporter.username

        return "Tidak diketahui"

    def get_is_owner(self, obj):
        request = self.context.get('request')

        if request and request.user and request.user.is_authenticated:
            return obj.reporter_id == request.user.id

        return False
