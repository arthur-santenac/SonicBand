# core/models.py
from django.db import models
from django.contrib.auth.models import User

class Groupe(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Musicien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    groupe = models.ForeignKey(Groupe, on_delete=models.SET_NULL, null=True, blank=True)
    est_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username