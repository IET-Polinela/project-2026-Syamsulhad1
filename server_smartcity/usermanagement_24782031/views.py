from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import RegisterForm, StyledAuthenticationForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_admin = False
            user.is_member = True
            user.save()
            messages.success(request, "Registrasi berhasil! Silakan login.")
            return redirect('login')
        else:
            # FIX: tampilkan pesan error jika form tidak valid
            messages.error(request, "Registrasi gagal! Periksa kembali data yang diisi.")
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


# LOGIN CUSTOM
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = StyledAuthenticationForm

    def get_success_url(self):
        return '/'

    def form_valid(self, form):
        messages.success(self.request, "Login berhasil! Selamat datang.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Login gagal! Username atau password salah.")
        return super().form_invalid(form)


# LOGOUT CUSTOM
class CustomLogoutView(LogoutView):
    next_page = '/'

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Berhasil logout! Sampai jumpa.")
        return super().dispatch(request, *args, **kwargs)
