from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'category', 'description', 'location', 'status']
        
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Judul Laporan'}),
            'category': forms.Select(), 
            'description': forms.Textarea(attrs={'placeholder': 'Jelaskan detail masalah...', 'rows': 4}),
            'location': forms.TextInput(attrs={'placeholder': 'Lokasi kejadian'}),
            'status': forms.Select(), 
        }