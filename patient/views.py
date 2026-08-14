# views.py
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .exam_forms import EXAM_SUBFORMS

from . import constants as C

from .models import (
    ObservationMedicale,
    TraitementAjustement,
    LigneTraitement,
)
from .forms import (
    TraitementAjustementForm,
    LigneTraitementForm,
    LigneTraitementFormSet,

    FicheRehydratationForm,
    EvaluationHoraireRehydratationFormSet,
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
    ExamenCliniqueBaseForm,
    HypotheseDiagnosticFormSet,
    TraitementForm,
    EvolutionFormSet,
    EpisodeHistoireMaladieFormSet,
    ExamenPhysiqueForm,
    
)
from .models import ObservationMedicale, ExamenPhysique, FicheRehydratation, EvaluationHoraireRehydratation


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
    observations = ObservationMedicale.objects.all().order_by("-created_at")

    q = request.GET.get("q", "").strip()
    observation_type = request.GET.get("type", "").strip()

    if q:
        observations = observations.filter(
            Q(nom__icontains=q)
            | Q(prenoms__icontains=q)
            | Q(numero_dossier__icontains=q)
            | Q(motif_admission__icontains=q)
            | Q(diagnostic_retenu__icontains=q)
        )

    if observation_type:
        observations = observations.filter(type_observation=observation_type)

    context = {
        "observations": observations,
        "q": q,
        "observation_type": observation_type,
        "type_choices": C.TYPE_OBSERVATION_CHOICES,
    }

    return render(request, "patient/observation_list.html", context)


# ============================================================
# DETAIL
# ============================================================

@require_GET
def observation_detail(request, pk):
    observation = get_object_or_404(ObservationMedicale, pk=pk)

    sections = {}
    for key, form_class, related_name, child_only in RELATED_FORMS:
        sections[key] = get_related_instance(observation, related_name)

    episodes = observation.episodes_histoire_maladie.all()
    hypotheses = observation.hypotheses_diagnostiques.all()
    evolutions = observation.evolutions.all()

    context = {
        "observation": observation,
        "sections": sections,
        "section_labels": SECTION_LABELS,
        "episodes": episodes,
        "hypotheses": hypotheses,
        "evolutions": evolutions,
    }

    return render(request, "patient/observation_detail.html", context)


# ============================================================
# CREATE / UPDATE
# ============================================================

@require_http_methods(["GET", "POST"])
def observation_form(request, pk=None):
    existing_observation = None

    if pk:
        existing_observation = get_object_or_404(ObservationMedicale, pk=pk)

    if request.method == "POST":
        observation_form = ObservationMedicaleForm(
            request.POST,
            request.FILES,
            instance=existing_observation,
            prefix="observation",
        )

        if observation_form.is_valid():
            candidate_observation = observation_form.save(commit=False)

            forms = build_forms(
                observation=candidate_observation,
                data=request.POST,
                files=request.FILES,
                include_observation_form=False,
            )
            forms["observation"] = observation_form

            formsets = build_formsets(
                observation=candidate_observation,
                data=request.POST,
                files=request.FILES,
            )

            examen_base_form, exam_subforms = build_exam_forms(
                observation=candidate_observation,
                data=request.POST,
                files=request.FILES,
            )

            if (
                forms_are_valid(forms)
                and formsets_are_valid(formsets)
                and exam_forms_are_valid(examen_base_form, exam_subforms)
            ):
                with transaction.atomic():
                    candidate_observation.save()
                    save_related_forms(forms, candidate_observation)
                    save_exam_forms(examen_base_form, exam_subforms, candidate_observation)
                    save_formsets(formsets, candidate_observation)

                messages.success(
                    request,
                    "L'observation a été enregistrée avec succès.",
                )

                return redirect(
                    reverse(
                        "patient:observation_detail",
                        kwargs={"pk": candidate_observation.pk},
                    )
                )

            messages.error(
                request,
                "Le formulaire principal est valide, mais certaines sections contiennent des erreurs.",
            )

            context_observation = candidate_observation

        else:
            forms = build_forms(
                observation=existing_observation,
                data=request.POST,
                files=request.FILES,
                include_observation_form=True,
            )
            forms["observation"] = observation_form

            formsets = build_formsets(
                observation=existing_observation,
                data=request.POST,
                files=request.FILES,
            )

            examen_base_form, exam_subforms = build_exam_forms(
                observation=existing_observation,
                data=request.POST,
                files=request.FILES,
            )

            messages.error(
                request,
                "Le formulaire principal contient des erreurs.",
            )

            context_observation = existing_observation

    else:
        forms = build_forms(observation=existing_observation)
        formsets = build_formsets(observation=existing_observation)

        examen_base_form, exam_subforms = build_exam_forms(
            observation=existing_observation,
        )

        context_observation = existing_observation

    context = {
        "observation": context_observation,
        "forms": forms,
        "formsets": formsets,
        "section_forms": get_section_context(forms),
        "section_labels": SECTION_LABELS,
        "examen_base_form": examen_base_form,
        "exam_sections": get_exam_sections(exam_subforms),
        "is_update": bool(existing_observation and existing_observation.pk),
        "title": "Modifier l'observation" if existing_observation else "Nouvelle observation",
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
    return generate_observation_docx(observation)

# ============================================================
# EXAMENS PHYSIQUES DE SUIVI
# ============================================================

@require_GET
def examen_physique_list(request, observation_pk):
    observation = get_object_or_404(ObservationMedicale, pk=observation_pk)
    examens = observation.examens_physiques.all()

    context = {
        "observation": observation,
        "examens": examens,
    }

    return render(request, "patient/examen_physique_list.html", context)


@require_http_methods(["GET", "POST"])
def examen_physique_create(request, observation_pk):
    observation = get_object_or_404(ObservationMedicale, pk=observation_pk)

    if request.method == "POST":
        form = ExamenPhysiqueForm(request.POST)

        if form.is_valid():
            examen = form.save(commit=False)
            examen.observation = observation
            examen.save()

            messages.success(
                request,
                "L'examen physique de suivi a été enregistré.",
            )

            return redirect(
                reverse(
                    "patient:examen_physique_list",
                    kwargs={"observation_pk": observation.pk},
                )
            )

        messages.error(
            request,
            "Le formulaire contient des erreurs.",
        )

    else:
        form = ExamenPhysiqueForm()

    context = {
        "observation": observation,
        "form": form,
        "title": "Ajouter un examen physique de suivi",
    }

    return render(request, "patient/examen_physique_form.html", context)


@require_http_methods(["GET", "POST"])
def examen_physique_update(request, pk):
    examen = get_object_or_404(ExamenPhysique, pk=pk)
    observation = examen.observation

    if request.method == "POST":
        form = ExamenPhysiqueForm(request.POST, instance=examen)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "L'examen physique de suivi a été modifié.",
            )

            return redirect(
                reverse(
                    "patient:examen_physique_list",
                    kwargs={"observation_pk": observation.pk},
                )
            )

        messages.error(
            request,
            "Le formulaire contient des erreurs.",
        )

    else:
        form = ExamenPhysiqueForm(instance=examen)

    context = {
        "observation": observation,
        "form": form,
        "examen": examen,
        "title": "Modifier un examen physique de suivi",
    }

    return render(request, "patient/examen_physique_form.html", context)


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


