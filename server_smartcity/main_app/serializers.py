from rest_framework import serializers
from .models import CATEGORY_CHOICES, Report


CATEGORY_ALIAS_MAP = {
    'Infrastruktur': 'INFRASTRUCTURE',
    'Infrastruktur & Jalan': 'INFRASTRUCTURE',
    'Keamanan': 'SECURITY',
    'Kesehatan': 'HEALTH',
    'Kebersihan': 'ENVIRONMENT',
    'Lingkungan': 'ENVIRONMENT',
    'Lingkungan & Kebersihan': 'ENVIRONMENT',
    'Fasilitas Umum': 'PUBLIC_FACILITY',
    'Fasilitas Publik': 'PUBLIC_FACILITY',
    'Lainnya': 'ENVIRONMENT',
}


class ReportSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    reporter = serializers.SerializerMethodField()
    reporter_name = serializers.SerializerMethodField()
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
            'reporter_name',
            'is_owner',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'status',
            'reporter',
            'reporter_name',
            'is_owner',
            'created_at',
            'updated_at',
        ]

    def validate_category(self, value):
        valid_categories = {code for code, _label in CATEGORY_CHOICES}
        normalized = CATEGORY_ALIAS_MAP.get(value, value)

        if normalized not in valid_categories:
            raise serializers.ValidationError("Kategori tidak valid.")

        return normalized

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

    def get_reporter_name(self, obj):
        request = self.context.get('request')

        if (
            request
            and request.user
            and request.user.is_authenticated
            and obj.reporter_id == request.user.id
            and obj.reporter
        ):
            return obj.reporter.username

        return "Warga Anonim"

    def get_is_owner(self, obj):
        request = self.context.get('request')

        if request and request.user and request.user.is_authenticated:
            return obj.reporter_id == request.user.id

        return False
