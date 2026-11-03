# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Une classe de base pour appliquer le style Bulma automatiquement
class BulmaFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Ajoute la classe 'input' de Bulma à chaque champ texte/email/password
            field.widget.attrs['class'] = 'input'

class InscriptionForm(BulmaFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class InviteForm(BulmaFormMixin, forms.Form):
    email = forms.EmailField(
        label="Email du musicien",
        widget=forms.EmailInput(attrs={'placeholder': 'musicien@domaine.com'})
    )