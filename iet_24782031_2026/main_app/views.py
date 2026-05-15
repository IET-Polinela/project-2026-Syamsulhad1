from django import forms
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView, UpdateView

from .forms import ReportForm
from .models import CATEGORY_CHOICES, Report


def user_is_app_admin(user):
    return user.is_authenticated and getattr(user, 'is_admin', False)


def redirect_non_admin(request):
    messages.error(request, "Akses ditolak! Hanya admin yang bisa melakukan aksi ini.")
    return redirect('report_list')

class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not user_is_app_admin(request.user):
            return redirect_non_admin(request)
        return super().dispatch(request, *args, **kwargs)

# 1. HomeView
class HomeView(TemplateView):
    template_name = 'main_app/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_reports'] = Report.objects.count()
        return context

# 2. report_list
def get_filtered_reports(request):
    reports = Report.objects.all().order_by('-created_at')
    if user_is_app_admin(request.user):
        reports = reports.exclude(status='DRAFT')
    elif request.user.is_authenticated:
        reports = reports.filter(Q(reporter=request.user) | ~Q(status='DRAFT'))
    else:
        reports = reports.exclude(status='DRAFT')

    search_query = request.GET.get('search')
    if search_query:
        reports = reports.filter(
            Q(title__icontains=search_query)
            | Q(location__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    category_filter = request.GET.get('category')
    if category_filter:
        reports = reports.filter(category=category_filter)

    return reports


def serialize_report(report):
    return {
        'id': report.id,
        'title': report.title,
        'category': report.category,
        'category_label': report.get_category_display(),
        'description': report.description,
        'location': report.location,
        'is_anonymous': report.is_anonymous,
        'status': report.status,
        'status_label': report.get_status_display(),
        'created_at': report.created_at.strftime('%d %b %Y %H:%M'),
        'detail_url': reverse('report_detail', kwargs={'pk': report.pk}),
        'edit_url': reverse('report_update', kwargs={'pk': report.pk}),
        'delete_url': reverse('report_delete', kwargs={'pk': report.pk}),
        'verify_url': reverse('update_status', kwargs={'pk': report.pk, 'new_status': 'VERIFIED'}),
        'process_url': reverse('update_status', kwargs={'pk': report.pk, 'new_status': 'IN_PROGRESS'}),
        'resolve_url': reverse('update_status', kwargs={'pk': report.pk, 'new_status': 'RESOLVED'}),
    }


def report_list(request):
    return render(
        request,
        'main_app/report_list.html',
        {
            'reports': get_filtered_reports(request),
            'category_choices': CATEGORY_CHOICES,
        },
    )


class ReportListJsonView(View):
    def get(self, request, *args, **kwargs):
        reports = get_filtered_reports(request)
        return JsonResponse({
            'reports': [serialize_report(report) for report in reports],
            'total': reports.count(),
            'is_admin': user_is_app_admin(request.user),
        })


class ReportDetailJsonView(View):
    def get(self, request, pk, *args, **kwargs):
        report = get_object_or_404(Report, pk=pk)
        return JsonResponse({'report': serialize_report(report)})

# 3. ReportDetailView
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'

# 4. ReportCreateView
class ReportCreateView(AdminRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        form.instance.status = 'REPORTED'
        messages.success(self.request, "Laporan berhasil dibuat!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Laporan gagal dibuat. Periksa kembali data yang diisi.")
        return super().form_invalid(form)

# 5. ReportUpdateView (Sistem Anti-Rollback)
class ReportUpdateView(AdminRequiredMixin, UpdateView):
    model = Report
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status == 'RESOLVED':
            messages.error(request, "Laporan yang sudah selesai tidak dapat diedit. Silakan lihat detail laporan untuk informasi lebih lanjut.")
            return redirect('report_detail', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        class UpdateReportForm(forms.ModelForm):
            class Meta:
                model = Report
                fields = ['title', 'category', 'description', 'location']
                widgets = {
                    'title': forms.TextInput(attrs={'placeholder': 'Judul Laporan'}),
                    'category': forms.Select(), 
                    'description': forms.Textarea(attrs={'placeholder': 'Jelaskan detail masalah...', 'rows': 4}),
                    'location': forms.TextInput(attrs={'placeholder': 'Lokasi kejadian'}),
                }
        return UpdateReportForm

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil diperbarui!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Gagal memperbarui laporan. Periksa kembali data yang diisi.")
        return super().form_invalid(form)

# 6. ReportDeleteView
class ReportDeleteView(AdminRequiredMixin, DeleteView):
    model = Report
    template_name = 'main_app/report_delete.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil dihapus.")
        return super().form_valid(form)

# 7. ReportUpdateStatusView
class ReportUpdateStatusView(AdminRequiredMixin, View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')
        valid_transitions = {
            'REPORTED': ['VERIFIED'],
            'VERIFIED': ['IN_PROGRESS'],
            'IN_PROGRESS': ['RESOLVED'],
            'RESOLVED': []
        }
        if new_status in valid_transitions.get(report.status, []):
            report.status = new_status
            report.save()
            messages.success(request, "Status berhasil diperbarui!")
        else:
            messages.error(request, "Status tidak valid.")
        return redirect('report_list')

# Function view untuk update status via GET
def update_status(request, pk, new_status):
    if not user_is_app_admin(request.user):
        return redirect_non_admin(request)

    report = get_object_or_404(Report, pk=pk)
    valid_transitions = {
        'REPORTED': ['VERIFIED'],
        'VERIFIED': ['IN_PROGRESS'],
        'IN_PROGRESS': ['RESOLVED'],
        'RESOLVED': []
    }
    if new_status in valid_transitions.get(report.status, []):
        report.status = new_status
        report.save()
        messages.success(request, f"Status laporan diperbarui menjadi {report.get_status_display()}.")
    else:
        messages.error(request, "Transisi status tidak valid.")
    return redirect('report_list')
