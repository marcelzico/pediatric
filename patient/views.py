from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    ObservationMedicale,
    AntecedentsFamiliaux,
    Grossesse,
    Accouchement,
    Alimentation,
    Vaccination,
    ContexteEpidemiologique,
    FicheSociale,
    DeveloppementPsychomoteur,
    AntecedentsPersonnels,
    ExamenClinique,
    HypotheseDiagnostic,
    Traitement,
    Evolution,
    EpisodeHistoireMaladie,
    ExamenPhysique,
    FicheRehydratation,
    EvaluationHoraireRehydratation,
    TraitementAjustement,
    LigneTraitement,
)
from .forms import (
    ObservationMedicaleForm,
    AntecedentsFamiliauxForm,
    GrossesseForm,
    AccouchementForm,
    AlimentationForm,
    VaccinationForm,
    ContexteEpidemiologiqueForm,
    FicheSocialeForm,
    DeveloppementPsychomoteurForm,
    AntecedentsPersonnelsForm,
    ExamenCliniqueForm,
    HypotheseDiagnosticForm,
    HypotheseDiagnosticFormSet,
    TraitementForm,
    EvolutionForm,
    EvolutionFormSet,
    EpisodeHistoireMaladieForm,
    EpisodeHistoireMaladieFormSet,
    ExamenCliniqueBaseForm,
    ExamenPhysiqueForm,
    FicheRehydratationForm,
    EvaluationHoraireRehydratationFormSet,
    TraitementAjustementForm,
    LigneTraitementFormSet,
    SerologiesForm,  # Sous-formulaire pour les sérologies de grossesse
)
from .exam_forms import EXAM_SUBFORMS  # Sous-formulaires d'examen par appareil
from . import constants as C

from .exam_forms import (
    PleuroPulmonaireExamenForm,
    CardiovasculaireExamenForm,
    DigestifExamenForm,
    NeurologiqueExamenForm,
    ORLExamenForm,
    CutaneomuqueuxExamenForm,
    GenitauxExamenForm,
    OsteoarticulaireExamenForm,
)


# ============================================================
# CONFIGURATION DES SECTIONS
# ============================================================

RELATED_FORMS = (
    # (clé dans le contexte, classe de formulaire, related_name sur ObservationMedicale, réservé enfant ?)
    ("antecedents_familiaux", AntecedentsFamiliauxForm, "antecedents_familiaux", False),
    ("grossesse", GrossesseForm, "grossesse", False),
    ("accouchement", AccouchementForm, "accouchement", False),
    ("alimentation", AlimentationForm, "alimentation", False),
    ("vaccination", VaccinationForm, "vaccination", False),
    ("contexte_epidemiologique", ContexteEpidemiologiqueForm, "contexte_epidemiologique", False),
    ("fiche_sociale", FicheSocialeForm, "fiche_sociale", False),
    ("developpement_psychomoteur", DeveloppementPsychomoteurForm, "developpement_psychomoteur", True),
    ("antecedents_personnels", AntecedentsPersonnelsForm, "antecedents_personnels", True),
    ("traitement", TraitementForm, "traitement", False),
)

SECTION_LABELS = {
    "observation": "État civil / Admission",
    "antecedents_familiaux": "Antécédents familiaux",
    "grossesse": "Déroulement de la grossesse",
    "accouchement": "Déroulement de l'accouchement",
    "alimentation": "Alimentation",
    "vaccination": "Vaccination",
    "contexte_epidemiologique": "Contexte épidémiologique",
    "fiche_sociale": "Fiche sociale",
    "developpement_psychomoteur": "Développement psychomoteur",
    "antecedents_personnels": "Antécédents personnels",
    "examen_clinique": "Examen clinique",
    "traitement": "Traitement",
}


# ============================================================
# HELPERS
# ============================================================

def get_related_instance(observation, related_name):
    """
    Récupère l'objet lié OneToOne s'il existe, sinon None.
    Évite les RelatedObjectDoesNotExist dans les vues/templates.
    """
    if not observation:
        return None
    try:
        return getattr(observation, related_name)
    except ObjectDoesNotExist:
        return None


def get_requested_type(data, observation):
    """
    Détermine le type d'observation demandé dans le POST,
    ou retombe sur le type de l'observation existante.
    """
    if data:
        return data.get("observation-type_observation") or data.get("type_observation")
    if observation:
        return observation.type_observation
    return None


def should_include_child_sections(requested_type, observation):
    """
    Les sections DPM / Antécédents personnels sont surtout utiles pour ENFANT.
    """
    if requested_type == "ENFANT":
        return True
    if observation and observation.type_observation == "ENFANT":
        return True
    return False


def build_forms(observation=None, data=None, files=None, include_observation_form=True):
    """
    Construit tous les formulaires de sections avec un prefix dédié.
    """
    requested_type = get_requested_type(data, observation)
    include_child_sections = should_include_child_sections(requested_type, observation)

    forms = {}

    if include_observation_form:
        forms["observation"] = ObservationMedicaleForm(
            data=data,
            files=files,
            instance=observation,
            prefix="observation",
        )

    for key, form_class, related_name, child_only in RELATED_FORMS:
        if child_only and not include_child_sections:
            continue

        related_instance = get_related_instance(observation, related_name)
        forms[key] = form_class(
            data=data,
            files=files,
            instance=related_instance,
            prefix=key,
        )

    return forms


def build_formsets(observation=None, data=None, files=None):
    """
    Construit les formsets.
    Pour une création non encore sauvegardée, on utilise instance=None.
    """
    instance = observation if observation and observation.pk else None

    return {
        "episodes": EpisodeHistoireMaladieFormSet(
            data=data,
            files=files,
            instance=instance,
            prefix="episodes",
        ),
        "hypotheses": HypotheseDiagnosticFormSet(
            data=data,
            files=files,
            instance=instance,
            prefix="hypotheses",
        ),
        "evolutions": EvolutionFormSet(
            data=data,
            files=files,
            instance=instance,
            prefix="evolutions",
        ),
    }


def forms_are_valid(forms):
    return all(form.is_valid() for form in forms.values())


def formsets_are_valid(formsets):
    return all(formset.is_valid() for formset in formsets.values())


def is_empty_value(value):
    """
    Permet de détecter si une valeur JSON/char/liste/dict est réellement vide.
    Utile pour éviter de créer des objets liés totalement vides.
    """
    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    if isinstance(value, (list, tuple, set)):
        return len(value) == 0

    if isinstance(value, dict):
        return all(is_empty_value(v) for v in value.values())

    # False, 0, Decimal("0"), etc. sont considérés comme valeurs non vides.
    return False


def form_has_meaningful_data(form):
    """
    Vérifie si le formulaire contient au moins une donnée utile.
    Cela évite de créer une section vide juste parce que le formulaire est présent.
    """
    if not form.is_bound:
        return False

    if not form.is_valid():
        return False

    # Si rien n'a changé par rapport à l'instance existante, on ne force pas la sauvegarde.
    if not form.has_changed():
        return False

    cleaned = getattr(form, "cleaned_data", {})
    if not cleaned:
        return False

    for field_name in form.fields.keys():
        if field_name not in cleaned:
            continue

        value = cleaned[field_name]
        if not is_empty_value(value):
            return True

    return False


def save_related_forms(forms, observation):
    """
    Sauvegarde les formulaires OneToOne liés à l'observation.
    """
    for key, form in forms.items():
        if key == "observation":
            continue

        if not form.is_valid():
            continue

        if not form_has_meaningful_data(form):
            continue

        obj = form.save(commit=False)
        obj.observation = observation
        obj.save()

        save_m2m = getattr(form, "save_m2m", None)
        if callable(save_m2m):
            save_m2m()


def save_formsets(formsets, observation):
    """
    Sauvegarde les formsets après avoir affecté l'observation parente.
    """
    for formset in formsets.values():
        formset.instance = observation
        formset.save()


def get_section_context(forms):
    """
    Petit helper pour faciliter l'accès aux formulaires dans le template.
    """
    return {
        "observation": forms.get("observation"),
        "antecedents_familiaux": forms.get("antecedents_familiaux"),
        "grossesse": forms.get("grossesse"),
        "accouchement": forms.get("accouchement"),
        "alimentation": forms.get("alimentation"),
        "vaccination": forms.get("vaccination"),
        "contexte_epidemiologique": forms.get("contexte_epidemiologique"),
        "fiche_sociale": forms.get("fiche_sociale"),
        "developpement_psychomoteur": forms.get("developpement_psychomoteur"),
        "antecedents_personnels": forms.get("antecedents_personnels"),
        "examen_clinique": forms.get("examen_clinique"),
        "traitement": forms.get("traitement"),
    }


def build_exam_forms(observation=None, data=None, files=None):
    """
    Construit :
    - le formulaire de base de l'examen clinique
    - tous les sous-formulaires d'appareil
    """
    examen = get_related_instance(observation, "examen_clinique")

    base_form = ExamenCliniqueBaseForm(
        data=data,
        files=files,
        instance=examen,
        prefix="examen_base",
    )

    subforms = {}

    for key, form_class, label in EXAM_SUBFORMS:
        json_data = getattr(examen, key, None) if examen else None

        subforms[key] = form_class(
            data=data,
            files=files,
            prefix=f"examen_{key}",
            json_data=json_data,
        )

    return base_form, subforms


def exam_forms_are_valid(base_form, subforms):
    if not base_form.is_valid():
        return False

    return all(form.is_valid() for form in subforms.values())


def get_exam_sections(exam_subforms):
    sections = []

    for key, form_class, label in EXAM_SUBFORMS:
        sections.append(
            {
                "key": key,
                "label": label,
                "form": exam_subforms.get(key),
            }
        )

    return sections


def save_exam_forms(base_form, subforms, observation):
    """
    Sauvegarde l'examen clinique de base,
    puis injecte les JSON des sous-formulaires d'appareil.
    """
    examen = base_form.save(commit=False)
    examen.observation = observation

    base_has_data = form_has_meaningful_data(base_form)
    subform_has_data = any(
        form_has_meaningful_data(form)
        for form in subforms.values()
    )

    # Si aucun examen n'est renseigné, on ne crée pas un objet vide.
    if not examen.pk and not base_has_data and not subform_has_data:
        return None

    examen.save()

    for key, form in subforms.items():
        if not form.is_valid():
            continue

        if form_has_meaningful_data(form):
            setattr(examen, key, form.get_json())

    examen.save()
    return examen


# ============================================================
# LISTE
# ============================================================

@require_GET
def observation_list(request):
    today = timezone.now().date()

    # Filtres
    q = request.GET.get("q", "").strip()
    observation_type = request.GET.get("type", "").strip()
    filtre_date = request.GET.get("date_filter", "").strip()
    statut_suivi = request.GET.get("suivi", "").strip()

    observations = ObservationMedicale.objects.all().order_by("-created_at")

    # Statistiques globales
    stats = {
        "total": ObservationMedicale.objects.count(),
        "total_nn": ObservationMedicale.objects.filter(type_observation="NN").count(),
        "total_enfant": ObservationMedicale.objects.filter(type_observation="ENFANT").count(),
        "total_jour": ObservationMedicale.objects.filter(created_at__date=today).count(),
        "avec_examens": ObservationMedicale.objects.filter(
            examens_physiques__isnull=False
        ).distinct().count(),
        "avec_rehydratation": ObservationMedicale.objects.filter(
            fiches_rehydratation__isnull=False
        ).distinct().count(),
        "avec_traitements": ObservationMedicale.objects.filter(
            traitements_ajustes__isnull=False
        ).distinct().count(),
    }

    # Application des filtres
    if q:
        observations = observations.filter(
            Q(nom__icontains=q)
            | Q(prenoms__icontains=q)
            | Q(numero_dossier__icontains=q)
            | Q(lit__icontains=q)
            | Q(motif_admission__icontains=q)
            | Q(diagnostic_retenu__icontains=q)
        )

    if observation_type:
        observations = observations.filter(type_observation=observation_type)

    if filtre_date == "today":
        observations = observations.filter(created_at__date=today)
    elif filtre_date == "week":
        week_ago = today - timezone.timedelta(days=7)
        observations = observations.filter(created_at__date__gte=week_ago)
    elif filtre_date == "month":
        month_ago = today - timezone.timedelta(days=30)
        observations = observations.filter(created_at__date__gte=month_ago)

    if statut_suivi == "avec_examens":
        observations = observations.filter(examens_physiques__isnull=False).distinct()
    elif statut_suivi == "avec_rehydratation":
        observations = observations.filter(fiches_rehydratation__isnull=False).distinct()
    elif statut_suivi == "avec_traitements":
        observations = observations.filter(traitements_ajustes__isnull=False).distinct()
    elif statut_suivi == "sans_suivi":
        observations = observations.filter(
            Q(examens_physiques__isnull=True)
            & Q(fiches_rehydratation__isnull=True)
            & Q(traitements_ajustes__isnull=True)
        ).distinct()

    # Annotations pour les compteurs par observation
    observations = observations.annotate(
        nb_examens=Count("examens_physiques", distinct=True),
        nb_rehydratation=Count("fiches_rehydratation", distinct=True),
        nb_traitements=Count("traitements_ajustes", distinct=True),
        nb_episodes=Count("episodes_histoire_maladie", distinct=True),
    )

    context = {
        "observations": observations,
        "stats": stats,
        "q": q,
        "observation_type": observation_type,
        "filtre_date": filtre_date,
        "statut_suivi": statut_suivi,
        "type_choices": C.TYPE_OBSERVATION_CHOICES,
    }

    return render(request, "patient/observation_list.html", context)


# ============================================================
# DETAIL
# ============================================================

@require_GET
def observation_detail(request, pk):
    observation = get_object_or_404(ObservationMedicale, pk=pk)

    # Récupérer toutes les données associées
    antecedents_familiaux = get_related_instance(observation, "antecedents_familiaux")
    grossesse = get_related_instance(observation, "grossesse")
    accouchement = get_related_instance(observation, "accouchement")
    alimentation = get_related_instance(observation, "alimentation")
    vaccination = get_related_instance(observation, "vaccination")
    contexte = get_related_instance(observation, "contexte_epidemiologique")
    fiche_sociale = get_related_instance(observation, "fiche_sociale")
    dpm = get_related_instance(observation, "developpement_psychomoteur")
    antecedents_personnels = get_related_instance(observation, "antecedents_personnels")
    examen_clinique = get_related_instance(observation, "examen_clinique")
    traitement = get_related_instance(observation, "traitement")

    episodes = observation.episodes_histoire_maladie.all()
    hypotheses = observation.hypotheses_diagnostiques.all()
    evolutions = observation.evolutions.all()
    examens_physiques = observation.examens_physiques.all()
    fiches_rehydratation = observation.fiches_rehydratation.all()
    traitements_ajustes = observation.traitements_ajustes.all()

    # Dernier traitement actif
    dernier_traitement = TraitementAjustement.dernier_pour_observation(observation)

        # Pré-formatter les données des appareils de l'examen clinique
    examen_appareils_formatted = []
    if examen_clinique:
        appareils_list = [
            ("pleuropulmonaire", "Appareil Pleuropulmonaire", "🫁"),
            ("cardiovasculaire", "Appareil Cardiovasculaire", "❤️"),
            ("digestif", "Appareil Digestif", "🫃"),
            ("neurologique", "Appareil Neurologique", "🧠"),
            ("orl", "Sphère ORL (Tête et Cou)", "👂"),
            ("cutaneomuqueux", "Revêtement Cutanéomuqueux", "🖐"),
            ("genitaux", "Appareils Génitaux", "⚧"),
            ("osteoarticulaire", "Appareil Ostéo-Articulaire", "🦴"),
        ]

        for appareil_key, appareil_title, appareil_icon in appareils_list:
            data = getattr(examen_clinique, appareil_key, None)

            if data and isinstance(data, dict):
                lines = format_exam_data(data)

                if lines:
                    # Séparer par catégorie
                    categories = []
                    current_category = None
                    current_lines = []

                    for line in lines:
                        if line.startswith("▸") or line.startswith("Chez"):
                            if current_category and current_lines:
                                categories.append({
                                    "title": current_category,
                                    "lines": current_lines,
                                })
                            current_category = line
                            current_lines = []
                        else:
                            current_lines.append(line)

                    if current_category and current_lines:
                        categories.append({
                            "title": current_category,
                            "lines": current_lines,
                        })

                    if not categories and lines:
                        categories.append({
                            "title": "",
                            "lines": lines,
                        })

                    examen_appareils_formatted.append({
                        "key": appareil_key,
                        "title": appareil_title,
                        "icon": appareil_icon,
                        "categories": categories,
                    })

    # Ajouter au context
    

    # Statistiques rapides
    stats = {
        "nb_examens": examens_physiques.count(),
        "nb_rehydratations": fiches_rehydratation.count(),
        "nb_traitements": traitements_ajustes.count(),
        "nb_episodes": episodes.count(),
        "dernier_examen": examens_physiques.first(),
        "derniere_rehydratation": fiches_rehydratation.first(),
        "dernier_traitement": dernier_traitement,
    }

    context = {
        "observation": observation,
        "antecedents_familiaux": antecedents_familiaux,
        "grossesse": grossesse,
        "accouchement": accouchement,
        "alimentation": alimentation,
        "vaccination": vaccination,
        "contexte": contexte,
        "fiche_sociale": fiche_sociale,
        "dpm": dpm,
        "antecedents_personnels": antecedents_personnels,
        "examen_clinique": examen_clinique,
        "traitement": traitement,
        "episodes": episodes,
        "hypotheses": hypotheses,
        "evolutions": evolutions,
        "examens_physiques": examens_physiques,
        "fiches_rehydratation": fiches_rehydratation,
        "traitements_ajustes": traitements_ajustes,
        "dernier_traitement": dernier_traitement,
        "stats": stats,
        "examen_appareils_formatted": examen_appareils_formatted,
    }

    return render(request, "patient/observation_detail.html", context)


# ============================================================
# CONFIGURATION DES FORMULAIRES LIÉS
# ============================================================

RELATED_FORMS_CONFIG = [
    # (clé dans le contexte, classe de formulaire, related_name sur ObservationMedicale, réservé enfant ?)
    ("antecedents_familiaux", AntecedentsFamiliauxForm, "antecedents_familiaux", False),
    ("grossesse", GrossesseForm, "grossesse", False),
    ("accouchement", AccouchementForm, "accouchement", False),
    ("alimentation", AlimentationForm, "alimentation", False),
    ("vaccination", VaccinationForm, "vaccination", False),
    ("contexte_epidemiologique", ContexteEpidemiologiqueForm, "contexte_epidemiologique", False),
    ("fiche_sociale", FicheSocialeForm, "fiche_sociale", False),
    ("developpement_psychomoteur", DeveloppementPsychomoteurForm, "developpement_psychomoteur", True),
    ("antecedents_personnels", AntecedentsPersonnelsForm, "antecedents_personnels", True),
    ("examen_clinique", ExamenCliniqueForm, "examen_clinique", False),
    ("traitement", TraitementForm, "traitement", False),
]


# ============================================================
# CREATE / UPDATE
# ============================================================

@require_http_methods(["GET", "POST"])
def observation_create(request):
    """
    Crée instantanément un brouillon d'observation et redirige vers la page de modification.
    Cela garantit que l'observation a un ID pour les relations OneToOne et les requêtes AJAX.
    """
    obs = ObservationMedicale.objects.create(
        type_observation="NN",
        nom="Nouveau Patient (Brouillon)",
        prenoms="",
        sexe="M",
        age_valeur=0,
        age_unite="jour",
    )
    messages.info(request, "Brouillon créé. Remplissez les sections à votre rythme, tout est sauvegardé automatiquement.")
    return redirect('observation_update', pk=obs.pk)


@require_http_methods(["GET", "POST"])
def observation_form(request, pk=None):
    """
    Vue principale de modification d'une observation médicale.
    Gère :
    - La création automatique de brouillon si pk=None
    - L'affichage par onglets (le template gère la présentation)
    - La sauvegarde AJAX (retourne du JSON si requête AJAX)
    - Tous les formulaires liés et formsets
    """

    # ----------------------------------------------------------
    # 1. SI AUCUN PK : CRÉER UN BROUILLON ET REDIRIGER
    # ----------------------------------------------------------
    if pk is None:
        obs = ObservationMedicale.objects.create(
            type_observation="NN",
            nom="Nouveau Patient (Brouillon)",
            prenoms="",
            sexe="M",
            age_valeur=0,
            age_unite="jour",
        )
        messages.info(
            request,
            "Brouillon créé. Remplissez les sections à votre rythme, tout est sauvegardé automatiquement.",
        )
        return redirect("patient:observation_update", pk=obs.pk)

    # ----------------------------------------------------------
    # 2. RÉCUPÉRER L'OBSERVATION
    # ----------------------------------------------------------
    observation = get_object_or_404(ObservationMedicale, pk=pk)
    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or request.GET.get("ajax")
    )

    # ----------------------------------------------------------
    # 3. DÉTERMINER LE TYPE (NN / ENFANT)
    # ----------------------------------------------------------
    requested_type = get_requested_type(request.POST if request.method == "POST" else None, observation)
    include_child_sections = should_include_child_sections(requested_type, observation)

    # ----------------------------------------------------------
    # 4. CONSTRUIRE LES FORMULAIRES PRINCIPAUX
    # ----------------------------------------------------------
    forms = {}

    # Formulaire principal (état civil)
    forms["observation"] = ObservationMedicaleForm(
        request.POST or None,
        instance=observation,
        prefix="observation",
    )

    # Formulaires liés (OneToOne)
    for key, form_class, related_name, child_only in RELATED_FORMS_CONFIG:
        if child_only and not include_child_sections:
            continue

        instance = get_related_instance(observation, related_name)
        forms[key] = form_class(
            request.POST or None,
            instance=instance,
            prefix=key,
        )

    # ----------------------------------------------------------
    # 5. SOUS-FORMULAIRE : SÉROLOGIES DE GROSSESSE
    # ----------------------------------------------------------
    grossesse_instance = get_related_instance(observation, "grossesse")
    serologies_data = getattr(grossesse_instance, "serologies", {}) if grossesse_instance else {}

    forms["serologies"] = SerologiesForm(
        data=request.POST if request.method == "POST" else None,
        json_data=serologies_data,
        prefix="serologies",
    )

    # ----------------------------------------------------------
    # 6. SOUS-FORMULAIRES : EXAMENS PAR APPAREIL
    # ----------------------------------------------------------
    examen_instance = get_related_instance(observation, "examen_clinique")
    exam_subforms = {}

    for key, form_class, label in EXAM_SUBFORMS:
        json_data = getattr(examen_instance, key, {}) if examen_instance else {}
        exam_subforms[key] = form_class(
            data=request.POST if request.method == "POST" else None,
            json_data=json_data,
            prefix=f"exam_{key}",
        )

    # ----------------------------------------------------------
    # 7. FORMSETS (RELATIONS ONE-TO-MANY)
    # ----------------------------------------------------------
    formsets = {
        "episodes": EpisodeHistoireMaladieFormSet(
            request.POST or None,
            instance=observation,
            prefix="episodes",
        ),
        "hypotheses": HypotheseDiagnosticFormSet(
            request.POST or None,
            instance=observation,
            prefix="hypotheses",
        ),
        "evolutions": EvolutionFormSet(
            request.POST or None,
            instance=observation,
            prefix="evolutions",
        ),
    }

    # ----------------------------------------------------------
    # 8. TRAITEMENT DU POST
    # ----------------------------------------------------------
    if request.method == "POST":
        # Vérifier la validité de tous les formulaires
        all_forms_valid = all(form.is_valid() for form in forms.values())
        all_exam_valid = all(form.is_valid() for form in exam_subforms.values())
        all_formsets_valid = all(fs.is_valid() for fs in formsets.values())

        if all_forms_valid and all_exam_valid and all_formsets_valid:
            # ------------------------------------------------------
            # SAUVEGARDE
            # ------------------------------------------------------
            with transaction.atomic():
                # Observation principale
                obs = forms["observation"].save()

                # Formulaires liés classiques
                for key, form in forms.items():
                    if key == "observation":
                        continue

                    # Cas spécial : sous-formulaire sérologies
                    if key == "serologies":
                        if form.has_changed():
                            grossesse_obj = get_related_instance(obs, "grossesse")
                            if not grossesse_obj:
                                grossesse_obj = Grossesse(observation=obs)
                            grossesse_obj.serologies = form.get_json()
                            grossesse_obj.save()
                        continue

                    # Cas normal : formulaires classiques
                    if form.has_changed():
                        obj = form.save(commit=False)
                        obj.observation = obs
                        obj.save()

                # Examen clinique de base + sous-formulaires par appareil
                examen_obj = get_related_instance(obs, "examen_clinique")
                if not examen_obj:
                    examen_obj = ExamenClinique(observation=obs)

                # Copier les données du formulaire de base (biométrie, signes, etc.)
                examen_form = forms.get("examen_clinique")
                if examen_form and examen_form.has_changed():
                    for field_name, value in examen_form.cleaned_data.items():
                        setattr(examen_obj, field_name, value)

                # Sauvegarder les sous-formulaires d'examen par appareil
                for key, form in exam_subforms.items():
                    if form.has_changed():
                        setattr(examen_obj, key, form.get_json())

                examen_obj.save()

                # Formsets
                for fs in formsets.values():
                    fs.instance = obs
                    fs.save()

            # ------------------------------------------------------
            # RÉPONSE AJAX OU REDIRECTION
            # ------------------------------------------------------
            if is_ajax:
                return JsonResponse({
                    "status": "success",
                    "message": "Sauvegardé avec succès",
                })

            messages.success(request, "L'observation a été enregistrée avec succès.")
            return redirect("patient:observation_detail", pk=obs.pk)

        else:
            # ------------------------------------------------------
            # ERREURS DE VALIDATION
            # ------------------------------------------------------
            if is_ajax:
                errors = {}

                # Erreurs des formulaires classiques
                for k, v in forms.items():
                    if v.errors:
                        errors[k] = v.errors.get_json_data()

                # Erreurs des sous-formulaires d'examen
                for k, v in exam_subforms.items():
                    if v.errors:
                        errors[f"exam_{k}"] = v.errors.get_json_data()

                # Erreurs des formsets (structure différente)
                for k, v in formsets.items():
                    if v.errors or v.non_form_errors():
                        errors[k] = {
                            "form_errors": [
                                e.get_json_data() if hasattr(e, "get_json_data") else e
                                for e in v.errors
                            ],
                            "non_form_errors": list(v.non_form_errors()),
                        }

                return JsonResponse(
                    {"status": "error", "errors": errors},
                    status=400,
                )

            messages.error(
                request,
                "Le formulaire contient des erreurs. Veuillez vérifier les champs.",
            )

    # ----------------------------------------------------------
    # 9. CONTEXTE ET RENDU
    # ----------------------------------------------------------
    context = {
        "observation": observation,
        "forms": forms,
        "formsets": formsets,
        "title": "Modifier l'observation" if observation else "Nouvelle observation",
        "is_enfant": include_child_sections,
        "serologies_form": forms.get("serologies"),
        "exam_subforms": exam_subforms,
    }

    return render(request, "patient/observation_form.html", context)


# ============================================================
# DELETE
# ============================================================

@require_POST
def observation_delete(request, pk):
    observation = get_object_or_404(ObservationMedicale, pk=pk)
    observation.delete()

    messages.success(request, "L'observation a été supprimée.")
    return redirect(reverse("patient:observation_list"))


# ============================================================
# GÉNÉRATION DOCX
# ============================================================

from .services.docx_generator import generate_observation_docx

@require_GET
def observation_generate_docx(request, pk):
    observation = get_object_or_404(ObservationMedicale, pk=pk)

    try:
        return generate_observation_docx(observation)
    except FileNotFoundError as exc:
        messages.error(request, str(exc))
        return redirect("patient:observation_detail", pk=pk)

# ============================================================
# EXAMENS PHYSIQUES DE SUIVI
# ============================================================

# Liste des sous-formulaires d'appareils
EXAM_SUBFORMS_LIST = [
    ("pleuropulmonaire", PleuroPulmonaireExamenForm, "Appareil Pleuropulmonaire"),
    ("cardiovasculaire", CardiovasculaireExamenForm, "Appareil Cardiovasculaire"),
    ("digestif", DigestifExamenForm, "Appareil Digestif"),
    ("neurologique", NeurologiqueExamenForm, "Appareil Neurologique"),
    ("orl", ORLExamenForm, "Sphère ORL (Tête et Cou)"),
    ("cutaneomuqueux", CutaneomuqueuxExamenForm, "Revêtement Cutanéomuqueux"),
    ("genitaux", GenitauxExamenForm, "Appareils Génitaux"),
    ("osteoarticulaire", OsteoarticulaireExamenForm, "Appareil Ostéo-Articulaire"),
]


def build_exam_subforms(examen_instance=None, data=None, files=None):
    """
    Construit les sous-formulaires d'appareils pour un examen physique.
    """
    subforms = {}
    donnees_appareils = {}

    if examen_instance and examen_instance.donnees_appareils:
        donnees_appareils = examen_instance.donnees_appareils

    for key, form_class, label in EXAM_SUBFORMS_LIST:
        json_data = donnees_appareils.get(key, {})
        subforms[key] = form_class(
            data=data,
            files=files,
            json_data=json_data,
            prefix=f"exam_{key}",
        )

    return subforms


@require_http_methods(["GET", "POST"])
def examen_physique_create(request, observation_pk):
    observation = get_object_or_404(ObservationMedicale, pk=observation_pk)

    if request.method == "POST":
        form = ExamenPhysiqueForm(request.POST, request.FILES)
        exam_subforms = build_exam_subforms(data=request.POST, files=request.FILES)

        # Vérifier la validité de tous les formulaires
        all_valid = form.is_valid()
        for key, subform in exam_subforms.items():
            if not subform.is_valid():
                all_valid = False

        if all_valid:
            examen = form.save(commit=False)
            examen.observation = observation

            # Combiner les données des sous-formulaires dans donnees_appareils
            donnees_appareils = {}
            for key, subform in exam_subforms.items():
                donnees_appareils[key] = subform.get_json()

            examen.donnees_appareils = donnees_appareils
            examen.save()

            messages.success(request, "L'examen physique a été enregistré avec succès.")
            return redirect("patient:examen_physique_list", observation_pk=observation.pk)
        else:
            messages.error(request, "Le formulaire contient des erreurs.")
    else:
        form = ExamenPhysiqueForm()
        exam_subforms = build_exam_subforms()

    context = {
        "observation": observation,
        "form": form,
        "exam_subforms": exam_subforms,
        "exam_subforms_list": EXAM_SUBFORMS_LIST,
        "title": "Nouvel examen physique",
    }

    return render(request, "patient/examen_physique_form.html", context)


@require_http_methods(["GET", "POST"])
def examen_physique_update(request, pk):
    examen = get_object_or_404(ExamenPhysique, pk=pk)
    observation = examen.observation

    if request.method == "POST":
        form = ExamenPhysiqueForm(request.POST, request.FILES, instance=examen)
        exam_subforms = build_exam_subforms(
            examen_instance=examen,
            data=request.POST,
            files=request.FILES,
        )

        # Vérifier la validité de tous les formulaires
        all_valid = form.is_valid()
        for key, subform in exam_subforms.items():
            if not subform.is_valid():
                all_valid = False

        if all_valid:
            examen = form.save(commit=False)

            # Combiner les données des sous-formulaires dans donnees_appareils
            donnees_appareils = {}
            for key, subform in exam_subforms.items():
                donnees_appareils[key] = subform.get_json()

            examen.donnees_appareils = donnees_appareils
            examen.save()

            messages.success(request, "L'examen physique a été modifié avec succès.")
            return redirect("patient:examen_physique_list", observation_pk=observation.pk)
        else:
            messages.error(request, "Le formulaire contient des erreurs.")
    else:
        form = ExamenPhysiqueForm(instance=examen)
        exam_subforms = build_exam_subforms(examen_instance=examen)

    context = {
        "observation": observation,
        "form": form,
        "exam_subforms": exam_subforms,
        "exam_subforms_list": EXAM_SUBFORMS_LIST,
        "title": f"Modifier l'examen du {examen.date_heure.strftime('%d/%m/%Y %H:%M')}",
    }

    return render(request, "patient/examen_physique_form.html", context)


from .services.docx_generator import format_exam_data


@require_GET
def examen_physique_list(request, observation_pk):
    observation = get_object_or_404(ObservationMedicale, pk=observation_pk)
    examens = observation.examens_physiques.all().order_by("-date_heure")

    # Pré-formatter chaque examen pour n'afficher que les champs évalués
    examens_formatted = []

    for examen in examens:
        examen_data = {
            "instance": examen,
            "appareils": [],
            "has_details": False,
        }

        donnees_appareils = examen.donnees_appareils or {}

        appareils_list = [
            ("pleuropulmonaire", "Appareil Pleuropulmonaire", "🫁"),
            ("cardiovasculaire", "Appareil Cardiovasculaire", "❤️"),
            ("digestif", "Appareil Digestif", "🫃"),
            ("neurologique", "Appareil Neurologique", "🧠"),
            ("orl", "Sphère ORL (Tête et Cou)", "👂"),
            ("cutaneomuqueux", "Revêtement Cutanéomuqueux", "🖐"),
            ("genitaux", "Appareils Génitaux", "⚧"),
            ("osteoarticulaire", "Appareil Ostéo-Articulaire", "🦴"),
        ]

        for appareil_key, appareil_title, appareil_icon in appareils_list:
            data = donnees_appareils.get(appareil_key, {})

            if data and isinstance(data, dict):
                # format_exam_data ne retourne QUE les lignes non vides
                lines = format_exam_data(data)

                if lines:
                    # Séparer les lignes par catégorie
                    categories = []
                    current_category = None
                    current_lines = []

                    for line in lines:
                        # Les lignes de catégorie commencent par "▸"
                        if line.startswith("▸") or line.startswith("Chez"):
                            if current_category and current_lines:
                                categories.append({
                                    "title": current_category,
                                    "lines": current_lines,
                                })
                            current_category = line
                            current_lines = []
                        else:
                            current_lines.append(line)

                    # Ajouter la dernière catégorie
                    if current_category and current_lines:
                        categories.append({
                            "title": current_category,
                            "lines": current_lines,
                        })

                    # S'il n'y a pas de catégories mais des lignes directes
                    if not categories and lines:
                        categories.append({
                            "title": "",
                            "lines": lines,
                        })

                    examen_data["appareils"].append({
                        "key": appareil_key,
                        "title": appareil_title,
                        "icon": appareil_icon,
                        "categories": categories,
                    })
                    examen_data["has_details"] = True

        examens_formatted.append(examen_data)

    context = {
        "observation": observation,
        "examens_formatted": examens_formatted,
        "examens_count": examens.count(),
    }

    return render(request, "patient/examen_physique_list.html", context)


@require_POST
def examen_physique_delete(request, pk):
    examen = get_object_or_404(ExamenPhysique, pk=pk)
    observation_pk = examen.observation_id

    examen.delete()

    messages.success(
        request,
        "L'examen physique de suivi a été supprimé.",
    )

    return redirect(
        reverse(
            "patient:examen_physique_list",
            kwargs={"observation_pk": observation_pk},
        )
    )


# ============================================================
# FICHES DE RÉHYDRATATION
# ============================================================

@require_GET
def fiche_rehydratation_list(request, observation_pk):
    observation = get_object_or_404(ObservationMedicale, pk=observation_pk)
    fiches = observation.fiches_rehydratation.all()

    context = {
        "observation": observation,
        "fiches": fiches,
    }

    return render(request, "patient/fiche_rehydratation_list.html", context)


@require_http_methods(["GET", "POST"])
def fiche_rehydratation_create(request, observation_pk):
    observation = get_object_or_404(ObservationMedicale, pk=observation_pk)

    if request.method == "POST":
        form = FicheRehydratationForm(request.POST)

        if form.is_valid():
            fiche = form.save(commit=False)
            fiche.observation = observation

            formset = EvaluationHoraireRehydratationFormSet(
                request.POST,
                instance=fiche,
                prefix="evaluations",
            )

            if formset.is_valid():
                fiche.save()
                formset.save()

                messages.success(
                    request,
                    "La fiche de réhydratation a été enregistrée.",
                )

                return redirect(
                    reverse(
                        "patient:fiche_rehydratation_list",
                        kwargs={"observation_pk": observation.pk},
                    )
                )

            messages.error(
                request,
                "Le formulaire principal est valide, mais les évaluations horaires contiennent des erreurs.",
            )

        else:
            formset = EvaluationHoraireRehydratationFormSet(
                request.POST,
                instance=FicheRehydratation(observation=observation),
                prefix="evaluations",
            )

            messages.error(
                request,
                "Le formulaire de réhydratation contient des erreurs.",
            )

    else:
        form = FicheRehydratationForm()
        formset = EvaluationHoraireRehydratationFormSet(
            instance=FicheRehydratation(observation=observation),
            prefix="evaluations",
        )

    context = {
        "observation": observation,
        "form": form,
        "formset": formset,
        "title": "Ajouter une fiche de réhydratation",
    }

    return render(request, "patient/fiche_rehydratation_form.html", context)


@require_http_methods(["GET", "POST"])
def fiche_rehydratation_update(request, pk):
    fiche = get_object_or_404(FicheRehydratation, pk=pk)
    observation = fiche.observation

    if request.method == "POST":
        form = FicheRehydratationForm(request.POST, instance=fiche)

        if form.is_valid():
            fiche = form.save(commit=False)

            formset = EvaluationHoraireRehydratationFormSet(
                request.POST,
                instance=fiche,
                prefix="evaluations",
            )

            if formset.is_valid():
                fiche.save()
                formset.save()

                messages.success(
                    request,
                    "La fiche de réhydratation a été modifiée.",
                )

                return redirect(
                    reverse(
                        "patient:fiche_rehydratation_list",
                        kwargs={"observation_pk": observation.pk},
                    )
                )

            messages.error(
                request,
                "Le formulaire principal est valide, mais les évaluations horaires contiennent des erreurs.",
            )

        else:
            formset = EvaluationHoraireRehydratationFormSet(
                request.POST,
                instance=fiche,
                prefix="evaluations",
            )

            messages.error(
                request,
                "Le formulaire de réhydratation contient des erreurs.",
            )

    else:
        form = FicheRehydratationForm(instance=fiche)
        formset = EvaluationHoraireRehydratationFormSet(
            instance=fiche,
            prefix="evaluations",
        )

    context = {
        "observation": observation,
        "form": form,
        "formset": formset,
        "fiche": fiche,
        "title": "Modifier une fiche de réhydratation",
    }

    return render(request, "patient/fiche_rehydratation_form.html", context)


@require_POST
def fiche_rehydratation_delete(request, pk):
    fiche = get_object_or_404(FicheRehydratation, pk=pk)
    observation_pk = fiche.observation_id

    fiche.delete()

    messages.success(
        request,
        "La fiche de réhydratation a été supprimée.",
    )

    return redirect(
        reverse(
            "patient:fiche_rehydratation_list",
            kwargs={"observation_pk": observation_pk},
        )
    )


# ============================================================
# TRAITEMENTS AJUSTÉS ET TRACÉS
# ============================================================

def get_initial_lignes_depuis_dernier(observation):
    """
    Pré-remplit les lignes du nouvel ajustement avec celles
    de la dernière version, sauf si la dernière version est un arrêt.
    """
    dernier = TraitementAjustement.dernier_pour_observation(observation)

    if not dernier:
        return []

    if dernier.est_arret:
        return []

    initial = []

    for ligne in dernier.lignes.all():
        initial.append(
            {
                "type_ligne": ligne.type_ligne,
                "nom": ligne.nom,
                "dose": ligne.dose,
                "voie": ligne.voie,
                "frequence": ligne.frequence,
                "duree": ligne.duree,
                "date_debut": ligne.date_debut,
                "date_fin": ligne.date_fin,
                "instructions": ligne.instructions,
            }
        )

    return initial


def ligne_traitement_form_has_data(form):
    """
    Vérifie qu'une ligne de traitement contient au moins un nom.
    Cela évite de sauver des lignes vides.
    """
    if not form.is_bound:
        return False

    cleaned = getattr(form, "cleaned_data", {})

    if not cleaned:
        return False

    if cleaned.get("DELETE"):
        return False

    if not cleaned.get("nom"):
        return False

    return True


@require_GET
def traitement_ajustement_list(request, observation_pk):
    observation = get_object_or_404(ObservationMedicale, pk=observation_pk)
    ajustements = observation.traitements_ajustes.all()
    dernier = TraitementAjustement.dernier_pour_observation(observation)

    context = {
        "observation": observation,
        "ajustements": ajustements,
        "dernier": dernier,
    }

    return render(request, "patient/traitement_ajustement_list.html", context)


@require_GET
def traitement_ajustement_detail(request, pk):
    ajustement = get_object_or_404(TraitementAjustement, pk=pk)
    observation = ajustement.observation
    lignes = ajustement.lignes.all()

    dernier = TraitementAjustement.dernier_pour_observation(observation)
    est_dernier = bool(dernier and dernier.pk == ajustement.pk)

    context = {
        "observation": observation,
        "ajustement": ajustement,
        "lignes": lignes,
        "est_dernier": est_dernier,
    }

    return render(request, "patient/traitement_ajustement_detail.html", context)


@require_http_methods(["GET", "POST"])
def traitement_ajustement_create(request, observation_pk):
    observation = get_object_or_404(ObservationMedicale, pk=observation_pk)

    if request.method == "POST":
        form = TraitementAjustementForm(request.POST)

        if form.is_valid():
            ajustement = form.save(commit=False)
            ajustement.observation = observation

            formset = LigneTraitementFormSet(
                request.POST,
                instance=ajustement,
                prefix="lignes",
            )

            if formset.is_valid():
                ajustement.save()

                # Sauvegarde manuelle des lignes pour garantir
                # la reprise des lignes pré-remplies.
                for ligne_form in formset.forms:
                    if ligne_traitement_form_has_data(ligne_form):
                        ligne = ligne_form.save(commit=False)
                        ligne.ajustement = ajustement
                        ligne.save()

                messages.success(
                    request,
                    "Le nouvel ajustement de traitement a été enregistré.",
                )

                return redirect(
                    reverse(
                        "traitement_ajustement_detail",
                        kwargs={"pk": ajustement.pk},
                    )
                )

            messages.error(
                request,
                "Les lignes de traitement contiennent des erreurs.",
            )

        else:
            formset = LigneTraitementFormSet(
                request.POST,
                instance=TraitementAjustement(observation=observation),
                prefix="lignes",
            )

            messages.error(
                request,
                "Le formulaire d'ajustement contient des erreurs.",
            )

    else:
        initial_lignes = get_initial_lignes_depuis_dernier(observation)

        form = TraitementAjustementForm()
        formset = LigneTraitementFormSet(
            instance=TraitementAjustement(observation=observation),
            prefix="lignes",
            initial=initial_lignes,
        )

    context = {
        "observation": observation,
        "form": form,
        "formset": formset,
        "title": "Nouvel ajustement de traitement",
    }

    return render(request, "patient/traitement_ajustement_form.html", context)


@require_http_methods(["GET", "POST"])
def traitement_ajustement_update(request, pk):
    ajustement = get_object_or_404(TraitementAjustement, pk=pk)
    observation = ajustement.observation

    dernier = TraitementAjustement.dernier_pour_observation(observation)

    if not dernier or dernier.pk != ajustement.pk:
        messages.error(
            request,
            "Seule la dernière version du traitement peut être modifiée.",
        )

        return redirect(
            reverse(
                "traitement_ajustement_list",
                kwargs={"observation_pk": observation.pk},
            )
        )

    if request.method == "POST":
        form = TraitementAjustementForm(request.POST, instance=ajustement)

        if form.is_valid():
            ajustement = form.save(commit=False)

            formset = LigneTraitementFormSet(
                request.POST,
                instance=ajustement,
                prefix="lignes",
            )

            if formset.is_valid():
                ajustement.save()
                formset.save()

                messages.success(
                    request,
                    "L'ajustement de traitement a été modifié.",
                )

                return redirect(
                    reverse(
                        "traitement_ajustement_detail",
                        kwargs={"pk": ajustement.pk},
                    )
                )

            messages.error(
                request,
                "Les lignes de traitement contiennent des erreurs.",
            )

        else:
            formset = LigneTraitementFormSet(
                request.POST,
                instance=ajustement,
                prefix="lignes",
            )

            messages.error(
                request,
                "Le formulaire d'ajustement contient des erreurs.",
            )

    else:
        form = TraitementAjustementForm(instance=ajustement)
        formset = LigneTraitementFormSet(
            instance=ajustement,
            prefix="lignes",
        )

    context = {
        "observation": observation,
        "form": form,
        "formset": formset,
        "ajustement": ajustement,
        "title": f"Modifier traitement v{ajustement.version}",
    }

    return render(request, "patient/traitement_ajustement_form.html", context)


@require_POST
def traitement_ajustement_delete(request, pk):
    ajustement = get_object_or_404(TraitementAjustement, pk=pk)
    observation = ajustement.observation

    dernier = TraitementAjustement.dernier_pour_observation(observation)

    if not dernier or dernier.pk != ajustement.pk:
        messages.error(
            request,
            "Seule la dernière version du traitement peut être supprimée.",
        )

        return redirect(
            reverse(
                "traitement_ajustement_list",
                kwargs={"observation_pk": observation.pk},
            )
        )

    ajustement.delete()

    messages.success(
        request,
        "L'ajustement de traitement a été supprimé.",
    )

    return redirect(
        reverse(
            "traitement_ajustement_list",
            kwargs={"observation_pk": observation.pk},
        )
    )


