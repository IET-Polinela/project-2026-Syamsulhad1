from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Report
from .serializers import ReportSerializer


def user_is_app_admin(user):
    return user.is_authenticated and getattr(user, 'is_admin', False)


class ReportViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportSerializer

    def get_queryset(self):
        reports = Report.objects.select_related('reporter').order_by('-created_at')
        user = self.request.user

        if user_is_app_admin(user):
            return reports.exclude(status='DRAFT')

        return reports.filter(reporter=user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user, status='DRAFT')

    def perform_update(self, serializer):
        report = serializer.instance
        if not user_is_app_admin(self.request.user) and report.status != 'DRAFT':
            raise PermissionDenied("Citizen hanya dapat mengubah laporan yang masih draft.")
        serializer.save(reporter=report.reporter, status=report.status)

    def perform_destroy(self, instance):
        if not user_is_app_admin(self.request.user) and instance.status != 'DRAFT':
            raise PermissionDenied("Citizen hanya dapat menghapus laporan yang masih draft.")
        instance.delete()

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        report = self.get_object()

        if report.status != 'DRAFT':
            raise ValidationError("Hanya laporan draft yang dapat dikirim.")

        report.status = 'REPORTED'
        report.save(update_fields=['status', 'updated_at'])

        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)
