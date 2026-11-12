from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Marche(models.Model):
    code_marche = models.CharField(max_length=10, primary_key=True)
    nom_marche = models.CharField(max_length=80)
    ville = models.CharField(max_length=60)

    class Meta:
        verbose_name = "marché"
        verbose_name_plural = "Marchés"

    def __str__(self):
        return f"{self.nom_marche} ({self.ville})"


class Produit(models.Model):
    class Unite(models.TextChoices):
        TAS = "tas", "Tas"
        REGIME = "regime", "Régime"
        KG = "kg", "Kilogramme"

    code_produit = models.CharField(max_length=6, primary_key=True)
    libelle = models.CharField(max_length=60)
    unite = models.CharField(max_length=6, choices=Unite.choices)

    class Meta:
        verbose_name = "produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.libelle


class Enqueteur(models.Model):
    matricule = models.CharField(max_length=8, primary_key=True)
    nom_enq = models.CharField(max_length=60)
    telephone = models.CharField(max_length=15, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enqueteur",
    )

    class Meta:
        verbose_name = "enquêteur"
        verbose_name_plural = "Enquêteurs"

    def __str__(self):
        return f"{self.matricule} - {self.nom_enq}"


class Affectation(models.Model):
    enqueteur = models.ForeignKey(Enqueteur, on_delete=models.PROTECT)
    marche = models.ForeignKey(Marche, on_delete=models.PROTECT)
    date_debut = models.DateField()

    class Meta:
        verbose_name = "affectation"
        verbose_name_plural = "Affectations"
        constraints = [
            models.UniqueConstraint(
                fields=("enqueteur", "marche"),
                name="affectation_unique",
            )
        ]

    def __str__(self):
        return f"{self.enqueteur} - {self.marche}"


class Releve(models.Model):
    num_releve = models.AutoField(primary_key=True)
    date_releve = models.DateField()
    prix = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name="releves")
    marche = models.ForeignKey(Marche, on_delete=models.PROTECT, related_name="releves")
    enqueteur = models.ForeignKey(
        Enqueteur, on_delete=models.PROTECT, related_name="releves"
    )

    class Meta:
        verbose_name = "relevé"
        verbose_name_plural = "Relevés"

    def __str__(self):
        return f"{self.produit} - {self.marche} : {self.prix} FCFA"
