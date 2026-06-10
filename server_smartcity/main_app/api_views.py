from django.db.models import Q

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Report
from .serializers import ReportSerializer


def user_is_app_admin(user):
    return user.is_authenticated and getattr(user, 'is_admin', False)


class ReportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    pagination_class = ReportPagination

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
        user = self.request.user
        tab = self.request.query_params.get('tab', None)

        queryset = Report.objects.select_related(
            'reporter'
        ).order_by('-updated_at')

        # Admin hanya melihat semua laporan non-draft
        if user_is_app_admin(user):
            return queryset.exclude(status='DRAFT')

        # Tab Laporan Saya
        # Menampilkan semua laporan milik user login
        if tab == 'my_reports':
            return queryset.filter(reporter=user)

        # Tab Feed Kota
        # Menampilkan laporan warga lain yang bukan DRAFT
        if tab == 'feed':
            return queryset.filter(
                ~Q(reporter=user),
                ~Q(status='DRAFT')
            )

        # Default:
        # Menampilkan laporan non-draft + draft milik user
        return queryset.filter(
            Q(reporter=user) | ~Q(status='DRAFT')
        )

    def perform_create(self, serializer):
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

        # Admin hanya boleh mengubah status laporan non-draft
        if user_is_app_admin(user):
            allowed_status = [
                'REPORTED',
                'VERIFIED',
                'IN_PROGRESS',
                'RESOLVED'
            ]

            new_status = self.request.data.get('status')

            if report.status == 'DRAFT':
                raise PermissionDenied(
                    "Admin tidak dapat mengubah laporan yang masih DRAFT."
                )

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
                is_anonymous=report.is_anonymous,
                status=new_status
            )

            return

        # Citizen hanya boleh edit draft miliknya sendiri
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

        # Admin tidak boleh menghapus laporan
        if user_is_app_admin(user):
            raise PermissionDenied(
                "Admin tidak dapat menghapus laporan."
            )

        # Citizen hanya boleh hapus draft sendiri
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

        if report.reporter != request.user:
            raise PermissionDenied(
                "Anda bukan pemilik laporan ini."
            )

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