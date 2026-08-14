# forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.forms import inlineformset_factory


from . import constants as C
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


# ============================================================
# WIDGETS CUSTOM POUR JSONFIELD (LISTES COCHABLES)
# ============================================================

class JSONMultipleChoiceField(forms.MultipleChoiceField):
    """
    Champ de choix multiples qui stocke en JSON (liste de strings).
    Utilisé pour tares_familiales, vaccins_recus, signes_3a2s, etc.
    """
    
    def to_python(self, value):
        if not value:
            return []
        return super().to_python(value)
    
    def validate(self, value):
        super().validate(value)
        # Validation custom si nécessaire


# ============================================================
# 1. OBSERVATION MEDICALE (ÉTAT CIVIL DE BASE)
# ============================================================

class ObservationMedicaleForm(forms.ModelForm):
    """
    Formulaire pour l'état civil et les informations de base.
    Seuls ces champs sont requis.
    """
    
    class Meta:
        model = ObservationMedicale
        fields = [
            'type_observation',
            'nom',
            'prenoms',
            'sexe',
            'age_valeur',
            'age_unite',
            'date_naissance',
            'adresse',
            'telephone',
            'lit',
            'numero_dossier',
            'date_admission',
            'motif_admission',
            'diagnostic_retenu',
        ]
        widgets = {
            'type_observation': forms.RadioSelect,
            'sexe': forms.RadioSelect,
            'age_unite': forms.RadioSelect,
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'date_admission': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 2}),
            'motif_admission': forms.Textarea(attrs={'rows': 2}),
            'diagnostic_retenu': forms.Textarea(attrs={'rows': 2}),
        }


# ============================================================
# 2. ANTÉCÉDENTS FAMILIAUX
# ============================================================

class AntecedentsFamiliauxForm(forms.ModelForm):
    """Formulaire pour les antécédents familiaux."""
    
    tares_familiales = JSONMultipleChoiceField(
        choices=C.TARES_FAMILIALES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Tares familiales",
    )
    
    class Meta:
        model = AntecedentsFamiliaux
        fields = [
            'rang_fratrie',
            'etat_sante_ascendants',
            'etat_sante_collateraux',
            'tares_familiales',
        ]
        widgets = {
            'etat_sante_ascendants': forms.Textarea(attrs={'rows': 2}),
            'etat_sante_collateraux': forms.Textarea(attrs={'rows': 2}),
        }


# ============================================================
# 3. GROSSESSE
# ============================================================

class GrossesseForm(forms.ModelForm):
    """Formulaire pour les antécédents de grossesse."""
    
    pathologies_grossesse = JSONMultipleChoiceField(
        choices=C.PATHOLOGIES_GROSSESSE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Pathologies de la grossesse",
    )
    
    leucorrhees_traitees = forms.ChoiceField(
        choices=[('', '---')] + C.OUI_NON_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Leucorrhées traitées ?",
    )
    
    class Meta:
        model = Grossesse
        fields = [
            'age_mere',
            'gpa',
            'debut_cpn',
            'rythme_cpn',
            'nombre_cpn',
            'lieu_cpn',
            'nombre_vat',
            'serologies',  # JSONField - sera géré séparément
            'nombre_echographies',
            'resultat_echographie',
            'pathologies_grossesse',
            'leucorrhees_couleur',
            'leucorrhees_odeur',
            'leucorrhees_abondance',
            'leucorrhees_traitees',
            'prise_medicaments',
            'prise_toxiques',
            'conclusion',
        ]
        widgets = {
            'gpa': forms.TextInput(attrs={'placeholder': 'Ex: G2 P1 A0'}),
            'resultat_echographie': forms.Textarea(attrs={'rows': 2}),
            'prise_medicaments': forms.Textarea(attrs={'rows': 2}),
            'prise_toxiques': forms.Textarea(attrs={'rows': 2}),
            'conclusion': forms.Select,
        }


# ============================================================
# 4. ACCOUCHEMENT
# ============================================================

class AccouchementForm(forms.ModelForm):
    """Formulaire pour les détails de l'accouchement."""
    
    cri_immediat = forms.ChoiceField(
        choices=[('', '---')] + C.OUI_NON_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Cri immédiat ?",
    )
    
    asphyxie = forms.ChoiceField(
        choices=[('', '---')] + C.OUI_NON_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Asphyxié ?",
    )
    
    reanimation = forms.ChoiceField(
        choices=[('', '---')] + C.OUI_NON_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Réanimation ?",
    )
    
    class Meta:
        model = Accouchement
        fields = [
            'lieu',
            'ddr',
            'dpa',
            'presentation',
            'duree_travail_minutes',
            'duree_poussee_minutes',
            'terme',
            'voie',
            'manoeuvre_obstetricale',  # JSONField
            'cri_immediat',
            'indice_apgar',
            'asphyxie',
            'reanimation',
            'duree_reanimation_minutes',
            'liquide_amniotique_couleur',
            'liquide_amniotique_abondance',
            'poids_naissance_kg',
            'poids_naissance_type',
            'type_accouchement',
            'adaptation_neonatale',
            'conclusion',
        ]
        widgets = {
            'ddr': forms.DateInput(attrs={'type': 'date'}),
            'dpa': forms.DateInput(attrs={'type': 'date'}),
            'presentation': forms.Select,
            'terme': forms.RadioSelect,
            'voie': forms.RadioSelect,
            'manoeuvre_obstetricale': forms.CheckboxSelectMultiple,
            'liquide_amniotique_couleur': forms.Select,
            'liquide_amniotique_abondance': forms.Select,
            'poids_naissance_type': forms.RadioSelect,
            'type_accouchement': forms.RadioSelect,
            'adaptation_neonatale': forms.RadioSelect,
            'conclusion': forms.Textarea(attrs={'rows': 2}),
        }


# ============================================================
# 5. ALIMENTATION
# ============================================================

class AlimentationForm(forms.ModelForm):
    """Formulaire pour l'alimentation."""
    
    type_alimentation = JSONMultipleChoiceField(
        choices=C.ALIMENTATION_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Type d'alimentation",
    )
    
    class Meta:
        model = Alimentation
        fields = [
            'type_alimentation',
            'ame_jusqua_mois',
            'diversification_mois',
            'diversification_aliments',
            'sevrage',
            'alimentation_actuelle',
            'regime',
        ]
        widgets = {
            'diversification_aliments': forms.Textarea(attrs={'rows': 2}),
            'alimentation_actuelle': forms.Textarea(attrs={'rows': 2}),
            'regime': forms.Select,
        }


# ============================================================
# 6. VACCINATION
# ============================================================

class VaccinationForm(forms.ModelForm):
    """Formulaire pour la vaccination."""
    
    vaccins_recus = JSONMultipleChoiceField(
        choices=C.VACCINS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Vaccins reçus",
    )
    
    vaccination_correcte = forms.ChoiceField(
        choices=[('', '---')] + C.OUI_NON_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Vaccination correcte ?",
    )
    
    class Meta:
        model = Vaccination
        fields = [
            'vaccins_recus',
            'vaccination_correcte',
            'nom_carnet',
            'details_vaccination',
        ]
        widgets = {
            'details_vaccination': forms.Textarea(attrs={'rows': 2}),
        }


# ============================================================
# 7. CONTEXTE ÉPIDÉMIOLOGIQUE
# ============================================================

class ContexteEpidemiologiqueForm(forms.ModelForm):
    """Formulaire pour le contexte épidémiologique."""
    
    dyspnee_contexte = JSONMultipleChoiceField(
        choices=C.CONTEXTE_DYSPNEE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Contexte dyspnée",
    )
    
    diarrhee_contexte = JSONMultipleChoiceField(
        choices=C.CONTEXTE_DIARRHEE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Contexte diarrhée",
    )
    
    convulsion_parents_bas_age = forms.ChoiceField(
        choices=[('', '---')] + C.OUI_NON_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Crise convulsive chez les parents à bas âge ?",
    )
    
    convulsion_hyperthermique = forms.ChoiceField(
        choices=[('', '---')] + C.OUI_NON_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Convulsion hyperthermique ?",
    )
    
    class Meta:
        model = ContexteEpidemiologique
        fields = [
            'dyspnee_contexte',
            'diarrhee_contexte',
            'convulsion_parents_bas_age',
            'convulsion_hyperthermique',
        ]


# ============================================================
# 8. FICHE SOCIALE
# ============================================================

class FicheSocialeForm(forms.ModelForm):
    """Formulaire pour la fiche sociale."""
    
    eclairage = JSONMultipleChoiceField(
        choices=C.ECLAIRAGE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Éclairage",
    )
    
    eau = JSONMultipleChoiceField(
        choices=C.EAU_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Eau",
    )
    
    combustible = JSONMultipleChoiceField(
        choices=C.COMBUSTIBLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Combustible",
    )
    
    class Meta:
        model = FicheSociale
        fields = [
            'profession_pere',
            'profession_mere',
            'type_maison',
            'nombre_chambres',
            'nombre_personnes',
            'eclairage',
            'eau',
            'combustible',
            'wc',
            'niveau_social',
        ]
        widgets = {
            'wc': forms.Select,
            'niveau_social': forms.RadioSelect,
        }


# ============================================================
# 9. ÉPISODES DE L'HISTOIRE DE LA MALADIE
# ============================================================

class EpisodeHistoireMaladieForm(forms.ModelForm):
    """Formulaire pour un épisode de l'histoire de la maladie."""
    
    class Meta:
        model = EpisodeHistoireMaladie
        fields = [
            'ordre',
            'date_debut',
            'signes',
            'contexte',
            'signes_associes',
            'traitement_recu',
            'evolution',
        ]
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'signes': forms.Textarea(attrs={'rows': 2}),
            'contexte': forms.Textarea(attrs={'rows': 2}),
            'signes_associes': forms.Textarea(attrs={'rows': 2}),
            'traitement_recu': forms.Textarea(attrs={'rows': 2}),
            'evolution': forms.Select,
        }


# ============================================================
# 10. DÉVELOPPEMENT PSYCHOMOTEUR (ENFANT)
# ============================================================

class DeveloppementPsychomoteurForm(forms.ModelForm):
    """Formulaire pour le développement psychomoteur (enfant seulement)."""
    
    class Meta:
        model = DeveloppementPsychomoteur
        fields = [
            'langage',
            'motricite',
            'prehension',
            'relationnelle',
            'conclusion',
        ]
        widgets = {
            'langage': forms.Textarea(attrs={'rows': 2}),
            'motricite': forms.Textarea(attrs={'rows': 2}),
            'prehension': forms.Textarea(attrs={'rows': 2}),
            'relationnelle': forms.Textarea(attrs={'rows': 2}),
            'conclusion': forms.RadioSelect,
        }


# ============================================================
# 11. ANTÉCÉDENTS PERSONNELS (ENFANT)
# ============================================================

class AntecedentsPersonnelsForm(forms.ModelForm):
    """Formulaire pour les antécédents médicaux et chirurgicaux (enfant)."""
    
    class Meta:
        model = AntecedentsPersonnels
        fields = [
            'hospitalisation_anterieure',
            'atcd_medicaux',
            'atcd_chirurgicaux',
        ]
        widgets = {
            'hospitalisation_anterieure': forms.Textarea(attrs={'rows': 2}),
            'atcd_medicaux': forms.Textarea(attrs={'rows': 2}),
            'atcd_chirurgicaux': forms.Textarea(attrs={'rows': 2}),
        }


# ============================================================
# 12. EXAMEN CLINIQUE (LE PLUS COMPLEXE)
# ============================================================

class ExamenCliniqueForm(forms.ModelForm):
    """
    Formulaire pour l'examen clinique complet.
    Les JSONField pour les examens par appareil sont gérés via des sous-sections.
    """
    
    signes_3a2s = JSONMultipleChoiceField(
        choices=C.SIGNES_3A2S_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Signes 3A2S",
    )
    
    class Meta:
        model = ExamenClinique
        fields = [
            'date_examen',
            # Biométrie
            'pc_cm',
            'pt_cm',
            'pbd_cm',
            'pbg_cm',
            'pb_cm',
            'poids_kg',
            'taille_cm',
            'p_t',
            't_a',
            'p_a',
            'nombre_dents',
            'conclusion_biometrie',
            # Signes généraux
            'signes_3a2s',
            'signes_generaux_precision',
            'signes_fonctionnels',
            # Examens par appareil (JSONField)
            'pleuropulmonaire',
            'cardiovasculaire',
            'digestif',
            'neurologique',
            'orl',
            'cutaneomuqueux',
            'genitaux',
            'osteoarticulaire',
        ]
        widgets = {
            'date_examen': forms.DateInput(attrs={'type': 'date'}),
            'signes_generaux_precision': forms.Textarea(attrs={'rows': 2}),
            'signes_fonctionnels': forms.Textarea(attrs={'rows': 2}),
            'conclusion_biometrie': forms.RadioSelect,
            # Les JSONField seront rendus via des templates custom ou widgets
        }
    
    def clean(self):
        cleaned_data = super().clean()
        # Validation custom pour les JSONField si nécessaire
        return cleaned_data


class ExamenCliniqueBaseForm(forms.ModelForm):
    """
    Formulaire de base de l'examen clinique :
    - biométrie
    - signes généraux
    - signes fonctionnels

    Les examens par appareil sont gérés par les sous-formulaires
    définis dans patient/exam_forms.py.
    """

    signes_3a2s = JSONMultipleChoiceField(
        choices=C.SIGNES_3A2S_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Signes 3A2S",
    )

    class Meta:
        model = ExamenClinique
        fields = [
            "date_examen",
            "pc_cm",
            "pt_cm",
            "pbd_cm",
            "pbg_cm",
            "pb_cm",
            "poids_kg",
            "taille_cm",
            "p_t",
            "t_a",
            "p_a",
            "nombre_dents",
            "conclusion_biometrie",
            "signes_3a2s",
            "signes_generaux_precision",
            "signes_fonctionnels",
        ]
        widgets = {
            "date_examen": forms.DateInput(attrs={"type": "date"}),
            "conclusion_biometrie": forms.RadioSelect,
            "signes_generaux_precision": forms.Textarea(attrs={"rows": 2}),
            "signes_fonctionnels": forms.Textarea(attrs={"rows": 2}),
        }


# ============================================================
# 13. HYPOTHÈSES DIAGNOSTIQUES
# ============================================================

class HypotheseDiagnosticForm(forms.ModelForm):
    """Formulaire pour une hypothèse diagnostique."""
    
    class Meta:
        model = HypotheseDiagnostic
        fields = [
            'ordre',
            'diagnostic_propose',
            'arguments_pour',
            'arguments_contre',
            'paraclinique',
        ]
        widgets = {
            'diagnostic_propose': forms.Textarea(attrs={'rows': 2}),
            'arguments_pour': forms.Textarea(attrs={'rows': 2}),
            'arguments_contre': forms.Textarea(attrs={'rows': 2}),
            'paraclinique': forms.Textarea(attrs={'rows': 2}),
        }


# ============================================================
# 14. TRAITEMENT
# ============================================================

class TraitementForm(forms.ModelForm):
    """Formulaire pour le traitement."""
    
    class Meta:
        model = Traitement
        fields = [
            'but',
            'symptomatique',
            'etiologique',
            'surveillance',
            'notes',
        ]
        widgets = {
            'but': forms.Textarea(attrs={'rows': 2}),
            'symptomatique': forms.Textarea(attrs={'rows': 3}),
            'etiologique': forms.Textarea(attrs={'rows': 3}),
            'surveillance': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


# ============================================================
# 15. ÉVOLUTION (OPTIONNEL)
# ============================================================

class EvolutionForm(forms.ModelForm):
    """Formulaire pour l'évolution (suivi ultérieur)."""
    
    class Meta:
        model = Evolution
        fields = [
            'date',
            'description',
            'statut',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'statut': forms.RadioSelect,
        }


# ============================================================
# FORMSETS POUR RELATIONS ONE-TO-MANY
# ============================================================

# Formset pour les épisodes de l'histoire de la maladie
EpisodeHistoireMaladieFormSet = inlineformset_factory(
    ObservationMedicale,
    EpisodeHistoireMaladie,
    form=EpisodeHistoireMaladieForm,
    extra=3,  # 3 épisodes par défaut
    can_delete=True,
)

# Formset pour les hypothèses diagnostiques
HypotheseDiagnosticFormSet = inlineformset_factory(
    ObservationMedicale,
    HypotheseDiagnostic,
    form=HypotheseDiagnosticForm,
    extra=3,  # 3 hypothèses par défaut
    can_delete=True,
)

# Formset pour les évolutions (optionnel)
EvolutionFormSet = inlineformset_factory(
    ObservationMedicale,
    Evolution,
    form=EvolutionForm,
    extra=1,
    can_delete=True,
)


# ============================================================
# HELPER POUR GÉRER LES JSONFIELD DES EXAMENS PAR APPAREIL
# ============================================================

def get_examen_appareil_form_fields(appareil_name):
    """
    Retourne les champs structurés pour un appareil donné.
    Utilisé pour générer dynamiquement les sous-formulaires des examens.
    
    Args:
        appareil_name: Nom de l'appareil (pleuropulmonaire, cardiovasculaire, etc.)
    
    Returns:
        dict: Structure des champs par catégorie (inspection, palpation, etc.)
    """
    
    structures = {
        'pleuropulmonaire': {
            'inspection': [
                ('frequence_respiratoire', 'Fréquence respiratoire (cpm)', forms.IntegerField),
                ('type_respiration', 'Type de respiration', forms.ChoiceField, C.TYPE_RESPIRATION_CHOICES),
                ('amplitude_thoracique', 'Amplitude thoracique', forms.ChoiceField, C.AMPLITUDE_THORACIQUE_CHOICES),
                ('symetrie_thoracique', 'Symétrie thoracique', forms.ChoiceField, C.SYMETRIE_THORACIQUE_CHOICES),
                ('signes_de_lutte', 'Signes de lutte', forms.MultipleChoiceField, C.SIGNES_LUTTE_CHOICES),
                ('deformation_thoracique', 'Déformation thoracique', forms.ChoiceField, C.DEFORMATION_THORACIQUE_CHOICES),
            ],
            'palpation': [
                ('vibrations_vocales', 'Vibrations vocales', forms.ChoiceField, C.VIBRATIONS_VOCALES_CHOICES),
                ('expansion_thoracique', 'Expansion thoracique', forms.ChoiceField, C.EXPANSION_THORACIQUE_CHOICES),
            ],
            'percussion': [
                ('sonorite_globale', 'Sonorité globale', forms.ChoiceField, C.SONORITE_PULMONAIRE_CHOICES),
                ('localisation_anormale', 'Localisation anormale', forms.ChoiceField, C.LOCALISATION_PULMONAIRE_CHOICES),
            ],
            'auscultation': [
                ('murmure_vesiculaire', 'Murmure vésiculaire', forms.ChoiceField, C.MURMURE_VESICULAIRE_CHOICES),
                ('rales_crepitants', 'Râles crépitants', forms.ChoiceField, C.RALES_CREPITANTS_CHOICES),
                ('rales_sous_crepitants', 'Râles sous-crépitants', forms.ChoiceField, C.RALES_SOUS_CREPITANTS_CHOICES),
                ('souffle_tubaire', 'Souffle tubaire', forms.ChoiceField, C.SOUFFLE_TUBAIRE_CHOICES),
            ],
            'exceptions': 'Exceptions / Imprévus',
            'conclusion': 'Conclusion',
        },
        # Ajouter les autres appareils ici...
    }
    
    return structures.get(appareil_name, {})


# ============================================================
# VALIDATION ET CLEANING METHODS
# ============================================================

def clean_json_list_field(value):
    """
    Nettoie et valide un champ de liste JSON.
    
    Args:
        value: Valeur du champ (peut être None, [], ou liste de strings)
    
    Returns:
        list: Liste nettoyée
    """
    if not value:
        return []
    if isinstance(value, str):
        return [value] if value else []
    return list(value)


def validate_observation_complete(observation):
    """
    Valide qu'une observation est complète selon le type (NN ou Enfant).
    
    Args:
        observation: Instance d'ObservationMedicale
    
    Returns:
        dict: Dictionnaire des erreurs par section
    """
    errors = {}
    
    # Validation de base
    if not observation.nom or not observation.prenoms:
        errors['etat_civil'] = "Nom et prénoms sont requis"
    
    # Validation spécifique selon le type
    if observation.type_observation == 'ENFANT':
        if not hasattr(observation, 'developpement_psychomoteur'):
            errors['dpm'] = "Développement psychomoteur requis pour un enfant"
    
    return errors


# ============================================================
# SUIVI HOSPITALISATION - EXAMEN PHYSIQUE
# ============================================================

class ExamenPhysiqueForm(forms.ModelForm):
    """
    Formulaire pour enregistrer un examen physique répété
    pendant l'hospitalisation.
    """

    date_heure = forms.DateTimeField(
        input_formats=[
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M",
        ],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        required=True,
        label="Date et heure de l'examen",
    )

    signes_generaux = JSONMultipleChoiceField(
        choices=C.SIGNES_GENERAUX_SUIVI_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Signes généraux",
    )

    signes_fonctionnels = JSONMultipleChoiceField(
        choices=C.SIGNES_FONCTIONNELS_SUIVI_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Signes fonctionnels",
    )

    class Meta:
        model = ExamenPhysique
        fields = [
            "date_heure",
            "examine_par",
            "poids_kg",
            "temperature_c",
            "frequence_respiratoire",
            "frequence_cardiaque",
            "tension_arterielle",
            "saturation_oxygene",
            "signes_generaux",
            "signes_fonctionnels",
            "exceptions",
            "conclusion",
        ]
        widgets = {
            "tension_arterielle": forms.TextInput(attrs={"placeholder": "100/60"}),
            "exceptions": forms.Textarea(attrs={"rows": 2}),
            "conclusion": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            if not self.fields["date_heure"].initial:
                self.fields["date_heure"].initial = timezone.now

    def clean_saturation_oxygene(self):
        value = self.cleaned_data.get("saturation_oxygene")

        if value is None:
            return value

        if value < 0 or value > 100:
            raise ValidationError("La SpO₂ doit être comprise entre 0 et 100 %.")

        return value

    def clean_temperature_c(self):
        value = self.cleaned_data.get("temperature_c")

        if value is None:
            return value

        if value < 25 or value > 45:
            raise ValidationError("La température semble invalide.")

        return value



# ============================================================
# FICHE DE RÉHYDRATATION
# ============================================================

class FicheRehydratationForm(forms.ModelForm):
    """
    Formulaire principal de la fiche de réhydratation.
    """

    heure_debut = forms.DateTimeField(
        input_formats=[
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M",
        ],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        required=True,
        label="Heure de début",
    )

    heure_fin = forms.DateTimeField(
        input_formats=[
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M",
        ],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        required=False,
        label="Heure de fin",
    )

    class Meta:
        model = FicheRehydratation
        fields = [
            "statut",
            "heure_debut",
            "heure_fin",
            "poids_initial_kg",
            "poids_final_kg",
            "quantite_liquide_ml",
            "duree_minutes",
            "notes",
        ]
        widgets = {
            "statut": forms.RadioSelect,
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            if not self.fields["heure_debut"].initial:
                self.fields["heure_debut"].initial = timezone.now


# ============================================================
# ÉVALUATION HORAIRE - RÉHYDRATATION
# ============================================================

class EvaluationHoraireRehydratationForm(forms.ModelForm):
    """
    Formulaire pour une évaluation horaire de réhydratation.
    """

    heure_evaluation = forms.DateTimeField(
        input_formats=[
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M",
        ],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        required=True,
        label="Heure d'évaluation",
    )

    signes_generaux = JSONMultipleChoiceField(
        choices=C.SIGNES_GENERAUX_SUIVI_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Signes généraux",
    )

    signes_fonctionnels = JSONMultipleChoiceField(
        choices=C.SIGNES_FONCTIONNELS_SUIVI_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Signes fonctionnels",
    )

    etat_yeux = forms.ChoiceField(
        choices=[("", "---")] + C.ETAT_YEUX_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="État des yeux",
    )

    etat_muqueuses = forms.ChoiceField(
        choices=[("", "---")] + C.ETAT_MUQUEUSES_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="État des muqueuses",
    )

    pli_cutane = forms.ChoiceField(
        choices=[("", "---")] + C.PLI_CUTANE_REHYDRATATION_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Pli cutané",
    )

    urine = forms.ChoiceField(
        choices=[("", "---")] + C.URINE_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Urine",
    )

    selles = forms.ChoiceField(
        choices=[("", "---")] + C.SELLES_REHYDRATATION_CHOICES,
        widget=forms.Select,
        required=False,
        label="Selles",
    )

    vomissements = forms.ChoiceField(
        choices=[("", "---")] + C.VOMISSEMENTS_REHYDRATATION_CHOICES,
        widget=forms.Select,
        required=False,
        label="Vomissements",
    )

    class Meta:
        model = EvaluationHoraireRehydratation
        fields = [
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
        ]
        widgets = {
            "remarque": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            if not self.fields["heure_evaluation"].initial:
                self.fields["heure_evaluation"].initial = timezone.now

    def clean_temperature_c(self):
        value = self.cleaned_data.get("temperature_c")

        if value is None:
            return value

        if value < 25 or value > 45:
            raise ValidationError("La température semble invalide.")

        return value

    def clean_frequence_respiratoire(self):
        value = self.cleaned_data.get("frequence_respiratoire")

        if value is None:
            return value

        if value > 300:
            raise ValidationError("La fréquence respiratoire semble invalide.")

        return value

    def clean_frequence_cardiaque(self):
        value = self.cleaned_data.get("frequence_cardiaque")

        if value is None:
            return value

        if value > 300:
            raise ValidationError("La fréquence cardiaque semble invalide.")

        return value


# ============================================================
# FORMSET - ÉVALUATIONS HORAIRES
# ============================================================

EvaluationHoraireRehydratationFormSet = inlineformset_factory(
    FicheRehydratation,
    EvaluationHoraireRehydratation,
    form=EvaluationHoraireRehydratationForm,
    extra=2,
    can_delete=True,
)


# ============================================================
# TRAITEMENTS AJUSTÉS ET TRACÉS
# ============================================================

class TraitementAjustementForm(forms.ModelForm):
    """
    Formulaire principal pour créer/modifier un ajustement de traitement.
    """

    date_heure = forms.DateTimeField(
        input_formats=[
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M",
        ],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        required=True,
        label="Date et heure",
    )

    class Meta:
        model = TraitementAjustement
        fields = [
            "date_heure",
            "type_ajustement",
            "motif",
            "notes",
        ]
        widgets = {
            "type_ajustement": forms.RadioSelect,
            "motif": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            if not self.fields["date_heure"].initial:
                self.fields["date_heure"].initial = timezone.now


class LigneTraitementForm(forms.ModelForm):
    """
    Formulaire pour une ligne de traitement.
    """

    type_ligne = forms.ChoiceField(
        choices=C.TYPE_LIGNE_TRAITEMENT_CHOICES,
        widget=forms.Select,
        required=False,
        label="Type",
    )

    voie = forms.ChoiceField(
        choices=[("", "---")] + C.VOIE_TRAITEMENT_CHOICES,
        widget=forms.Select,
        required=False,
        label="Voie",
    )

    frequence = forms.ChoiceField(
        choices=[("", "---")] + C.FREQUENCE_TRAITEMENT_CHOICES,
        widget=forms.Select,
        required=False,
        label="Fréquence",
    )

    date_debut = forms.DateTimeField(
        input_formats=[
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M",
        ],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        required=False,
        label="Date de début",
    )

    date_fin = forms.DateTimeField(
        input_formats=[
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M",
        ],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        required=False,
        label="Date de fin",
    )

    class Meta:
        model = LigneTraitement
        fields = [
            "type_ligne",
            "nom",
            "dose",
            "voie",
            "frequence",
            "duree",
            "date_debut",
            "date_fin",
            "instructions",
        ]
        widgets = {
            "instructions": forms.Textarea(attrs={"rows": 2}),
        }

    def clean_type_ligne(self):
        value = self.cleaned_data.get("type_ligne")

        if not value:
            return "medicament"

        return value


LigneTraitementFormSet = inlineformset_factory(
    TraitementAjustement,
    LigneTraitement,
    form=LigneTraitementForm,
    extra=2,
    can_delete=True,
)


