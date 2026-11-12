from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import (
    AffectationForm,
    EnqueteurForm,
    MarcheForm,
    ProduitForm,
    RegistrationForm,
    ReleveForm,
)
from .models import Affectation, Enqueteur, Marche, Produit, Releve


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Votre compte enquêteur a été créé.")
            return redirect("home")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "Enqueter/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            marche_count=Marche.objects.count(),
            produit_count=Produit.objects.count(),
            enqueteur_count=Enqueteur.objects.count(),
            affectation_count=Affectation.objects.count(),
            releve_count=Releve.objects.count(),
        )
        return context


class FormPageMixin:
    page_title = ""
    cancel_url = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(page_title=self.page_title, cancel_url=self.cancel_url)
        return context


class SuccessMessageMixin:
    success_message = ""

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class ProtectedDeleteView(LoginRequiredMixin, DeleteView):
    page_title = ""
    success_message = ""
    cancel_url = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(page_title=self.page_title, cancel_url=self.cancel_url)
        return context

    def form_valid(self, form):
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(
                self.request,
                "Suppression impossible : cet élément est utilisé par d’autres données.",
            )
            return redirect(self.get_success_url())
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())


class ReferenceDetailView(LoginRequiredMixin, DetailView):
    template_name = "Enqueter/detail.html"
    page_title = ""
    list_url = ""
    update_url = ""
    delete_url = ""

    def get_detail_rows(self):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            page_title=self.page_title,
            detail_rows=self.get_detail_rows(),
            list_url=reverse_lazy(self.list_url),
            update_url=reverse_lazy(self.update_url, kwargs={"pk": self.object.pk}),
            delete_url=reverse_lazy(self.delete_url, kwargs={"pk": self.object.pk}),
        )
        return context


class MarcheDetailView(ReferenceDetailView):
    model = Marche
    context_object_name = "marche"
    page_title = "Détail du marché"
    list_url = "marches"
    update_url = "marche_update"
    delete_url = "marche_delete"

    def get_detail_rows(self):
        return (
            ("Code", self.object.code_marche),
            ("Nom", self.object.nom_marche),
            ("Ville", self.object.ville),
        )


class ProduitDetailView(ReferenceDetailView):
    model = Produit
    context_object_name = "produit"
    page_title = "Détail du produit"
    list_url = "produits"
    update_url = "produit_update"
    delete_url = "produit_delete"

    def get_detail_rows(self):
        return (
            ("Code", self.object.code_produit),
            ("Libellé", self.object.libelle),
            ("Unité", self.object.get_unite_display()),
        )


class EnqueteurDetailView(ReferenceDetailView):
    model = Enqueteur
    context_object_name = "enqueteur"
    page_title = "Détail de l’enquêteur"
    list_url = "enqueteurs"
    update_url = "enqueteur_update"
    delete_url = "enqueteur_delete"

    def get_detail_rows(self):
        return (
            ("Matricule", self.object.matricule),
            ("Nom", self.object.nom_enq),
            ("Téléphone", self.object.telephone or "—"),
            ("Compte", self.object.user or "—"),
        )


class AffectationDetailView(ReferenceDetailView):
    model = Affectation
    context_object_name = "affectation"
    page_title = "Détail de l’affectation"
    list_url = "affectations"
    update_url = "affectation_update"
    delete_url = "affectation_delete"

    def get_queryset(self):
        return super().get_queryset().select_related("enqueteur", "marche")

    def get_detail_rows(self):
        return (
            ("Enquêteur", self.object.enqueteur),
            ("Marché", self.object.marche),
            ("Date de début", self.object.date_debut.strftime("%d/%m/%Y")),
        )


class MarcheListView(LoginRequiredMixin, ListView):
    model = Marche
    template_name = "Enqueter/marches.html"
    context_object_name = "marches"
    queryset = Marche.objects.order_by("nom_marche")


class MarcheCreateView(LoginRequiredMixin, SuccessMessageMixin, FormPageMixin, CreateView):
    model = Marche
    form_class = MarcheForm
    template_name = "Enqueter/formulaire.html"
    success_url = reverse_lazy("marches")
    page_title = "Nouveau marché"
    cancel_url = reverse_lazy("marches")
    success_message = "Le marché a été créé."


class MarcheUpdateView(LoginRequiredMixin, SuccessMessageMixin, FormPageMixin, UpdateView):
    model = Marche
    form_class = MarcheForm
    template_name = "Enqueter/formulaire.html"
    success_url = reverse_lazy("marches")
    page_title = "Modifier le marché"
    cancel_url = reverse_lazy("marches")
    success_message = "Le marché a été modifié."


class MarcheDeleteView(ProtectedDeleteView):
    model = Marche
    template_name = "Enqueter/confirmation_suppression.html"
    success_url = reverse_lazy("marches")
    page_title = "Supprimer le marché"
    cancel_url = reverse_lazy("marches")
    success_message = "Le marché a été supprimé."


class ProduitListView(LoginRequiredMixin, ListView):
    model = Produit
    template_name = "Enqueter/produits.html"
    context_object_name = "produits"
    queryset = Produit.objects.order_by("libelle")


class ProduitCreateView(LoginRequiredMixin, SuccessMessageMixin, FormPageMixin, CreateView):
    model = Produit
    form_class = ProduitForm
    template_name = "Enqueter/formulaire.html"
    success_url = reverse_lazy("produits")
    page_title = "Nouveau produit"
    cancel_url = reverse_lazy("produits")
    success_message = "Le produit a été créé."


class ProduitUpdateView(LoginRequiredMixin, SuccessMessageMixin, FormPageMixin, UpdateView):
    model = Produit
    form_class = ProduitForm
    template_name = "Enqueter/formulaire.html"
    success_url = reverse_lazy("produits")
    page_title = "Modifier le produit"
    cancel_url = reverse_lazy("produits")
    success_message = "Le produit a été modifié."


class ProduitDeleteView(ProtectedDeleteView):
    model = Produit
    template_name = "Enqueter/confirmation_suppression.html"
    success_url = reverse_lazy("produits")
    page_title = "Supprimer le produit"
    cancel_url = reverse_lazy("produits")
    success_message = "Le produit a été supprimé."


class EnqueteurListView(LoginRequiredMixin, ListView):
    model = Enqueteur
    template_name = "Enqueter/enqueteurs.html"
    context_object_name = "enqueteurs"
    queryset = Enqueteur.objects.order_by("nom_enq")


class EnqueteurCreateView(LoginRequiredMixin, SuccessMessageMixin, FormPageMixin, CreateView):
    model = Enqueteur
    form_class = EnqueteurForm
    template_name = "Enqueter/formulaire.html"
    success_url = reverse_lazy("enqueteurs")
    page_title = "Nouvel enquêteur"
    cancel_url = reverse_lazy("enqueteurs")
    success_message = "L’enquêteur a été créé."


class EnqueteurUpdateView(LoginRequiredMixin, SuccessMessageMixin, FormPageMixin, UpdateView):
    model = Enqueteur
    form_class = EnqueteurForm
    template_name = "Enqueter/formulaire.html"
    success_url = reverse_lazy("enqueteurs")
    page_title = "Modifier l’enquêteur"
    cancel_url = reverse_lazy("enqueteurs")
    success_message = "L’enquêteur a été modifié."


class EnqueteurDeleteView(ProtectedDeleteView):
    model = Enqueteur
    template_name = "Enqueter/confirmation_suppression.html"
    success_url = reverse_lazy("enqueteurs")
    page_title = "Supprimer l’enquêteur"
    cancel_url = reverse_lazy("enqueteurs")
    success_message = "L’enquêteur a été supprimé."


class AffectationListView(LoginRequiredMixin, ListView):
    model = Affectation
    template_name = "Enqueter/affectations.html"
    context_object_name = "affectations"
    queryset = Affectation.objects.select_related("enqueteur", "marche").order_by(
        "marche__nom_marche", "enqueteur__nom_enq"
    )


class AffectationCreateView(
    LoginRequiredMixin, SuccessMessageMixin, FormPageMixin, CreateView
):
    model = Affectation
    form_class = AffectationForm
    template_name = "Enqueter/formulaire.html"
    success_url = reverse_lazy("affectations")
    page_title = "Nouvelle affectation"
    cancel_url = reverse_lazy("affectations")
    success_message = "L’affectation a été créée."


class AffectationUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, FormPageMixin, UpdateView
):
    model = Affectation
    form_class = AffectationForm
    template_name = "Enqueter/formulaire.html"
    success_url = reverse_lazy("affectations")
    page_title = "Modifier l’affectation"
    cancel_url = reverse_lazy("affectations")
    success_message = "L’affectation a été modifiée."


class AffectationDeleteView(ProtectedDeleteView):
    model = Affectation
    template_name = "Enqueter/confirmation_suppression.html"
    success_url = reverse_lazy("affectations")
    page_title = "Supprimer l’affectation"
    cancel_url = reverse_lazy("affectations")
    success_message = "L’affectation a été supprimée."


class ReleveListView(LoginRequiredMixin, ListView):
    model = Releve
    template_name = "Enqueter/releve_list.html"
    context_object_name = "releves"
    queryset = Releve.objects.select_related(
        "marche", "produit", "enqueteur"
    ).order_by("-date_releve", "-pk")


class ReleveCreateView(LoginRequiredMixin, FormPageMixin, CreateView):
    model = Releve
    form_class = ReleveForm
    template_name = "Enqueter/releve_form.html"
    success_url = reverse_lazy("releve_list")
    page_title = "Nouveau relevé"
    cancel_url = reverse_lazy("releve_list")

    def form_valid(self, form):
        enqueteur = getattr(self.request.user, "enqueteur", None)
        if enqueteur is None:
            messages.error(
                self.request,
                "Votre compte n’est associé à aucun enquêteur. "
                "Contactez un administrateur avant de saisir un relevé.",
            )
            return redirect("releve_list")
        self.object = form.save(commit=False)
        self.object.enqueteur = enqueteur
        self.object.save()
        messages.success(self.request, "Le relevé a été enregistré.")
        return HttpResponseRedirect(self.get_success_url())


class ReleveDetailView(LoginRequiredMixin, DetailView):
    model = Releve
    template_name = "Enqueter/releve_detail.html"
    context_object_name = "releve"

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            "marche", "produit", "enqueteur", "enqueteur__user"
        )
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(enqueteur__user=self.request.user)


class ReleveUpdateView(LoginRequiredMixin, SuccessMessageMixin, FormPageMixin, UpdateView):
    model = Releve
    form_class = ReleveForm
    template_name = "Enqueter/releve_form.html"
    success_url = reverse_lazy("releve_list")
    page_title = "Modifier le relevé"
    cancel_url = reverse_lazy("releve_list")
    success_message = "Le relevé a été modifié."

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(enqueteur__user=self.request.user)


class ReleveDeleteView(ProtectedDeleteView):
    model = Releve
    template_name = "Enqueter/confirmation_suppression.html"
    success_url = reverse_lazy("releve_list")
    page_title = "Supprimer le relevé"
    cancel_url = reverse_lazy("releve_list")
    success_message = "Le relevé a été supprimé."

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(enqueteur__user=self.request.user)
