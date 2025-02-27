from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView, View, UpdateView
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import logout

from .forms import CustomAuthenticationForm
from .forms import CustomUserCreationForm
from users.models import User
from .utils.send_emails import send_activation_email


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm


class CustomUserCreationView(CreateView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('register')

    def form_valid(self, form):
        with transaction.atomic():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_activation_email(user)
        messages.success(
            self.request,
            ("Votre compte compte a ete cree, consulter "
                "votre boite email pour activer votre compte")
        )
        return redirect(self.success_url)


class ActivationUserView(View):
    login_url = reverse_lazy('login')

    def get(self, request, uid, token):
        id = urlsafe_base64_decode(uid)
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return render(request, 'registration/activation_invalid.html')

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(
                self.request,
                "Votre compte a ete active. Vous pouvez vous connecter "
            )
            return redirect(self.login_url)
        return render(request, 'registration/activation_invalid.html')



class ProfileUserView(ListView):
    template_name = 'registration/user_profile.html'
    model = User


class LogoutView(View):
    login_url = reverse_lazy('login')

    def get(self, request):
        logout(request)
        messages.success(
            self.request,
            "Votre a ete deconnecte"
        )
        return redirect(self.login_url)


class ProfileUsersView(ListView):
    template_name = 'users/user_profile.html'
    model = User

class ProfileUpdateView(UpdateView):
    model = User
    template_name = "users/update.html"


class ProfileUpdateView(UpdateView):
    model = User
    template_name = "registration/update.html"
    fields = ['first_name', 'last_name', 'email', 'profile_photo']
    success_url = reverse_lazy('profile_user') 

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Votre profil a été mis à jour avec succès.")
        return super().form_valid(form)