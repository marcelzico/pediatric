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
    ExamenParaclinique,

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
            # 'serologies',  # JSONField - sera géré séparément
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
    
    # ✅ Tous les ChoiceField sont redéfinis explicitement avec required=False
    presentation = forms.ChoiceField(
        choices=[('', '--- Choisir ---')] + C.PRESENTATION_CHOICES,
        widget=forms.Select,
        required=False,
        label="Présentation",
    )
    
    terme = forms.ChoiceField(
        choices=[('', '--- Choisir ---')] + C.TERME_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Terme",
    )
    
    voie = forms.ChoiceField(
        choices=[('', '--- Choisir ---')] + C.VOIE_ACCOUCHEMENT_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Voie d'accouchement",
    )
    
    manoeuvre_obstetricale = JSONMultipleChoiceField(
        choices=C.MANOEUVRE_OBSTETRICALE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Manœuvre obstétricale",
    )
    
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
    
    liquide_amniotique_couleur = forms.ChoiceField(
        choices=[('', '--- Choisir ---')] + C.COULEUR_LIQUIDE_AMNIOTIQUE_CHOICES,
        widget=forms.Select,
        required=False,
        label="Couleur du liquide amniotique",
    )
    
    liquide_amniotique_abondance = forms.ChoiceField(
        choices=[('', '--- Choisir ---')] + C.ABONDANCE_LIQUIDE_AMNIOTIQUE_CHOICES,
        widget=forms.Select,
        required=False,
        label="Abondance du liquide amniotique",
    )
    
    poids_naissance_type = forms.ChoiceField(
        choices=[('', '--- Choisir ---')] + C.POIDS_NAISSANCE_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Type de poids de naissance",
    )
    
    type_accouchement = forms.ChoiceField(
        choices=[('', '--- Choisir ---')] + C.TYPE_ACCOUCHEMENT_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Type d'accouchement",
    )
    
    adaptation_neonatale = forms.ChoiceField(
        choices=[('', '--- Choisir ---')] + C.ADAPTATION_NEONATALE_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Adaptation néonatale",
    )
    
    # Champs numériques avec required=False
    duree_travail_minutes = forms.IntegerField(
        required=False,
        label="Durée du travail (minutes)",
        widget=forms.NumberInput(attrs={'min': 0}),
    )
    
    duree_poussee_minutes = forms.IntegerField(
        required=False,
        label="Durée de poussée (minutes)",
        widget=forms.NumberInput(attrs={'min': 0}),
    )
    
    indice_apgar = forms.IntegerField(
        required=False,
        label="Indice d'Apgar",
        widget=forms.NumberInput(attrs={'min': 0, 'max': 10}),
    )
    
    duree_reanimation_minutes = forms.IntegerField(
        required=False,
        label="Durée de réanimation (minutes)",
        widget=forms.NumberInput(attrs={'min': 0}),
    )
    
    poids_naissance_kg = forms.DecimalField(
        required=False,
        label="Poids de naissance (kg)",
        widget=forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        decimal_places=3,
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
            'manoeuvre_obstetricale',
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
            'lieu': forms.TextInput(attrs={'placeholder': 'Lieu de l\'accouchement'}),
            'ddr': forms.DateInput(attrs={'type': 'date'}),
            'dpa': forms.DateInput(attrs={'type': 'date'}),
            'conclusion': forms.Textarea(attrs={'rows': 2}),
        }
    
    def clean(self):
        """
        Nettoie les données et convertit les valeurs vides en None
        pour les champs booléens et numériques.
        """
        cleaned_data = super().clean()
        
        # Liste des champs qui doivent être None si vides
        nullable_fields = [
            'presentation', 'terme', 'voie', 'cri_immediat', 'asphyxie', 
            'reanimation', 'liquide_amniotique_couleur', 'liquide_amniotique_abondance',
            'poids_naissance_type', 'type_accouchement', 'adaptation_neonatale',
            'duree_travail_minutes', 'duree_poussee_minutes', 'indice_apgar',
            'duree_reanimation_minutes', 'poids_naissance_kg'
        ]
        
        for field_name in nullable_fields:
            value = cleaned_data.get(field_name)
            # Convertir les chaînes vides en None
            if value == '' or value == '---' or value == '--- Choisir ---':
                cleaned_data[field_name] = None
        
        return cleaned_data


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
            'langage': forms.Textarea(attrs={'rows': 7}),
            'motricite': forms.Textarea(attrs={'rows': 7}),
            'prehension': forms.Textarea(attrs={'rows': 7}),
            'relationnelle': forms.Textarea(attrs={'rows': 7}),
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
            'pbd_mm',
            'pbg_mm',
            'pb_mm',
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
            # 'pleuropulmonaire',
            # 'cardiovasculaire',
            # 'digestif',
            # 'neurologique',
            # 'orl',
            # 'cutaneomuqueux',
            # 'genitaux',
            # 'osteoarticulaire',
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
            "pbd_mm",
            "pbg_mm",
            "pb_mm",
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
        required=False,
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
            "duree_heure",
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


# ============================================================
# SÉROLOGIES DE GROSSESSE (SOUS-FORMULAIRE)
# ============================================================

class SerologiesForm(forms.Form):
    """
    Sous-formulaire pour gérer les sérologies de grossesse.
    Déplie le JSONField 'serologies' en champs Django classiques.
    """
    
    SEROLOGIE_KEYS = [
        ("bw", "BW (Syphilis)"),
        ("vih", "VIH"),
        ("toxoplasmose", "Toxoplasmose"),
        ("rubeole", "Rubéole"),
        ("hb", "Hépatite B"),
    ]
    
    def __init__(self, *args, json_data=None, **kwargs):
        self.json_data = json_data if isinstance(json_data, dict) else {}
        super().__init__(*args, **kwargs)
        
        for key, label in self.SEROLOGIE_KEYS:
            data = self.json_data.get(key, {}) if isinstance(self.json_data.get(key), dict) else {}
            
            # Champ "Fait" (checkbox)
            self.fields[f"{key}_fait"] = forms.BooleanField(
                required=False,
                label=f"{label} - Fait",
                initial=data.get("fait", False),
            )
            
            # Champ "Résultat" (radio +/-)
            self.fields[f"{key}_resultat"] = forms.ChoiceField(
                choices=[("", "—"), ("positif", "Positif (+)"), ("negatif", "Négatif (-)")],
                required=False,
                label=f"{label} - Résultat",
                initial=data.get("resultat", ""),
                widget=forms.RadioSelect,
            )
    
    def get_json(self):
        """Replie les données en structure JSON."""
        if not self.is_valid():
            return self.json_data
        
        result = {}
        for key, _ in self.SEROLOGIE_KEYS:
            fait = self.cleaned_data.get(f"{key}_fait", False)
            resultat = self.cleaned_data.get(f"{key}_resultat", "")
            
            # On ne stocke que si au moins une info est présente
            if fait or resultat:
                result[key] = {
                    "fait": bool(fait),
                    "resultat": resultat if resultat else None,
                }
            else:
                result[key] = {"fait": None, "resultat": None}
        
        return result
    
    def grouped_fields(self):
        """Regroupe les champs par sérologie pour l'affichage."""
        groups = []
        for key, label in self.SEROLOGIE_KEYS:
            groups.append({
                "key": key,
                "label": label,
                "fait": self[f"{key}_fait"],
                "resultat": self[f"{key}_resultat"],
            })
        return groups


class BaseExamenAppareilForm(forms.Form):
    """
    Classe de base pour les sous-formulaires d'examen par appareil.
    Gère le dépliage/repliage du JSON.
    """
    
    appareil_key = None  # À définir dans les sous-classes
    
    def __init__(self, *args, json_data=None, **kwargs):
        self.json_data = json_data if isinstance(json_data, dict) else {}
        super().__init__(*args, **kwargs)
    
    def get_json(self):
        """
        Replie les données du formulaire en structure JSON.
        À surcharger dans les sous-classes.
        """
        if not self.is_valid():
            return self.json_data
        
        result = {}
        for field_name in self.fields.keys():
            value = self.cleaned_data.get(field_name)
            
            # Gestion des champs imbriqués (ex: inspection__frequence_respiratoire)
            if "__" in field_name:
                parts = field_name.split("__")
                current = result
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                result[field_name] = value
        
        return result


# ============================================================
# LABELS DES CATÉGORIES D'EXAMEN
# ============================================================

CATEGORY_LABELS = {
    "inspection": "▸ Inspection",
    "palpation": "▸ Palpation",
    "percussion": "▸ Percussion",
    "auscultation": "▸ Auscultation",
    "emission": "▸ Émission",
    "reflexes": "▸ Réflexes",
    "fille": "👧 Chez la fille",
    "garcon": "👦 Chez le garçon",
    "general": "Général",
}


# ============================================================
# CLASSE DE BASE POUR LES EXAMENS PAR APPAREIL
# ============================================================

# ============================================================
# CLASSE DE BASE POUR LES EXAMENS PAR APPAREIL
# ============================================================

class BaseExamenAppareilForm(forms.Form):
    """
    Classe de base pour les sous-formulaires d'examen par appareil.
    Gère :
    - le dépliage/repliage du JSON
    - le pré-remplissage depuis le JSON existant
    - le groupement des champs par catégorie pour le template
    """

    appareil_key = None

    CATEGORY_LABELS = {
        "inspection": "▸ Inspection",
        "palpation": "▸ Palpation",
        "percussion": "▸ Percussion",
        "auscultation": "▸ Auscultation",
        "emission": "▸ Émission",
        "reflexes": "▸ Réflexes",
        "fille": "👧 Chez la fille",
        "garcon": "👦 Chez le garçon",
        "general": "Général",
    }

    def __init__(self, *args, json_data=None, **kwargs):
        self.json_data = json_data if isinstance(json_data, dict) else {}
        super().__init__(*args, **kwargs)
        self._load_initial_data()

    def _get_nested_value(self, data, field_name):
        """
        Récupère une valeur imbriquée dans le JSON.
        Exemple : inspection__frequence_respiratoire
        """
        if "__" in field_name:
            current = data
            for part in field_name.split("__"):
                if not isinstance(current, dict):
                    return None
                current = current.get(part)
            return current

        return data.get(field_name)

    def _load_initial_data(self):
        """
        Pré-remplit les champs du formulaire avec les données JSON existantes.
        """
        for field_name, field in self.fields.items():
            value = self._get_nested_value(self.json_data, field_name)

            if value is not None:
                field.initial = value

    def get_json(self):
        """
        Replie les données du formulaire en structure JSON.
        """
        if not self.is_valid():
            return self.json_data

        result = {}

        for field_name in self.fields.keys():
            value = self.cleaned_data.get(field_name)

            if "__" in field_name:
                parts = field_name.split("__")
                current = result

                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                current[parts[-1]] = value
            else:
                result[field_name] = value

        return result

    def get_categories(self):
        """
        Retourne les champs visibles groupés par catégorie.

        Format retourné :
        [
            ("▸ Inspection", [bound_field1, bound_field2, ...]),
            ("▸ Palpation", [bound_field3, ...]),
            ...
        ]
        """
        categories = {}
        order = []

        for bound_field in self.visible_fields():
            field_name = bound_field.name

            if "__" in field_name:
                category_key = field_name.split("__")[0]
            else:
                category_key = "general"

            if category_key not in categories:
                categories[category_key] = []
                order.append(category_key)

            categories[category_key].append(bound_field)

        return [
            (
                self.CATEGORY_LABELS.get(category_key, category_key.title()),
                categories[category_key],
            )
            for category_key in order
        ]

# ============================================================
# APPAREIL PLEUROPULMONAIRE
# ============================================================

class PleuropulmonaireForm(BaseExamenAppareilForm):
    """Sous-formulaire pour l'appareil pleuropulmonaire."""
    
    appareil_key = "pleuropulmonaire"
    
    # Inspection
    inspection__frequence_respiratoire = forms.IntegerField(
        required=False,
        label="Fréquence respiratoire (cpm)",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0}),
    )
    
    inspection__type_respiration = forms.ChoiceField(
        choices=[("", "---")] + C.TYPE_RESPIRATION_CHOICES,
        required=False,
        label="Type de respiration",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__amplitude_thoracique = forms.ChoiceField(
        choices=[("", "---")] + C.AMPLITUDE_THORACIQUE_CHOICES,
        required=False,
        label="Amplitude thoracique",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__symetrie_thoracique = forms.ChoiceField(
        choices=[("", "---")] + C.SYMETRIE_THORACIQUE_CHOICES,
        required=False,
        label="Symétrie thoracique",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__signes_de_lutte = forms.MultipleChoiceField(
        choices=C.SIGNES_LUTTE_CHOICES,
        required=False,
        label="Signes de lutte",
        widget=forms.CheckboxSelectMultiple,
    )
    
    inspection__turgescence_jugulaire = forms.ChoiceField(
        choices=[("", "---")] + C.ABSENTE_PRESENTE_CHOICES,
        required=False,
        label="Turgescence jugulaire",
        widget=forms.RadioSelect,
    )
    
    inspection__deformation_thoracique = forms.ChoiceField(
        choices=[("", "---")] + C.DEFORMATION_THORACIQUE_CHOICES,
        required=False,
        label="Déformation thoracique",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Palpation
    palpation__vibrations_vocales = forms.ChoiceField(
        choices=[("", "---")] + C.VIBRATIONS_VOCALES_CHOICES,
        required=False,
        label="Vibrations vocales",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__expansion_thoracique = forms.ChoiceField(
        choices=[("", "---")] + C.EXPANSION_THORACIQUE_CHOICES,
        required=False,
        label="Expansion thoracique",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__douleur_palpation = forms.ChoiceField(
        choices=[("", "---")] + C.ABSENTE_PRESENTE_CHOICES,
        required=False,
        label="Douleur à la palpation",
        widget=forms.RadioSelect,
    )
    
    palpation__crepitations_sous_cutanees = forms.ChoiceField(
        choices=[("", "---")] + C.ABSENTE_PRESENTE_CHOICES,
        required=False,
        label="Crépitations sous-cutanées",
        widget=forms.RadioSelect,
    )
    
    # Percussion
    percussion__sonorite_globale = forms.ChoiceField(
        choices=[("", "---")] + C.SONORITE_PULMONAIRE_CHOICES,
        required=False,
        label="Sonorité globale",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    percussion__localisation_anormale = forms.ChoiceField(
        choices=[("", "---")] + C.LOCALISATION_PULMONAIRE_CHOICES,
        required=False,
        label="Localisation anormale",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    percussion__mobilite_bord_inferieur_poumon = forms.ChoiceField(
        choices=[("", "---")] + C.MOBILITE_BORD_INFERIEUR_POUMON_CHOICES,
        required=False,
        label="Mobilité bord inférieur poumon",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Auscultation
    auscultation__murmure_vesiculaire = forms.ChoiceField(
        choices=[("", "---")] + C.MURMURE_VESICULAIRE_CHOICES,
        required=False,
        label="Murmure vésiculaire",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__rales_crepitants = forms.ChoiceField(
        choices=[("", "---")] + C.RALES_CREPITANTS_CHOICES,
        required=False,
        label="Râles crépitants",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__rales_sous_crepitants = forms.ChoiceField(
        choices=[("", "---")] + C.RALES_SOUS_CREPITANTS_CHOICES,
        required=False,
        label="Râles sous-crépitants",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__sibilances = forms.MultipleChoiceField(
        choices=C.SIBILANCES_CHOICES,
        required=False,
        label="Sibilances / Wheezing",
        widget=forms.CheckboxSelectMultiple,
    )
    
    auscultation__rales_ronflants = forms.ChoiceField(
        choices=[("", "---")] + C.RALES_RONFLANTS_CHOICES,
        required=False,
        label="Râles ronflants",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__souffle_tubaire = forms.ChoiceField(
        choices=[("", "---")] + C.SOUFFLE_TUBAIRE_CHOICES,
        required=False,
        label="Souffle tubaire",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__frottement_pleural = forms.ChoiceField(
        choices=[("", "---")] + C.FROTTEMENT_PLEURAL_CHOICES,
        required=False,
        label="Frottement pleural",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__localisation_anomalies = forms.MultipleChoiceField(
        choices=C.LOCALISATION_PULMONAIRE_CHOICES,
        required=False,
        label="Localisation anomalies",
        widget=forms.CheckboxSelectMultiple,
    )
    
    # Textes libres
    exceptions = forms.CharField(
        required=False,
        label="Autres précisions",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    conclusion = forms.CharField(
        required=False,
        label="Conclusion pleuropulmonaire",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


# ============================================================
# APPAREIL CARDIOVASCULAIRE
# ============================================================

class CardiovasculaireForm(BaseExamenAppareilForm):
    """Sous-formulaire pour l'appareil cardiovasculaire."""
    
    appareil_key = "cardiovasculaire"
    
    # Inspection
    inspection__cyanose = forms.ChoiceField(
        choices=[("", "---")] + C.CYANOSE_CHOICES,
        required=False,
        label="Cyanose",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__paleur = forms.ChoiceField(
        choices=[("", "---")] + C.PALEUR_CHOICES,
        required=False,
        label="Pâleur",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__ictere = forms.ChoiceField(
        choices=[("", "---")] + C.ABSENT_PRESENT_CHOICES,
        required=False,
        label="Ictère",
        widget=forms.RadioSelect,
    )
    
    inspection__oedemes = forms.ChoiceField(
        choices=[("", "---")] + C.OEDEMES_CHOICES,
        required=False,
        label="Œdèmes",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__turgescence_jugulaire = forms.ChoiceField(
        choices=[("", "---")] + C.ABSENTE_PRESENTE_CHOICES,
        required=False,
        label="Turgescence jugulaire",
        widget=forms.RadioSelect,
    )
    
    inspection__hippocratisme_digital = forms.ChoiceField(
        choices=[("", "---")] + C.HIPPOCRATISME_DIGITAL_CHOICES,
        required=False,
        label="Hippocratisme digital",
        widget=forms.RadioSelect,
    )
    
    # Palpation
    palpation__frequence_cardiaque = forms.IntegerField(
        required=False,
        label="Fréquence cardiaque (bpm)",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0}),
    )
    
    palpation__choc_de_pointe = forms.ChoiceField(
        choices=[("", "---")] + C.CHOC_DE_POINTE_CHOICES,
        required=False,
        label="Choc de pointe",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__rythme = forms.ChoiceField(
        choices=[("", "---")] + C.RYTHME_CARDIAQUE_CHOICES,
        required=False,
        label="Rythme",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__thrill = forms.ChoiceField(
        choices=[("", "---")] + C.ABSENT_PRESENT_CHOICES,
        required=False,
        label="Thrill (frémissement)",
        widget=forms.RadioSelect,
    )
    
    palpation__chaleur_extremites = forms.ChoiceField(
        choices=[("", "---")] + C.CHALEUR_EXTREMITES_CHOICES,
        required=False,
        label="Chaleur des extrémités",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__trc_secondes = forms.IntegerField(
        required=False,
        label="TRC (secondes)",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0}),
    )
    
    palpation__pouls_peripheriques = forms.ChoiceField(
        choices=[("", "---")] + C.POULS_PERIPHERIQUES_CHOICES,
        required=False,
        label="Pouls périphériques",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__pouls_femoraux = forms.ChoiceField(
        choices=[("", "---")] + C.POULS_FEMORAUX_CHOICES,
        required=False,
        label="Pouls fémoraux",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Percussion
    percussion__matite_cardiaque = forms.ChoiceField(
        choices=[("", "---")] + C.MATITE_CARDIAQUE_CHOICES,
        required=False,
        label="Matité cardiaque",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Auscultation
    auscultation__bdc = forms.ChoiceField(
        choices=[("", "---")] + C.BDC_CHOICES,
        required=False,
        label="BDC (Bruits du Cœur)",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__souffle_cardiaque = forms.ChoiceField(
        choices=[("", "---")] + C.SOUFFLE_CARDIAQUE_CHOICES,
        required=False,
        label="Souffle cardiaque",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__intensite_souffle_levine = forms.ChoiceField(
        choices=[("", "---")] + C.LEVINE_CHOICES,
        required=False,
        label="Intensité souffle (Levine)",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__localisation_souffle = forms.ChoiceField(
        choices=[("", "---")] + C.LOCALISATION_SOUFFLE_CHOICES,
        required=False,
        label="Localisation souffle",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__bruits_surajoutes = forms.ChoiceField(
        choices=[("", "---")] + C.BRUITS_SURAJOUTES_CHOICES,
        required=False,
        label="Bruits surajoutés",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__dedoublement = forms.ChoiceField(
        choices=[("", "---")] + C.DEDOUBLEMENT_CHOICES,
        required=False,
        label="Dédoublement",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Textes libres
    exceptions = forms.CharField(
        required=False,
        label="Autres précisions",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    conclusion = forms.CharField(
        required=False,
        label="Conclusion cardiovasculaire",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


# ============================================================
# APPAREIL DIGESTIF
# ============================================================

class DigestifForm(BaseExamenAppareilForm):
    """Sous-formulaire pour l'appareil digestif."""
    
    appareil_key = "digestif"
    
    # Inspection
    inspection__volume_abdominal = forms.ChoiceField(
        choices=[("", "---")] + C.VOLUME_ABDOMINAL_CHOICES,
        required=False,
        label="Volume abdominal",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__voussures = forms.ChoiceField(
        choices=[("", "---")] + C.VOUSSURES_CHOICES,
        required=False,
        label="Voussures",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__circulation_collaterale = forms.ChoiceField(
        choices=[("", "---")] + C.CIRCULATION_COLLATERALE_CHOICES,
        required=False,
        label="Circulation collatérale",
        widget=forms.RadioSelect,
    )
    
    inspection__ombilic = forms.ChoiceField(
        choices=[("", "---")] + C.OMBILIC_CHOICES,
        required=False,
        label="Ombilic",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Palpation
    palpation__souplesse_abdominale = forms.ChoiceField(
        choices=[("", "---")] + C.SOUPLESSE_ABDOMINALE_CHOICES,
        required=False,
        label="Souplesse abdominale",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__douleur = forms.ChoiceField(
        choices=[("", "---")] + C.DOULEUR_ABDOMINALE_CHOICES,
        required=False,
        label="Douleur",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__localisation_douleur = forms.CharField(
        required=False,
        label="Localisation douleur (si localisée)",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    palpation__signe_de_murphy = forms.ChoiceField(
        choices=[("", "---")] + C.SIGNE_MURPHY_CHOICES,
        required=False,
        label="Signe de Murphy",
        widget=forms.RadioSelect,
    )
    
    palpation__point_de_mcburney = forms.ChoiceField(
        choices=[("", "---")] + C.POINT_MCBURNEY_CHOICES,
        required=False,
        label="Point de McBurney",
        widget=forms.RadioSelect,
    )
    
    palpation__hepatomegalie = forms.ChoiceField(
        choices=[("", "---")] + C.HEPATOMEGALIE_CHOICES,
        required=False,
        label="Hépatomégalie",
        widget=forms.RadioSelect,
    )
    
    palpation__taille_hepatomegalie_cm = forms.DecimalField(
        required=False,
        label="Taille hépatomégalie (cm)",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0, "step": "0.1"}),
    )
    
    palpation__splenomegalie = forms.ChoiceField(
        choices=[("", "---")] + C.SPLENOMEGALIE_CHOICES,
        required=False,
        label="Splénomégalie",
        widget=forms.RadioSelect,
    )
    
    palpation__taille_splenomegalie_cm = forms.DecimalField(
        required=False,
        label="Taille splénomégalie (cm)",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0, "step": "0.1"}),
    )
    
    palpation__masse_palpable = forms.ChoiceField(
        choices=[("", "---")] + C.MASSE_PALPABLE_CHOICES,
        required=False,
        label="Masse palpable",
        widget=forms.RadioSelect,
    )
    
    palpation__localisation_masse = forms.CharField(
        required=False,
        label="Localisation masse",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    palpation__globe_vesical = forms.ChoiceField(
        choices=[("", "---")] + C.GLOBE_VESICAL_CHOICES,
        required=False,
        label="Globe vésical",
        widget=forms.RadioSelect,
    )
    
    palpation__pli_cutane = forms.ChoiceField(
        choices=[("", "---")] + C.PLI_CUTANE_CHOICES,
        required=False,
        label="Pli cutané (déshydratation)",
        widget=forms.RadioSelect,
    )
    
    # Percussion
    percussion__sonorite_abdominale = forms.ChoiceField(
        choices=[("", "---")] + C.SONORITE_ABDOMINALE_CHOICES,
        required=False,
        label="Sonorité abdominale",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    percussion__matite_hepatique = forms.ChoiceField(
        choices=[("", "---")] + C.MATITE_HEPATIQUE_CHOICES,
        required=False,
        label="Matité hépatique",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    percussion__matite_declive = forms.ChoiceField(
        choices=[("", "---")] + C.MATITE_DECLIVE_CHOICES,
        required=False,
        label="Matité déclive",
        widget=forms.RadioSelect,
    )
    
    # Auscultation
    auscultation__bruits_hydro_aeriques = forms.ChoiceField(
        choices=[("", "---")] + C.BRUITS_HYDRO_AERIQUES_CHOICES,
        required=False,
        label="Bruits hydro-aériques",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    auscultation__souffle_vasculaire = forms.ChoiceField(
        choices=[("", "---")] + C.SOUFFLE_VASCULAIRE_CHOICES,
        required=False,
        label="Souffle vasculaire",
        widget=forms.RadioSelect,
    )
    
    # Émission
    emission__selles = forms.MultipleChoiceField(
        choices=C.SELLES_CHOICES,
        required=False,
        label="Selles",
        widget=forms.CheckboxSelectMultiple,
    )
    
    emission__vomissements = forms.MultipleChoiceField(
        choices=C.VOMISSEMENTS_CHOICES,
        required=False,
        label="Vomissements",
        widget=forms.CheckboxSelectMultiple,
    )
    
    emission__emission_meconium = forms.ChoiceField(
        choices=[("", "---")] + C.MECONIUM_CHOICES,
        required=False,
        label="Émission de méconium",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    emission__autres_precisions = forms.CharField(
        required=False,
        label="Autres précisions",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    # Textes libres
    exceptions = forms.CharField(
        required=False,
        label="Autres précisions",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    conclusion = forms.CharField(
        required=False,
        label="Conclusion digestive",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


# ============================================================
# APPAREIL NEUROLOGIQUE
# ============================================================

class NeurologiqueForm(BaseExamenAppareilForm):
    """Sous-formulaire pour l'appareil neurologique."""
    
    appareil_key = "neurologique"
    
    # Inspection
    inspection__etat_de_conscience = forms.ChoiceField(
        choices=[("", "---")] + C.ETAT_CONSCIENCE_CHOICES,
        required=False,
        label="État de conscience",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__score_glasgow = forms.IntegerField(
        required=False,
        label="Score de Glasgow (3-15)",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 3, "max": 15}),
    )
    
    inspection__score_blantyre = forms.IntegerField(
        required=False,
        label="Score de Blantyre (0-5)",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 5}),
    )
    
    inspection__mouvements_anormaux = forms.MultipleChoiceField(
        choices=C.MOUVEMENTS_ANORMAUX_CHOICES,
        required=False,
        label="Mouvements anormaux",
        widget=forms.CheckboxSelectMultiple,
    )
    
    inspection__attitude_posture = forms.ChoiceField(
        choices=[("", "---")] + C.ATTITUDE_POSTURE_CHOICES,
        required=False,
        label="Attitude / Posture",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__pupilles = forms.ChoiceField(
        choices=[("", "---")] + C.PUPILLES_CHOICES,
        required=False,
        label="Pupilles",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Palpation
    palpation__fontanelle = forms.ChoiceField(
        choices=[("", "---")] + C.FONTANELLE_CHOICES,
        required=False,
        label="Fontanelle",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__permeabilite_sutures = forms.CharField(
        required=False,
        label="Perméabilité sutures (travers de doigt)",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    palpation__raideur_nuque = forms.ChoiceField(
        choices=[("", "---")] + C.RAIDEUR_NUQUE_CHOICES,
        required=False,
        label="Raideur de nuque",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__signe_kernig_bragard = forms.ChoiceField(
        choices=[("", "---")] + C.KERNIG_BRAGARD_CHOICES,
        required=False,
        label="Signe de Kernig/Bragard",
        widget=forms.RadioSelect,
    )
    
    palpation__ton_musculaire = forms.ChoiceField(
        choices=[("", "---")] + C.TON_MUSCULAIRE_CHOICES,
        required=False,
        label="Ton musculaire",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__force_musculaire = forms.ChoiceField(
        choices=[("", "---")] + C.FORCE_MUSCULAIRE_CHOICES,
        required=False,
        label="Force musculaire",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__sensibilite = forms.ChoiceField(
        choices=[("", "---")] + C.SENSIBILITE_CHOICES,
        required=False,
        label="Sensibilité",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Réflexes
    reflexes__reflexes_osteo_tendineux = forms.ChoiceField(
        choices=[("", "---")] + C.REFLEXES_OSTEO_TENDINEUX_CHOICES,
        required=False,
        label="Réflexes ostéo-tendineux",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    reflexes__babinski = forms.ChoiceField(
        choices=[("", "---")] + C.BABINSKI_CHOICES,
        required=False,
        label="Signe de Babinski",
        widget=forms.RadioSelect,
    )
    
    reflexes__reflexes_archaiques = forms.MultipleChoiceField(
        choices=C.REFLEXES_ARCHEAQUES_CHOICES,
        required=False,
        label="Réflexes archaïques",
        widget=forms.CheckboxSelectMultiple,
    )
    
    # Textes libres
    exceptions = forms.CharField(
        required=False,
        label="Autres précisions",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    conclusion = forms.CharField(
        required=False,
        label="Conclusion neurologique",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


# ============================================================
# SPHÈRE ORL (TÊTE ET COU)
# ============================================================

class ORLForm(BaseExamenAppareilForm):
    """Sous-formulaire pour la sphère ORL (tête et cou)."""
    
    appareil_key = "orl"
    
    # Inspection
    inspection__pc_cm = forms.DecimalField(
        required=False,
        label="PC (cm)",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0, "step": "0.1"}),
    )
    
    inspection__dysmorphie_faciale = forms.ChoiceField(
        choices=[("", "---")] + C.DYSMORPHIE_FACIALE_CHOICES,
        required=False,
        label="Dysmorphie faciale",
        widget=forms.RadioSelect,
    )
    
    inspection__type_dysmorphie = forms.CharField(
        required=False,
        label="Type dysmorphie (si présente)",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    inspection__yeux = forms.MultipleChoiceField(
        choices=C.YEUX_CHOICES,
        required=False,
        label="Yeux",
        widget=forms.CheckboxSelectMultiple,
    )
    
    inspection__nez = forms.MultipleChoiceField(
        choices=C.NEZ_CHOICES,
        required=False,
        label="Nez",
        widget=forms.CheckboxSelectMultiple,
    )
    
    inspection__oreilles = forms.MultipleChoiceField(
        choices=C.OREILLES_CHOICES,
        required=False,
        label="Oreilles",
        widget=forms.CheckboxSelectMultiple,
    )
    
    inspection__levres = forms.ChoiceField(
        choices=[("", "---")] + C.LEVRES_CHOICES,
        required=False,
        label="Lèvres",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__muqueuse_buccale = forms.MultipleChoiceField(
        choices=C.MUQUEUSE_BUCCALE_CHOICES,
        required=False,
        label="Muqueuse buccale",
        widget=forms.CheckboxSelectMultiple,
    )
    
    inspection__langue = forms.ChoiceField(
        choices=[("", "---")] + C.LANGUE_CHOICES,
        required=False,
        label="Langue",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__amygdales = forms.ChoiceField(
        choices=[("", "---")] + C.AMYgDALES_CHOICES,
        required=False,
        label="Amygdales",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__fente_bec_lievre = forms.ChoiceField(
        choices=[("", "---")] + C.FENTE_CHOICES,
        required=False,
        label="Fente / Bec de lièvre",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__frein_langue = forms.ChoiceField(
        choices=[("", "---")] + C.FREIN_LANGUE_CHOICES,
        required=False,
        label="Frein de langue",
        widget=forms.RadioSelect,
    )
    
    inspection__cou_mobilite = forms.ChoiceField(
        choices=[("", "---")] + C.COU_MOBILITE_CHOICES,
        required=False,
        label="Cou - Mobilité",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__adenopathies_cervicales = forms.ChoiceField(
        choices=[("", "---")] + C.ADENOPATHIES_CERVICALES_CHOICES,
        required=False,
        label="Adénopathies cervicales",
        widget=forms.RadioSelect,
    )
    
    inspection__hematome_scm = forms.ChoiceField(
        choices=[("", "---")] + C.HEMATOME_SCM_CHOICES,
        required=False,
        label="Hématome SCM",
        widget=forms.RadioSelect,
    )
    
    # Palpation
    palpation__ganglions_cervicaux = forms.MultipleChoiceField(
        choices=C.GANGLIONS_CERVICAUX_CHOICES,
        required=False,
        label="Ganglions cervicaux",
        widget=forms.CheckboxSelectMultiple,
    )
    
    palpation__masse_cervicale = forms.ChoiceField(
        choices=[("", "---")] + C.MASSE_CERVICALE_CHOICES,
        required=False,
        label="Masse cervicale",
        widget=forms.RadioSelect,
    )
    
    palpation__thyroide = forms.ChoiceField(
        choices=[("", "---")] + C.THYROIDE_CHOICES,
        required=False,
        label="Thyroïde",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Textes libres
    exceptions = forms.CharField(
        required=False,
        label="Autres précisions",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    conclusion = forms.CharField(
        required=False,
        label="Conclusion ORL",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


# ============================================================
# REVÊTEMENT CUTANÉOMUQUEUX
# ============================================================

class CutaneomuqueuxForm(BaseExamenAppareilForm):
    """Sous-formulaire pour le revêtement cutanéomuqueux."""
    
    appareil_key = "cutaneomuqueux"
    
    # Inspection
    inspection__coloration = forms.MultipleChoiceField(
        choices=C.COLORATION_CUTANEE_CHOICES,
        required=False,
        label="Coloration",
        widget=forms.CheckboxSelectMultiple,
    )
    
    inspection__hydratation = forms.ChoiceField(
        choices=[("", "---")] + C.HYDRATATION_CHOICES,
        required=False,
        label="Hydratation",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    inspection__turgor_cutane = forms.ChoiceField(
        choices=[("", "---")] + C.TURGOR_CUTANE_CHOICES,
        required=False,
        label="Turgor cutané",
        widget=forms.RadioSelect,
    )
    
    inspection__eruption_exantheme = forms.MultipleChoiceField(
        choices=C.ERUPTION_CHOICES,
        required=False,
        label="Éruption / Exanthème",
        widget=forms.CheckboxSelectMultiple,
    )
    
    inspection__desquamation = forms.ChoiceField(
        choices=[("", "---")] + C.DESQUAMATION_CHOICES,
        required=False,
        label="Desquamation",
        widget=forms.RadioSelect,
    )
    
    inspection__purpura = forms.ChoiceField(
        choices=[("", "---")] + C.PURPURA_CHOICES,
        required=False,
        label="Purpura",
        widget=forms.RadioSelect,
    )
    
    inspection__petechies = forms.ChoiceField(
        choices=[("", "---")] + C.PETECHIES_CHOICES,
        required=False,
        label="Pétéchies",
        widget=forms.RadioSelect,
    )
    
    inspection__syndrome_hemorragique = forms.ChoiceField(
        choices=[("", "---")] + C.SYNDROME_HEMORRAGIQUE_CHOICES,
        required=False,
        label="Syndrome hémorragique",
        widget=forms.RadioSelect,
    )
    
    inspection__oedemes = forms.ChoiceField(
        choices=[("", "---")] + C.OEDEMES_CHOICES,
        required=False,
        label="Œdèmes",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Palpation
    palpation__temperature_cutanee = forms.ChoiceField(
        choices=[("", "---")] + C.TEMPERATURE_CUTANEE_CHOICES,
        required=False,
        label="Température cutanée",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    palpation__texture = forms.ChoiceField(
        choices=[("", "---")] + C.TEXTURE_CUTANEE_CHOICES,
        required=False,
        label="Texture",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Textes libres
    exceptions = forms.CharField(
        required=False,
        label="Autres précisions",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    conclusion = forms.CharField(
        required=False,
        label="Conclusion cutanéomuqueux",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


# ============================================================
# APPAREILS GÉNITAUX
# ============================================================

class GenitauxForm(BaseExamenAppareilForm):
    """Sous-formulaire pour les appareils génitaux."""
    
    appareil_key = "genitaux"
    
    # Chez la fille
    fille__petite_levre_clitoris = forms.CharField(
        required=False,
        label="Petite lèvre et clitoris",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    fille__grande_levre = forms.CharField(
        required=False,
        label="Grande lèvre",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    fille__orifices_verifies = forms.ChoiceField(
        choices=[("", "---")] + [(str(v), l) for v, l in C.OUI_NON_CHOICES],
        required=False,
        label="Orifices vérifiés",
        widget=forms.RadioSelect,
    )
    
    fille__secretion_vaginale_metrorragie = forms.ChoiceField(
        choices=[("", "---")] + [(str(v), l) for v, l in C.OUI_NON_CHOICES],
        required=False,
        label="Sécrétion vaginale / métrorragie",
        widget=forms.RadioSelect,
    )
    
    # Chez le garçon
    garcon__scrotum = forms.CharField(
        required=False,
        label="Scrotum",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    garcon__presence_testicules = forms.ChoiceField(
        choices=[("", "---")] + [(str(v), l) for v, l in C.OUI_NON_CHOICES],
        required=False,
        label="Présence testicules",
        widget=forms.RadioSelect,
    )
    
    garcon__mar = forms.ChoiceField(
        choices=[("", "---")] + [(str(v), l) for v, l in C.OUI_NON_CHOICES],
        required=False,
        label="Absence MAR",
        widget=forms.RadioSelect,
    )
    
    garcon__hydrocele_vaginale = forms.ChoiceField(
        choices=[("", "---")] + [(str(v), l) for v, l in C.OUI_NON_CHOICES],
        required=False,
        label="Hydrocèle vaginale",
        widget=forms.RadioSelect,
    )
    
    # Textes libres
    exceptions = forms.CharField(
        required=False,
        label="Autres précisions",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    conclusion = forms.CharField(
        required=False,
        label="Conclusion génitaux",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


# ============================================================
# APPAREIL OSTÉO-ARTICULAIRE
# ============================================================

class OsteoarticulaireForm(BaseExamenAppareilForm):
    """Sous-formulaire pour l'appareil ostéo-articulaire."""
    
    appareil_key = "osteoarticulaire"
    
    # Champs directs (pas de catégorie)
    ms = forms.CharField(
        required=False,
        label="MS (lésions, doigts, pli palmaire)",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    mi = forms.CharField(
        required=False,
        label="MI (orteils, malposition)",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    rachis = forms.CharField(
        required=False,
        label="Rachis (malformations)",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    hanche_lch = forms.ChoiceField(
        choices=[("", "---")] + C.HANCHE_LCH_CHOICES,
        required=False,
        label="Hanche (Recherche LCH)",
        widget=forms.RadioSelect,
    )
    
    # Textes libres
    exceptions = forms.CharField(
        required=False,
        label="Autres précisions",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    
    conclusion = forms.CharField(
        required=False,
        label="Conclusion ostéo-articulaire",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


# ============================================================
# LISTE DE TOUS LES SOUS-FORMULAIRES D'EXAMEN
# ============================================================

EXAM_SUBFORMS = [
    ("pleuropulmonaire", PleuropulmonaireForm, "Appareil pleuropulmonaire"),
    ("cardiovasculaire", CardiovasculaireForm, "Appareil cardiovasculaire"),
    ("digestif", DigestifForm, "Appareil digestif"),
    ("neurologique", NeurologiqueForm, "Appareil neurologique"),
    ("orl", ORLForm, "Sphère ORL (Tête et Cou)"),
    ("cutaneomuqueux", CutaneomuqueuxForm, "Revêtement cutanéomuqueux"),
    ("genitaux", GenitauxForm, "Appareils génitaux"),
    ("osteoarticulaire", OsteoarticulaireForm, "Appareil ostéo-articulaire"),
]


# ============================================================
# EXAMENS PARACLINIQUES
# ============================================================

class ExamenParacliniqueForm(forms.ModelForm):
    """
    Formulaire pour un examen paraclinique.
    Les choix du nom de l'examen sont dynamiques selon le type.
    La validation des choices est faite ici, pas dans le modèle.
    """
    date_examen = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        label="Date de l'examen",
    )

    date_resultat = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        label="Date du résultat",
    )

    # ✅ Champ sans choices fixe — les choices sont remplies dynamiquement
    nom_examen = forms.ChoiceField(
        required=False,
        label="Nom de l'examen",
    )

    class Meta:
        model = ExamenParaclinique
        fields = [
            "type_examen",
            "nom_examen",
            "nom_examen_autre",
            "date_examen",
            "date_resultat",
            "statut",
            "resultat",
            "fichier_resultat",
            "interpretation",
            "conclusion",
            "notes",
        ]
        widgets = {
            "type_examen": forms.RadioSelect,
            "statut": forms.Select,
            "resultat": forms.Textarea(attrs={"rows": 4}),
            "interpretation": forms.Textarea(attrs={"rows": 3}),
            "conclusion": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Déterminer le type d'examen sélectionné
        type_examen = None
        if self.data.get("type_examen"):
            type_examen = self.data.get("type_examen")
        elif self.instance.pk and self.instance.type_examen:
            type_examen = self.instance.type_examen

        # Remplir les choices selon le type
        if type_examen == "imagerie":
            self.fields["nom_examen"].choices = [("", "---")] + C.IMAGERIE_CHOICES
        elif type_examen == "biologie":
            self.fields["nom_examen"].choices = [("", "---")] + C.BIOLOGIE_CHOICES
        elif type_examen == "fonctionnel":
            self.fields["nom_examen"].choices = [("", "---")] + C.FONCTIONNEL_CHOICES
        elif type_examen == "autre":
            self.fields["nom_examen"].choices = [("", "---"), ("autre", "Autre")]
        else:
            # ✅ Fallback : accepter TOUTE valeur pour éviter l'erreur de validation
            # quand le type n'est pas encore sélectionné ou en mode édition
            self.fields["nom_examen"].choices = [("", "--- Choisir un type d'examen d'abord ---")]
            # Si une valeur existe déjà (mode édition), l'ajouter aux choices
            if self.instance.pk and self.instance.nom_examen:
                current_value = self.instance.nom_examen
                self.fields["nom_examen"].choices += [(current_value, current_value)]

    def clean(self):
        cleaned_data = super().clean()
        type_examen = cleaned_data.get("type_examen")
        nom_examen = cleaned_data.get("nom_examen")
        nom_examen_autre = cleaned_data.get("nom_examen_autre")

        # Si le type est "autre", le nom_examen_autre est requis
        if type_examen == "autre" and not nom_examen_autre:
            self.add_error("nom_examen_autre", "Veuillez préciser le nom de l'examen.")

        return cleaned_data
    

ExamenParacliniqueFormSet = inlineformset_factory(
    ObservationMedicale,
    ExamenParaclinique,
    form=ExamenParacliniqueForm,
    extra=2,
    can_delete=True,
)



