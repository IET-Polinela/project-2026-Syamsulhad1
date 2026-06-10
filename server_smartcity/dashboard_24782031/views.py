from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from main_app.models import CATEGORY_CHOICES, STATUS_CHOICES, Report


def user_is_app_admin(user):
    return user.is_authenticated and getattr(user, 'is_admin', False)


def _choice_statistics(field_name, choices):
    total_reports = Report.objects.count()
    counts = dict(
        Report.objects.values(field_name)
        .annotate(total=Count('id'))
        .values_list(field_name, 'total')
    )

    return [
        {
            'code': code,
            'label': label,
            'total': counts.get(code, 0),
            'percentage': round((counts.get(code, 0) / total_reports) * 100, 1)
            if total_reports
            else 0,
        }
        for code, label in choices
    ]


def _report_summary(report):
    return {
        'id': report.id,
        'title': report.title,
        'category': report.get_category_display(),
        'location': report.location,
        'status_code': report.status,
        'status': report.get_status_display(),
        'created_at': report.created_at.strftime('%d %b %Y %H:%M'),
        'detail_url': reverse('report_detail', kwargs={'pk': report.pk}),
    }


def _latest_reports_by_status(status):
    reports = Report.objects.filter(status=status).order_by('-created_at')[:5]
    return [_report_summary(report) for report in reports]


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        # Only admin can access dashboard
        if not user_is_app_admin(request.user):
            messages.error(request, "Akses ditolak! Hanya admin yang dapat mengakses dashboard.")
            return redirect('report_list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_reports': Report.objects.count(),
            'resolved_reports': Report.objects.filter(status='RESOLVED').count(),
            'in_progress_reports': Report.objects.filter(status='IN_PROGRESS').count(),
            'status_stats': _choice_statistics('status', STATUS_CHOICES),
            'category_stats': _choice_statistics('category', CATEGORY_CHOICES),
        })
        return context


class DashboardStatsView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'status': _choice_statistics('status', STATUS_CHOICES),
            'category': _choice_statistics('category', CATEGORY_CHOICES),
            'total_reports': Report.objects.count(),
            'in_progress_reports': Report.objects.filter(status='IN_PROGRESS').count(),
            'resolved_reports': Report.objects.filter(status='RESOLVED').count(),
            'latest_reported': _latest_reports_by_status('REPORTED'),
            'latest_resolved': _latest_reports_by_status('RESOLVED'),
        })
