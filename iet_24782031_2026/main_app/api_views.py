from django.db.models import Q

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Report
from .serializers import ReportSerializer


def user_is_app_admin(user):
    return user.is_authenticated and getattr(user, 'is_admin', False)


class ReportViewSet(viewsets.ModelViewSet):

    serializer_class = ReportSerializer

    def get_permissions(self):

        if self.action in [
            'list',
            'retrieve',
            'create',
            'update',
            'partial_update',
            'destroy',
            'submit'
        ]:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()

    def get_queryset(self):

        reports = Report.objects.select_related(
            'reporter'
        ).order_by('-created_at')

        user = self.request.user

        # Admin hanya melihat laporan non-draft
        if user_is_app_admin(user):
            return reports.exclude(status='DRAFT')

        # Citizen:
        # - melihat semua non-draft
        # - melihat draft miliknya sendiri
        return reports.filter(
            Q(reporter=user) | ~Q(status='DRAFT')
        )

    def perform_create(self, serializer):

        # Admin tidak boleh membuat laporan
        if user_is_app_admin(self.request.user):
            raise PermissionDenied(
                "Admin tidak dapat membuat laporan."
            )

        serializer.save(
            reporter=self.request.user,
            status='DRAFT'
        )

    def perform_update(self, serializer):

        report = serializer.instance
        user = self.request.user

        # ADMIN:
        # hanya boleh mengubah status
        if user_is_app_admin(user):

            allowed_status = [
                'REPORTED',
                'VERIFIED',
                'IN_PROGRESS',
                'RESOLVED'
            ]

            new_status = self.request.data.get('status')

            if new_status not in allowed_status:
                raise ValidationError(
                    "Status tidak valid."
                )

            serializer.save(
                reporter=report.reporter,
                title=report.title,
                category=report.category,
                description=report.description,
                location=report.location,
                status=new_status
            )

            return

        # CITIZEN:
        # hanya boleh edit draft miliknya sendiri
        if (
            report.reporter != user
            or report.status != 'DRAFT'
        ):
            raise PermissionDenied(
                "Citizen hanya dapat mengubah draft miliknya sendiri."
            )

        serializer.save(
            reporter=report.reporter,
            status=report.status
        )

    def perform_destroy(self, instance):

        user = self.request.user

        # Admin tidak boleh delete laporan
        if user_is_app_admin(user):
            raise PermissionDenied(
                "Admin tidak dapat menghapus laporan."
            )

        # Citizen hanya boleh delete draft sendiri
        if (
            instance.reporter != user
            or instance.status != 'DRAFT'
        ):
            raise PermissionDenied(
                "Citizen hanya dapat menghapus draft miliknya sendiri."
            )

        instance.delete()

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):

        report = self.get_object()

        # Hanya pemilik draft
        if report.reporter != request.user:
            raise PermissionDenied(
                "Anda bukan pemilik laporan ini."
            )

        # Hanya draft yang bisa disubmit
        if report.status != 'DRAFT':
            raise ValidationError(
                "Hanya laporan draft yang dapat dikirim."
            )

        report.status = 'REPORTED'

        report.save(update_fields=[
            'status',
            'updated_at'
        ])

        serializer = self.get_serializer(report)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )