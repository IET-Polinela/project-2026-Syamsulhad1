from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class StyledAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan username',
                'autocomplete': 'username',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan password',
                'autocomplete': 'current-password',
            }
        )
    )


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Pilih username',
                    'autocomplete': 'username',
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'email@contoh.com',
                    'autocomplete': 'email',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Masukkan password',
                'autocomplete': 'new-password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Ulangi password',
                'autocomplete': 'new-password',
            }
        )
