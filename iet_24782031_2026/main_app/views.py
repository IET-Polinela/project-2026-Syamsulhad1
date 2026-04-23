from django import forms
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView, UpdateView

from .forms import ReportForm
from .models import Report


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
def report_list(request):
    reports = Report.objects.all().order_by('-created_at')

    search_query = request.GET.get('search')
    if search_query:
        reports = reports.filter(title__icontains=search_query) | reports.filter(location__icontains=search_query)

    category_filter = request.GET.get('category')
    if category_filter:
        reports = reports.filter(category=category_filter)

    return render(request, 'main_app/report_list.html', {'reports': reports})

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
        if new_status:
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
