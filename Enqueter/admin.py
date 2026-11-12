from django.contrib import admin

from .models import Affectation, Enqueteur, Marche, Produit, Releve


admin.site.site_header = "Administration PrixMarché"
admin.site.site_title = "PrixMarché"
admin.site.index_title = "Gestion des données enregistrées"


@admin.register(Marche)
class MarcheAdmin(admin.ModelAdmin):
    list_display = ("code_marche", "nom_marche", "ville")
    search_fields = ("code_marche", "nom_marche", "ville")


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ("code_produit", "libelle", "unite")
    list_filter = ("unite",)
    search_fields = ("code_produit", "libelle")


@admin.register(Enqueteur)
class EnqueteurAdmin(admin.ModelAdmin):
    list_display = ("matricule", "nom_enq", "telephone", "user")
    search_fields = ("matricule", "nom_enq", "telephone", "user__username")


@admin.register(Affectation)
class AffectationAdmin(admin.ModelAdmin):
    list_display = ("enqueteur", "marche", "date_debut")
    list_filter = ("marche",)
    search_fields = ("enqueteur__matricule", "enqueteur__nom_enq", "marche__nom_marche")


@admin.register(Releve)
class ReleveAdmin(admin.ModelAdmin):
    list_display = ("num_releve", "date_releve", "produit", "marche", "enqueteur", "prix")
    list_filter = ("date_releve", "marche", "produit")
    search_fields = (
        "produit__libelle",
        "marche__nom_marche",
        "enqueteur__matricule",
        "enqueteur__nom_enq",
    )
