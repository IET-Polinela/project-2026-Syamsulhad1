from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'category', 'description', 'location']
        
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Judul Laporan', 'required': True}),
            'category': forms.Select(attrs={'required': True}), 
            'description': forms.Textarea(attrs={'placeholder': 'Jelaskan detail masalah...', 'rows': 4, 'required': True}),
            'location': forms.TextInput(attrs={'placeholder': 'Lokasi kejadian', 'required': True}),
        }
