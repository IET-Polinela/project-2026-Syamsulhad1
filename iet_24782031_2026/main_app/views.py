from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Report
from .forms import ReportForm

# View untuk Halaman Home (Menampilkan statistik singkat)
class HomeView(TemplateView):
    template_name = 'main_app/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_reports'] = Report.objects.count()
        return context

# ListView: Menampilkan daftar laporan
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports' # Agar di template tetap menggunakan variabel 'reports'

# DetailView: Menampilkan detail laporan (Opsional, jika dibutuhkan)
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'

# CreateView: Membuat laporan baru
class ReportCreateView(CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')

# UpdateView: Mengedit data laporan
class ReportUpdateView(UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')

# DeleteView: Menghapus laporan
class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/report_delete.html'
    success_url = reverse_lazy('report_list')

# Implementasi Workflow Dasar: Update Status Saja
class ReportUpdateStatusView(View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')
        if new_status:
            report.status = new_status
            report.save()
        return redirect('report_list')