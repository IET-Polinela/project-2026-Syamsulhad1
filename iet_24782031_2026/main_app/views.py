from django.shortcuts import redirect, render, get_object_or_404
from .models import Report
from .forms import ReportForm


def home(request):
    # Alih-alih hanya merender halaman statis, 
    # Anda bisa menampilkan jumlah laporan terbaru di halaman depan
    reports_count = Report.objects.count()
    return render(request, 'main_app/home.html', {'total_reports': reports_count})

def report_list(request):
    reports = Report.objects.all()
    return render(request, 'main_app/report_list.html', {'reports': reports})

def report_create(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('report_list')
    else:
        form = ReportForm()
    return render(request, 'main_app/report_form.html', {'form': form})

def report_update(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            return redirect('report_list')
    else:
        form = ReportForm(instance=report)
    return render(request, 'main_app/report_form.html', {'form': form})

def report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        report.delete()
        return redirect('report_list')
    return render(request, 'main_app/report_delete.html', {'report': report})