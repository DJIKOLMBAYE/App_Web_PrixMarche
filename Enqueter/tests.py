from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Affectation, Enqueteur, Marche, Produit, Releve


class AdminAccessTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="admin",
            password="Admin-password-123!",
        )

    def test_superuser_can_manage_all_registered_data(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gestion des données enregistrées")
        admin_routes = (
            "admin:Enqueter_marche_changelist",
            "admin:Enqueter_produit_changelist",
            "admin:Enqueter_enqueteur_changelist",
            "admin:Enqueter_affectation_changelist",
            "admin:Enqueter_releve_changelist",
        )
        for route_name in admin_routes:
            with self.subTest(route=route_name):
                self.assertContains(response, reverse(route_name), status_code=200)

        dashboard = self.client.get(reverse("home"))
        self.assertContains(dashboard, reverse("admin:index"))

    def test_regular_user_cannot_access_admin(self):
        user = get_user_model().objects.create_user(
            username="regular",
            password="Regular-password-123!",
        )
        self.client.force_login(user)

        dashboard = self.client.get(reverse("home"))
        self.assertNotContains(dashboard, reverse("admin:index"))

        response = self.client.get(reverse("admin:index"))

        self.assertRedirects(
            response,
            f"{reverse('admin:login')}?next={reverse('admin:index')}",
        )


class AuthenticationTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "Test-password-123!"
        get_user_model().objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_home_redirects_anonymous_users_to_login(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

    def test_login_opens_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.username, "password": self.password},
        )

        self.assertRedirects(response, reverse("home"))
        dashboard = self.client.get(reverse("home"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, self.username)
        self.assertContains(dashboard, "Affectations")
        self.assertNotContains(dashboard, reverse("admin:index"))

    def test_login_rejects_an_incorrect_password(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.username, "password": "incorrect"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nom d’utilisateur ou mot de passe incorrect.")

    def test_registration_creates_account_and_linked_enqueteur(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "matricule": "ENQ002",
                "nom_enq": "Nouvel enquêteur",
                "telephone": "690000000",
                "password1": "Strong-password-473!",
                "password2": "Strong-password-473!",
            },
        )

        self.assertRedirects(response, reverse("home"))
        user = get_user_model().objects.get(username="newuser")
        self.assertTrue(user.check_password("Strong-password-473!"))
        self.assertNotEqual(user.password, "Strong-password-473!")
        self.assertEqual(user.enqueteur.matricule, "ENQ002")
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_registration_rejects_duplicate_enqueteur_matricule(self):
        Enqueteur.objects.create(matricule="ENQ001", nom_enq="Déjà utilisé")

        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "matricule": "ENQ001",
                "nom_enq": "Nouvel enquêteur",
                "password1": "Strong-password-473!",
                "password2": "Strong-password-473!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ce matricule est déjà utilisé.")
        self.assertFalse(get_user_model().objects.filter(username="newuser").exists())

    def test_logout_returns_to_login(self):
        self.client.force_login(get_user_model().objects.get(username=self.username))

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertRedirects(
            self.client.get(reverse("home")),
            f"{reverse('login')}?next={reverse('home')}",
        )


class ReferenceCrudTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="manager",
            password="Test-password-123!",
        )
        self.client.force_login(self.user)

    def test_reference_pages_are_login_protected(self):
        paths = (
            "marches",
            "produits",
            "enqueteurs",
            "affectations",
            "releve_list",
        )
        self.client.logout()

        for name in paths:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertRedirects(
                    response,
                    f"{reverse('login')}?next={reverse(name)}",
                )

    def test_product_can_be_created_updated_and_deleted(self):
        response = self.client.post(
            reverse("produit_create"),
            {"code_produit": "MAN", "libelle": "Manioc", "unite": Produit.Unite.KG},
        )
        self.assertRedirects(response, reverse("produits"))
        produit = Produit.objects.get(pk="MAN")

        response = self.client.post(
            reverse("produit_update", args=[produit.pk]),
            {"code_produit": "MAN", "libelle": "Manioc frais", "unite": Produit.Unite.KG},
        )
        self.assertRedirects(response, reverse("produits"))
        produit.refresh_from_db()
        self.assertEqual(produit.libelle, "Manioc frais")

        response = self.client.get(reverse("produit_delete", args=[produit.pk]))
        self.assertContains(response, "Confirmer la suppression")
        response = self.client.post(reverse("produit_delete", args=[produit.pk]))
        self.assertRedirects(response, reverse("produits"))
        self.assertFalse(Produit.objects.filter(pk="MAN").exists())

    def test_marche_and_enqueteur_can_be_managed(self):
        response = self.client.post(
            reverse("marche_create"),
            {
                "code_marche": "MOK",
                "nom_marche": "Marché central",
                "ville": "Yaoundé",
            },
        )
        self.assertRedirects(response, reverse("marches"))
        response = self.client.post(
            reverse("marche_update", args=["MOK"]),
            {
                "code_marche": "MOK",
                "nom_marche": "Marché central rénové",
                "ville": "Yaoundé",
            },
        )
        self.assertRedirects(response, reverse("marches"))
        self.assertEqual(Marche.objects.get(pk="MOK").nom_marche, "Marché central rénové")

        response = self.client.post(
            reverse("enqueteur_create"),
            {"matricule": "ENQ001", "nom_enq": "Ada", "telephone": "690000000"},
        )
        self.assertRedirects(response, reverse("enqueteurs"))
        response = self.client.post(
            reverse("enqueteur_update", args=["ENQ001"]),
            {"matricule": "ENQ001", "nom_enq": "Ada Lovelace", "telephone": ""},
        )
        self.assertRedirects(response, reverse("enqueteurs"))
        self.assertEqual(Enqueteur.objects.get(pk="ENQ001").nom_enq, "Ada Lovelace")

    def test_reference_and_affectation_detail_pages_render(self):
        marche = Marche.objects.create(
            code_marche="MOK",
            nom_marche="Marché central",
            ville="Yaoundé",
        )
        produit = Produit.objects.create(
            code_produit="MAN",
            libelle="Manioc",
            unite=Produit.Unite.KG,
        )
        enqueteur = Enqueteur.objects.create(
            matricule="ENQ001",
            nom_enq="Ada",
        )
        affectation = Affectation.objects.create(
            enqueteur=enqueteur,
            marche=marche,
            date_debut="2026-09-01",
        )

        pages = (
            ("marche_detail", marche.pk),
            ("produit_detail", produit.pk),
            ("enqueteur_detail", enqueteur.pk),
            ("affectation_detail", affectation.pk),
        )
        for name, pk in pages:
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name, args=[pk])).status_code,
                    200,
                )

    def test_referenced_product_cannot_be_deleted(self):
        produit = Produit.objects.create(
            code_produit="MAN", libelle="Manioc", unite=Produit.Unite.KG
        )
        marche = Marche.objects.create(
            code_marche="MOK", nom_marche="Marché central", ville="Yaoundé"
        )
        enqueteur = Enqueteur.objects.create(matricule="ENQ001", nom_enq="Ada")
        Releve.objects.create(
            date_releve="2026-11-10",
            prix=650,
            produit=produit,
            marche=marche,
            enqueteur=enqueteur,
        )

        response = self.client.post(
            reverse("produit_delete", args=[produit.pk]),
            follow=True,
        )

        self.assertContains(response, "Suppression impossible")
        self.assertRedirects(response, reverse("produits"))
        self.assertTrue(Produit.objects.filter(pk=produit.pk).exists())


class AffectationTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="manager",
            password="Test-password-123!",
        )
        self.client.force_login(user)
        self.enqueteur = Enqueteur.objects.create(
            matricule="ENQ001",
            nom_enq="Ada",
        )
        self.marche = Marche.objects.create(
            code_marche="MOK",
            nom_marche="Marché central",
            ville="Yaoundé",
        )
        self.data = {
            "enqueteur": self.enqueteur.pk,
            "marche": self.marche.pk,
            "date_debut": "2026-09-01",
        }

    def test_affectation_can_be_created_updated_and_deleted(self):
        response = self.client.post(reverse("affectation_create"), self.data)
        self.assertRedirects(response, reverse("affectations"))
        affectation = Affectation.objects.get()

        response = self.client.post(
            reverse("affectation_update", args=[affectation.pk]),
            {**self.data, "date_debut": "2026-09-03"},
        )
        self.assertRedirects(response, reverse("affectations"))
        affectation.refresh_from_db()
        self.assertEqual(str(affectation.date_debut), "2026-09-03")

        response = self.client.post(
            reverse("affectation_delete", args=[affectation.pk])
        )
        self.assertRedirects(response, reverse("affectations"))
        self.assertFalse(Affectation.objects.exists())

    def test_duplicate_enqueteur_market_assignment_is_rejected(self):
        Affectation.objects.create(
            enqueteur=self.enqueteur,
            marche=self.marche,
            date_debut="2026-09-01",
        )

        response = self.client.post(reverse("affectation_create"), self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Affectation.objects.count(), 1)
        self.assertTrue(response.context["form"].non_field_errors())

    def test_references_cannot_be_deleted_while_assigned(self):
        Affectation.objects.create(
            enqueteur=self.enqueteur,
            marche=self.marche,
            date_debut="2026-09-01",
        )

        response = self.client.post(reverse("marche_delete", args=[self.marche.pk]))

        self.assertRedirects(response, reverse("marches"))
        self.assertTrue(Marche.objects.filter(pk=self.marche.pk).exists())


class ReleveManagementTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="surveyuser",
            password="Test-password-123!",
        )
        self.enqueteur = Enqueteur.objects.create(
            matricule="ENQ001",
            nom_enq="Ada",
            user=self.user,
        )
        self.other_user = user_model.objects.create_user(
            username="otheruser",
            password="Test-password-123!",
        )
        self.other_enqueteur = Enqueteur.objects.create(
            matricule="ENQ002",
            nom_enq="Grace",
            user=self.other_user,
        )
        self.staff = user_model.objects.create_user(
            username="staffuser",
            password="Test-password-123!",
            is_staff=True,
        )
        self.marche = Marche.objects.create(
            code_marche="MOK",
            nom_marche="Marché central",
            ville="Yaoundé",
        )
        self.produit = Produit.objects.create(
            code_produit="MAN",
            libelle="Manioc",
            unite=Produit.Unite.KG,
        )
        self.client.force_login(self.user)

    def releve_data(self, **overrides):
        return {
            "date_releve": "2026-11-10",
            "prix": "650",
            "produit": self.produit.pk,
            "marche": self.marche.pk,
            **overrides,
        }

    def test_authenticated_user_can_create_and_list_a_releve(self):
        response = self.client.post(
            reverse("releve_create"),
            {**self.releve_data(), "enqueteur": self.other_enqueteur.pk},
            follow=True,
        )

        self.assertRedirects(response, reverse("releve_list"))
        releve = Releve.objects.get()
        self.assertEqual(releve.prix, 650)
        self.assertEqual(releve.enqueteur, self.enqueteur)
        self.assertContains(response, "Le relevé a été enregistré.")
        self.assertContains(response, "650 FCFA")

    def test_price_must_be_strictly_positive(self):
        response = self.client.post(
            reverse("releve_create"),
            self.releve_data(prix="0"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("prix", response.context["form"].errors)
        self.assertFalse(Releve.objects.exists())

    def test_account_without_enqueteur_cannot_create_a_releve(self):
        user = get_user_model().objects.create_user(
            username="unlinked",
            password="Test-password-123!",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("releve_create"),
            self.releve_data(),
            follow=True,
        )

        self.assertRedirects(response, reverse("releve_list"))
        self.assertFalse(Releve.objects.exists())
        self.assertContains(response, "n’est associé à aucun enquêteur")

    def test_owner_can_consult_update_and_delete_a_releve(self):
        releve = Releve.objects.create(
            date_releve="2026-11-10",
            prix=650,
            produit=self.produit,
            marche=self.marche,
            enqueteur=self.enqueteur,
        )

        self.assertEqual(
            self.client.get(reverse("releve_detail", args=[releve.pk])).status_code,
            200,
        )
        response = self.client.post(
            reverse("releve_update", args=[releve.pk]),
            self.releve_data(prix="700"),
        )
        self.assertRedirects(response, reverse("releve_list"))
        releve.refresh_from_db()
        self.assertEqual(releve.prix, 700)
        self.assertEqual(releve.enqueteur, self.enqueteur)

        response = self.client.get(reverse("releve_delete", args=[releve.pk]))
        self.assertContains(response, "Confirmer la suppression")
        response = self.client.post(reverse("releve_delete", args=[releve.pk]))
        self.assertRedirects(response, reverse("releve_list"))
        self.assertFalse(Releve.objects.filter(pk=releve.pk).exists())

    def test_user_cannot_consult_or_edit_another_enqueteurs_releve(self):
        releve = Releve.objects.create(
            date_releve="2026-11-10",
            prix=650,
            produit=self.produit,
            marche=self.marche,
            enqueteur=self.other_enqueteur,
        )

        self.assertEqual(
            self.client.get(reverse("releve_detail", args=[releve.pk])).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("releve_update", args=[releve.pk])).status_code,
            404,
        )

    def test_staff_can_edit_any_releve_without_changing_its_author(self):
        releve = Releve.objects.create(
            date_releve="2026-11-10",
            prix=650,
            produit=self.produit,
            marche=self.marche,
            enqueteur=self.enqueteur,
        )
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("releve_update", args=[releve.pk]),
            self.releve_data(prix="700"),
        )

        self.assertRedirects(response, reverse("releve_list"))
        releve.refresh_from_db()
        self.assertEqual(releve.prix, 700)
        self.assertEqual(releve.enqueteur, self.enqueteur)
