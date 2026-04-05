from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'description', 'location']
        
        # Opsional: Menambahkan widget agar tampilan form lebih rapi
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Judul Laporan'}),
            'description': forms.Textarea(attrs={'placeholder': 'Jelaskan detail masalah...', 'rows': 4}),
            'location': forms.TextInput(attrs={'placeholder': 'Lokasi kejadian'}),
        }