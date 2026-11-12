import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Enqueter", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.DeleteModel(name="Releve"),
        migrations.DeleteModel(name="Marche"),
        migrations.DeleteModel(name="Produit"),
        migrations.DeleteModel(name="Enqueteur"),
        migrations.DeleteModel(name="Region"),
        migrations.CreateModel(
            name="Marche",
            fields=[
                (
                    "code_marche",
                    models.CharField(max_length=10, primary_key=True, serialize=False),
                ),
                ("nom_marche", models.CharField(max_length=80)),
                ("ville", models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name="Produit",
            fields=[
                (
                    "code_produit",
                    models.CharField(max_length=6, primary_key=True, serialize=False),
                ),
                ("libelle", models.CharField(max_length=60)),
                (
                    "unite",
                    models.CharField(
                        choices=[
                            ("tas", "Tas"),
                            ("regime", "Régime"),
                            ("kg", "Kilogramme"),
                        ],
                        max_length=6,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Enqueteur",
            fields=[
                (
                    "matricule",
                    models.CharField(max_length=8, primary_key=True, serialize=False),
                ),
                ("nom_enq", models.CharField(max_length=60)),
                ("telephone", models.CharField(blank=True, max_length=15)),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="enqueteur",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Affectation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_debut", models.DateField()),
                (
                    "enqueteur",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="Enqueter.enqueteur",
                    ),
                ),
                (
                    "marche",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="Enqueter.marche",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("enqueteur", "marche"),
                        name="affectation_unique",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="Releve",
            fields=[
                (
                    "num_releve",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("date_releve", models.DateField()),
                (
                    "prix",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "produit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="releves",
                        to="Enqueter.produit",
                    ),
                ),
                (
                    "marche",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="releves",
                        to="Enqueter.marche",
                    ),
                ),
                (
                    "enqueteur",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="releves",
                        to="Enqueter.enqueteur",
                    ),
                ),
            ],
        ),
    ]
