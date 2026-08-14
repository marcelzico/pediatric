# patient/admin.py
from django.contrib import admin

from .models import (
    ObservationMedicale,
    AntecedentsFamiliaux,
    Grossesse,
    Accouchement,
    Alimentation,
    Vaccination,
    ContexteEpidemiologique,
    FicheSociale,
    EpisodeHistoireMaladie,
    DeveloppementPsychomoteur,
    AntecedentsPersonnels,
    ExamenClinique,
    HypotheseDiagnostic,
    Traitement,
    Evolution,
    ExamenPhysique,
    FicheRehydratation,
    EvaluationHoraireRehydratation,
    TraitementAjustement,
    LigneTraitement,
)


# ============================================================
# PERSONNALISATION GLOBALE DE L'ADMIN
# ============================================================

admin.site.site_header = "Administration - Application Patient"
admin.site.site_title = "Patient Admin"
admin.site.index_title = "Gestion des observations et suivis médicaux"


# ============================================================
# HELPERS D'AFFICHAGE
# ============================================================

@admin.display(description="Âge")
def observation_age_display(obj):
    return obj.age_display


@admin.display(description="Gain de poids")
def fiche_rehydratation_gain_display(obj):
    return obj.gain_poids_display


@admin.display(description="Diagnostic")
def hypothese_diagnostic_short_display(obj):
    return (obj.diagnostic_propose or "")[:80]


# ============================================================
# BASE ADMIN POUR LES MODÈLES LIÉS À UNE OBSERVATION
# ============================================================

class ObservationRelatedAdmin(admin.ModelAdmin):
    raw_id_fields = ("observation",)
    search_fields = (
        "observation__nom",
        "observation__prenoms",
        "observation__numero_dossier",
        "observation__lit",
    )


# ============================================================
# OBSERVATION MÉDICALE
# ============================================================

@admin.register(ObservationMedicale)
class ObservationMedicaleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lit",
        "nom",
        "prenoms",
        "type_observation",
        observation_age_display,
        "sexe",
        "date_admission",
        "numero_dossier",
        "created_at",
    )
    list_filter = (
        "type_observation",
        "sexe",
    )
    search_fields = (
        "id",
        "nom",
        "prenoms",
        "numero_dossier",
        "lit",
        "motif_admission",
        "diagnostic_retenu",
    )
    ordering = ("-created_at",)
    date_hierarchy = "date_admission"
    list_per_page = 50


# ============================================================
# ANTÉCÉDENTS FAMILIAUX
# ============================================================

@admin.register(AntecedentsFamiliaux)
class AntecedentsFamiliauxAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "rang_fratrie",
    )


# ============================================================
# GROSSESSE
# ============================================================

@admin.register(Grossesse)
class GrossesseAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "age_mere",
        "gpa",
        "nombre_cpn",
        "conclusion",
    )


# ============================================================
# ACCOUCHEMENT
# ============================================================

@admin.register(Accouchement)
class AccouchementAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "lieu",
        "terme",
        "voie",
        "poids_naissance_kg",
        "adaptation_neonatale",
    )


# ============================================================
# ALIMENTATION
# ============================================================

@admin.register(Alimentation)
class AlimentationAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "ame_jusqua_mois",
        "diversification_mois",
        "regime",
    )


# ============================================================
# VACCINATION
# ============================================================

@admin.register(Vaccination)
class VaccinationAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "vaccination_correcte",
        "nom_carnet",
    )


# ============================================================
# CONTEXTE ÉPIDÉMIOLOGIQUE
# ============================================================

@admin.register(ContexteEpidemiologique)
class ContexteEpidemiologiqueAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "convulsion_parents_bas_age",
        "convulsion_hyperthermique",
    )


# ============================================================
# FICHE SOCIALE
# ============================================================

@admin.register(FicheSociale)
class FicheSocialeAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "profession_pere",
        "profession_mere",
        "niveau_social",
    )


# ============================================================
# HISTOIRE DE LA MALADIE
# ============================================================

@admin.register(EpisodeHistoireMaladie)
class EpisodeHistoireMaladieAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "ordre",
        "date_debut",
        "evolution",
    )
    list_filter = ("evolution",)
    date_hierarchy = "date_debut"


# ============================================================
# DÉVELOPPEMENT PSYCHOMOTEUR
# ============================================================

@admin.register(DeveloppementPsychomoteur)
class DeveloppementPsychomoteurAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "conclusion",
    )


# ============================================================
# ANTÉCÉDENTS PERSONNELS
# ============================================================

@admin.register(AntecedentsPersonnels)
class AntecedentsPersonnelsAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
    )


# ============================================================
# EXAMEN CLINIQUE INITIAL
# ============================================================

@admin.register(ExamenClinique)
class ExamenCliniqueAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "date_examen",
        "poids_kg",
        "taille_cm",
        "conclusion_biometrie",
    )
    date_hierarchy = "date_examen"


# ============================================================
# DISCUSSION DIAGNOSTIQUE
# ============================================================

@admin.register(HypotheseDiagnostic)
class HypotheseDiagnosticAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "ordre",
        hypothese_diagnostic_short_display,
    )


# ============================================================
# TRAITEMENT INITIAL
# ============================================================

@admin.register(Traitement)
class TraitementAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
    )


# ============================================================
# ÉVOLUTION SIMPLE
# ============================================================

@admin.register(Evolution)
class EvolutionAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "date",
        "statut",
    )
    date_hierarchy = "date"


# ============================================================
# EXAMEN PHYSIQUE DE SUIVI
# ============================================================

@admin.register(ExamenPhysique)
class ExamenPhysiqueAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "date_heure",
        "temperature_c",
        "frequence_respiratoire",
        "frequence_cardiaque",
        "saturation_oxygene",
    )
    date_hierarchy = "date_heure"


# ============================================================
# RÉHYDRATATION
# ============================================================

class EvaluationHoraireRehydratationInline(admin.StackedInline):
    model = EvaluationHoraireRehydratation
    extra = 0
    classes = ("collapse",)
    fields = (
        "heure_evaluation",
        "signes_generaux",
        "signes_fonctionnels",
        "etat_yeux",
        "etat_muqueuses",
        "pli_cutane",
        "urine",
        "selles",
        "vomissements",
        "temperature_c",
        "frequence_respiratoire",
        "frequence_cardiaque",
        "remarque",
    )


@admin.register(FicheRehydratation)
class FicheRehydratationAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "heure_debut",
        "statut",
        "poids_initial_kg",
        "poids_final_kg",
        fiche_rehydratation_gain_display,
        "quantite_liquide_ml",
    )
    list_filter = ("statut",)
    date_hierarchy = "heure_debut"
    inlines = (EvaluationHoraireRehydratationInline,)


@admin.register(EvaluationHoraireRehydratation)
class EvaluationHoraireRehydratationAdmin(admin.ModelAdmin):
    list_display = (
        "fiche_rehydratation",
        "heure_evaluation",
        "urine",
        "selles",
        "vomissements",
        "temperature_c",
        "frequence_respiratoire",
        "frequence_cardiaque",
    )
    raw_id_fields = ("fiche_rehydratation",)
    search_fields = (
        "fiche_rehydratation__observation__nom",
        "fiche_rehydratation__observation__prenoms",
        "fiche_rehydratation__observation__numero_dossier",
    )
    date_hierarchy = "heure_evaluation"


# ============================================================
# TRAITEMENTS AJUSTÉS ET TRACÉS
# ============================================================

class LigneTraitementInline(admin.TabularInline):
    model = LigneTraitement
    extra = 0
    fields = (
        "type_ligne",
        "nom",
        "dose",
        "voie",
        "frequence",
        "duree",
        "date_debut",
        "date_fin",
        "instructions",
    )


@admin.register(TraitementAjustement)
class TraitementAjustementAdmin(ObservationRelatedAdmin):
    list_display = (
        "observation",
        "version",
        "date_heure",
        "type_ajustement",
    )
    list_filter = ("type_ajustement",)
    date_hierarchy = "date_heure"
    inlines = (LigneTraitementInline,)


@admin.register(LigneTraitement)
class LigneTraitementAdmin(admin.ModelAdmin):
    list_display = (
        "ajustement",
        "nom",
        "dose",
        "voie",
        "frequence",
    )
    raw_id_fields = ("ajustement",)
    search_fields = (
        "nom",
        "dose",
        "instructions",
        "ajustement__observation__nom",
        "ajustement__observation__prenoms",
        "ajustement__observation__numero_dossier",
    )
    