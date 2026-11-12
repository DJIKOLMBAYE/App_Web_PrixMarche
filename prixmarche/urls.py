from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from Enqueter import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(
        "connexion/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("inscription/", views.register, name="register"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
    path("marches/", views.MarcheListView.as_view(), name="marches"),
    path("marches/nouveau/", views.MarcheCreateView.as_view(), name="marche_create"),
    path(
        "marches/<str:pk>/",
        views.MarcheDetailView.as_view(),
        name="marche_detail",
    ),
    path(
        "marches/<str:pk>/modifier/",
        views.MarcheUpdateView.as_view(),
        name="marche_update",
    ),
    path(
        "marches/<str:pk>/supprimer/",
        views.MarcheDeleteView.as_view(),
        name="marche_delete",
    ),
    path("produits/", views.ProduitListView.as_view(), name="produits"),
    path("produits/nouveau/", views.ProduitCreateView.as_view(), name="produit_create"),
    path(
        "produits/<str:pk>/",
        views.ProduitDetailView.as_view(),
        name="produit_detail",
    ),
    path(
        "produits/<str:pk>/modifier/",
        views.ProduitUpdateView.as_view(),
        name="produit_update",
    ),
    path(
        "produits/<str:pk>/supprimer/",
        views.ProduitDeleteView.as_view(),
        name="produit_delete",
    ),
    path("enqueteurs/", views.EnqueteurListView.as_view(), name="enqueteurs"),
    path(
        "enqueteurs/nouveau/",
        views.EnqueteurCreateView.as_view(),
        name="enqueteur_create",
    ),
    path(
        "enqueteurs/<str:pk>/",
        views.EnqueteurDetailView.as_view(),
        name="enqueteur_detail",
    ),
    path(
        "enqueteurs/<str:pk>/modifier/",
        views.EnqueteurUpdateView.as_view(),
        name="enqueteur_update",
    ),
    path(
        "enqueteurs/<str:pk>/supprimer/",
        views.EnqueteurDeleteView.as_view(),
        name="enqueteur_delete",
    ),
    path("affectations/", views.AffectationListView.as_view(), name="affectations"),
    path(
        "affectations/nouvelle/",
        views.AffectationCreateView.as_view(),
        name="affectation_create",
    ),
    path(
        "affectations/<int:pk>/",
        views.AffectationDetailView.as_view(),
        name="affectation_detail",
    ),
    path(
        "affectations/<int:pk>/modifier/",
        views.AffectationUpdateView.as_view(),
        name="affectation_update",
    ),
    path(
        "affectations/<int:pk>/supprimer/",
        views.AffectationDeleteView.as_view(),
        name="affectation_delete",
    ),
    path("gestion/releves/", views.ReleveListView.as_view(), name="releve_list"),
    path(
        "gestion/releves/nouveau/",
        views.ReleveCreateView.as_view(),
        name="releve_create",
    ),
    path(
        "gestion/releves/<int:pk>/",
        views.ReleveDetailView.as_view(),
        name="releve_detail",
    ),
    path(
        "gestion/releves/<int:pk>/modifier/",
        views.ReleveUpdateView.as_view(),
        name="releve_update",
    ),
    path(
        "gestion/releves/<int:pk>/supprimer/",
        views.ReleveDeleteView.as_view(),
        name="releve_delete",
    ),
    path("admin/", admin.site.urls),
]
