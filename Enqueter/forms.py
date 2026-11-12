from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Affectation, Enqueteur, Marche, Produit, Releve


class RegistrationForm(UserCreationForm):
    matricule = forms.CharField(max_length=8, label="Matricule")
    nom_enq = forms.CharField(max_length=60, label="Nom de l’enquêteur")
    telephone = forms.CharField(max_length=15, required=False, label="Téléphone")

    class Meta:
        model = get_user_model()
        fields = ("username", "matricule", "nom_enq", "telephone")

    def clean_matricule(self):
        matricule = self.cleaned_data["matricule"]
        if Enqueteur.objects.filter(matricule=matricule).exists():
            raise forms.ValidationError("Ce matricule est déjà utilisé.")
        return matricule

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Enqueteur.objects.create(
                matricule=self.cleaned_data["matricule"],
                nom_enq=self.cleaned_data["nom_enq"],
                telephone=self.cleaned_data["telephone"],
                user=user,
            )
        return user


class MarcheForm(forms.ModelForm):
    class Meta:
        model = Marche
        fields = ("code_marche", "nom_marche", "ville")
        labels = {
            "code_marche": "Code du marché",
            "nom_marche": "Nom du marché",
            "ville": "Ville",
        }


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ("code_produit", "libelle", "unite")
        labels = {
            "code_produit": "Code du produit",
            "libelle": "Libellé",
            "unite": "Unité",
        }


class EnqueteurForm(forms.ModelForm):
    class Meta:
        model = Enqueteur
        fields = ("matricule", "nom_enq", "telephone")
        labels = {
            "matricule": "Matricule",
            "nom_enq": "Nom de l’enquêteur",
            "telephone": "Téléphone",
        }


class AffectationForm(forms.ModelForm):
    class Meta:
        model = Affectation
        fields = ("enqueteur", "marche", "date_debut")
        labels = {
            "enqueteur": "Enquêteur",
            "marche": "Marché",
            "date_debut": "Date de début",
        }
        widgets = {"date_debut": forms.DateInput(attrs={"type": "date"})}


class ReleveForm(forms.ModelForm):
    class Meta:
        model = Releve
        fields = ("date_releve", "prix", "produit", "marche")
        labels = {
            "date_releve": "Date du relevé",
            "prix": "Prix (FCFA)",
            "produit": "Produit",
            "marche": "Marché",
        }
        widgets = {
            "date_releve": forms.DateInput(attrs={"type": "date"}),
            "prix": forms.NumberInput(attrs={"min": 1, "step": 1}),
        }
