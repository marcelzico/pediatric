# urls.py
from django.urls import path

from . import views

app_name = "patient"

urlpatterns = [
    path(
        "",
        views.observation_list,
        name="observation_list",
    ),
    path(
        "observations/nouvelle/",
        views.observation_form,
        name="observation_create",
    ),
    path(
        "observations/<int:pk>/",
        views.observation_detail,
        name="observation_detail",
    ),
    path(
        "observations/<int:pk>/modifier/",
        views.observation_form,
        name="observation_update",
    ),
    path(
        "observations/<int:pk>/supprimer/",
        views.observation_delete,
        name="observation_delete",
    ),
    path(
        "observations/<int:pk>/docx/",
        views.observation_generate_docx,
        name="observation_generate_docx",
    ),
    path(
        "observations/<int:observation_pk>/examens-physiques/",
        views.examen_physique_list,
        name="examen_physique_list",
    ),
    path(
        "observations/<int:observation_pk>/examens-physiques/ajouter/",
        views.examen_physique_create,
        name="examen_physique_create",
    ),
    path(
        "examens-physiques/<int:pk>/modifier/",
        views.examen_physique_update,
        name="examen_physique_update",
    ),
    path(
        "examens-physiques/<int:pk>/supprimer/",
        views.examen_physique_delete,
        name="examen_physique_delete",
    ),

    # Fiches de réhydratation
    path(
        "observations/<int:observation_pk>/rehydratation/",
        views.fiche_rehydratation_list,
        name="fiche_rehydratation_list",
    ),
    path(
        "observations/<int:observation_pk>/rehydratation/ajouter/",
        views.fiche_rehydratation_create,
        name="fiche_rehydratation_create",
    ),
    path(
        "rehydratation/<int:pk>/modifier/",
        views.fiche_rehydratation_update,
        name="fiche_rehydratation_update",
    ),
    path(
        "rehydratation/<int:pk>/supprimer/",
        views.fiche_rehydratation_delete,
        name="fiche_rehydratation_delete",
    ),

    
    # Traitements ajustés et tracés
    path(
        "observations/<int:observation_pk>/traitements/",
        views.traitement_ajustement_list,
        name="traitement_ajustement_list",
    ),
    path(
        "observations/<int:observation_pk>/traitements/ajouter/",
        views.traitement_ajustement_create,
        name="traitement_ajustement_create",
    ),
    path(
        "traitements/<int:pk>/",
        views.traitement_ajustement_detail,
        name="traitement_ajustement_detail",
    ),
    path(
        "traitements/<int:pk>/modifier/",
        views.traitement_ajustement_update,
        name="traitement_ajustement_update",
    ),
    path(
        "traitements/<int:pk>/supprimer/",
        views.traitement_ajustement_delete,
        name="traitement_ajustement_delete",
    ),
]
