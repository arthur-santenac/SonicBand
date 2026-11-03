# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, FormView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import InscriptionForm, InviteForm
from .models import Musicien

class PresentationView(TemplateView):
    template_name = "core/presentation.html"

class CustomLoginView(LoginView):
    template_name = "core/login.html"

class SignupView(CreateView):
    form_class = InscriptionForm
    template_name = "core/signup.html"
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # On sauvegarde l'utilisateur
        user = form.save()
        # On lui crée un profil Musicien vide
        Musicien.objects.create(user=user)
        # On le connecte automatiquement après l'inscription
        login(self.request, user)
        return super().form_valid(form)

# Vue protégée (LoginRequiredMixin) : accessible uniquement si connecté
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

# Vue d'invitation par mail
class InviteView(LoginRequiredMixin, FormView):
    template_name = "core/invite.html"
    form_class = InviteForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        # Envoi de l'email simulé dans la console
        send_mail(
            subject='Invitation à rejoindre Sonic Band',
            message=f"Bonjour ! {self.request.user.username} vous invite à rejoindre son groupe sur Sonic Band.",
            from_email='admin@sonicband.com',
            recipient_list=[email],
        )
        return super().form_valid(form)