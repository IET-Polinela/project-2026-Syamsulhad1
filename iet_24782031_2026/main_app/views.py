from django import forms 
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Report, STATUS_CHOICES
from .forms import ReportForm

# 1. HomeView (Ini yang menyebabkan error AttributeError: HomeView)
class HomeView(TemplateView):
    template_name = 'main_app/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_reports'] = Report.objects.count()
        return context

# 2. report_list
def report_list(request):
    # Ambil data awal
    reports = Report.objects.all().order_by('-created_at')

    # Logika Pencarian
    search_query = request.GET.get('search')
    if search_query:
        reports = reports.filter(title__icontains=search_query) | reports.filter(location__icontains=search_query)

    # Logika Filter Kategori
    category_filter = request.GET.get('category')
    if category_filter:
        reports = reports.filter(category=category_filter)

    return render(request, 'main_app/report_list.html', {'reports': reports})

# 3. ReportDetailView
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'

# 4. ReportCreateView
class ReportCreateView(CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')
    
    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        # SAAT CREATE: Sembunyikan pilihan status agar tidak bisa dimanipulasi
        # Status akan otomatis mengikuti default dari model (REPORTED)
        if 'status' in form.fields:
            form.fields['status'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        # Memastikan status adalah REPORTED saat pertama kali dibuat
        form.instance.status = 'REPORTED'
        messages.success(self.request, "Laporan berhasil ditambahkan!")
        return super().form_valid(form)

# 5. ReportUpdateView (Sistem Anti-Rollback)
class ReportUpdateView(UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        # Cek status laporan sebelum allow edit
        self.object = self.get_object()
        if self.object.status == 'RESOLVED':
            messages.error(request, "Laporan yang sudah selesai tidak dapat diedit. Silakan lihat detail laporan untuk informasi lebih lanjut.")
            return redirect('report_detail', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        current_status = self.object.status
        
        # Ambil kunci status dari model
        status_keys = [choice[0] for choice in STATUS_CHOICES]
        current_index = status_keys.index(current_status)
        
        # ATURAN WORKFLOW:
        # Index 0: REPORTED, 1: VERIFIED, 2: IN_PROGRESS, 3: RESOLVED
        if current_status == 'RESOLVED':
            # Jika sudah Resolved, tidak ada pilihan perubahan (readonly)
            allowed_choices = [(current_status, 'Resolved')]
        else:
            # Ambil status saat ini dan TEPAT satu status setelahnya
            allowed_choices = [STATUS_CHOICES[current_index], STATUS_CHOICES[current_index + 1]]
        
        form.fields['status'].choices = allowed_choices
        return form

    def form_valid(self, form):
        messages.info(self.request, "Laporan berhasil diperbarui.")
        return super().form_valid(form)
    
# 6. ReportDeleteView
class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/report_delete.html'
    success_url = reverse_lazy('report_list')
    
    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Laporan telah dihapus.")
        return super().delete(request, *args, **kwargs)

# 7. ReportUpdateStatusView (Ini yang menyebabkan error AttributeError: ReportUpdateStatusView)
class ReportUpdateStatusView(View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')
        if new_status:
            report.status = new_status
            report.save()
            messages.success(request, "Status berhasil diperbarui!")
        return redirect('report_list')

# Function view untuk update status via GET
def update_status(request, pk, new_status):
    report = get_object_or_404(Report, pk=pk)
    # Validasi workflow: hanya allow transisi yang valid
    valid_transitions = {
        'REPORTED': ['VERIFIED'],
        'VERIFIED': ['IN_PROGRESS'],
        'IN_PROGRESS': ['RESOLVED'],
        'RESOLVED': []  # Tidak bisa diubah lagi
    }
    if new_status in valid_transitions.get(report.status, []):
        report.status = new_status
        report.save()
        messages.success(request, f"Status laporan diperbarui menjadi {report.get_status_display()}.")
    else:
        messages.error(request, "Transisi status tidak valid.")
    return redirect('report_list')