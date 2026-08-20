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
    path(
        "observations/<int:observation_pk>/paraclinique/",
        views.examen_paraclinique_list,
        name="examen_paraclinique_list",
    ),
    path(
        "observations/<int:observation_pk>/paraclinique/ajouter/",
        views.examen_paraclinique_create,
        name="examen_paraclinique_create",
    ),
    path(
        "paraclinique/<int:pk>/modifier/",
        views.examen_paraclinique_update,
        name="examen_paraclinique_update",
    ),
    path(
        "paraclinique/<int:pk>/supprimer/",
        views.examen_paraclinique_delete,
        name="examen_paraclinique_delete",
    ),


    path("observations/etat_civil/", views.create_etat_civil, name="etat_civil"),
    path("observations/<int:pk>/atcd_familial/", views.create_atcd_familial, name="atcd_familial"),
    path("observations/<int:pk>/grossesse/", views.create_grossesse, name="grossesse"),
    path("observations/<int:pk>/accouchement/", views.create_accouchement, name="accouchement"),
    path("observations/<int:pk>/alimentation/", views.create_alimentation, name="alimentation"),
    path("observations/<int:pk>/vaccination/", views.create_vaccination, name="vaccination"),
    path("observations/<int:pk>/social/", views.create_social, name="social"),
    path("observations/<int:pk>/dpm/", views.create_dpm, name="dpm"),
    path("observations/<int:pk>/hdm/", views.create_hdm, name="hdm"),
    path("observations/<int:pk>/examen/", views.create_examen, name="examen"),
    path("observations/<int:pk>/discussion/", views.create_discussion, name="discussion"),
    path("observations/<int:pk>/traitement/", views.create_traitement, name="traitement"),
]
