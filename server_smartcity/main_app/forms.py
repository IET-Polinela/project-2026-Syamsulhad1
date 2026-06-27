from django import forms
from .models import CATEGORY_CHOICES, Report


CATEGORY_ALIAS_MAP = {
    'Infrastruktur': 'INFRASTRUCTURE',
    'Infrastruktur & Jalan': 'INFRASTRUCTURE',
    'Keamanan': 'SECURITY',
    'Kesehatan': 'HEALTH',
    'Kebersihan': 'ENVIRONMENT',
    'Lingkungan': 'ENVIRONMENT',
    'Lingkungan & Kebersihan': 'ENVIRONMENT',
    'Fasilitas Umum': 'PUBLIC_FACILITY',
    'Fasilitas Publik': 'PUBLIC_FACILITY',
    'Lainnya': 'ENVIRONMENT',
}


def category_choices_with_aliases():
    return list(CATEGORY_CHOICES) + [
        (label, label)
        for label in CATEGORY_ALIAS_MAP
    ]

class ReportForm(forms.ModelForm):
    category = forms.ChoiceField(choices=category_choices_with_aliases())

    class Meta:
        model = Report
        fields = ['title', 'category', 'description', 'location']
        
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Judul Laporan', 'required': True}),
            'category': forms.Select(attrs={'required': True}), 
            'description': forms.Textarea(attrs={'placeholder': 'Jelaskan detail masalah...', 'rows': 4, 'required': True}),
            'location': forms.TextInput(attrs={'placeholder': 'Lokasi kejadian', 'required': True}),
        }

    def clean_category(self):
        category = self.cleaned_data['category']
        return CATEGORY_ALIAS_MAP.get(category, category)
