# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.PresentationView.as_view(), name="presentation"),
    path("connexion/", views.CustomLoginView.as_view(), name="login"),
    path("deconnexion/", views.LogoutView.as_view(), name="logout"),
    path("inscription/", views.SignupView.as_view(), name="signup"),
    path("mon-compte/", views.DashboardView.as_view(), name="dashboard"),
    path("inviter/", views.InviteView.as_view(), name="invite"),
]