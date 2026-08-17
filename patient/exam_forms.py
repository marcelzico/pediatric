# patient/exam_forms.py
from copy import deepcopy

from django import forms

from . import constants as C


# ============================================================
# CHOIX MANQUANTS / ALIAS
# ============================================================

ABSENTES_PRESENTES_CHOICES = getattr(
    C,
    "ABSENTES_PRESENTES_CHOICES",
    [
        ("absentes", "Absentes"),
        ("presentes", "Présentes"),
    ],
)

AMYgDALES_CHOICES = getattr(
    C,
    "AMYgDALES_CHOICES",
    [
        ("normales", "Normales"),
        ("hypertrophiees", "Hypertrophiées"),
        ("erythemateuses", "Érythémateuses"),
        ("enduites", "Enduites"),
    ],
)


# ============================================================
# HELPERS JSON -> FORM / FORM -> JSON
# ============================================================

def flatten_json(data, parent_key="", sep="__"):
    """
    Transforme un JSON imbriqué en dictionnaire plat.
    Exemple :
        {"inspection": {"fr": 30}}
    devient :
        {"inspection__fr": 30}
    """
    items = {}

    if not isinstance(data, dict):
        return items

    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            items.update(flatten_json(value, new_key, sep=sep))
        else:
            items[new_key] = value

    return items


def unflatten_flat(flat_data, sep="__"):
    """
    Transforme un dictionnaire plat en JSON imbriqué.
    """
    result = {}

    for key, value in flat_data.items():
        parts = key.split(sep)
        current = result

        for part in parts[:-1]:
            current = current.setdefault(part, {})

        current[parts[-1]] = value

    return result


def deep_update(base, updates):
    """
    Met à jour un dictionnaire imbriqué sans écraser les clés non fournies.
    """
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_update(base[key], value)
        else:
            base[key] = value

    return base


# ============================================================
# HELPERS DE CHAMPS
# ============================================================

def optional_choice(choices, widget_class=forms.RadioSelect):
    return forms.ChoiceField(
        choices=[("", "---")] + list(choices),
        required=False,
        widget=widget_class(),
    )


def optional_select(choices):
    return optional_choice(choices, widget_class=forms.Select)


def optional_multiple(choices):
    return forms.MultipleChoiceField(
        choices=list(choices),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )


def optional_text():
    return forms.CharField(
        required=False,
        widget=forms.TextInput(),
    )


def optional_textarea(rows=2):
    return forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": rows}),
    )


def optional_integer(min_value=None, max_value=None):
    return forms.IntegerField(
        required=False,
        min_value=min_value,
        max_value=max_value,
    )


def optional_decimal():
    return forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
    )


class OuiNonField(forms.ChoiceField):
    """
    Champ Oui / Non / Inconnu qui stocke True / False / None dans le JSON.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault("choices", [("", "---"), ("true", "Oui"), ("false", "Non")])
        kwargs.setdefault("widget", forms.RadioSelect())
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        if value is True:
            return "true"
        if value is False:
            return "false"
        return ""

    def to_python(self, value):
        if value in (True, "True", "true", "1", "oui"):
            return True
        if value in (False, "False", "false", "0", "non"):
            return False
        return None

    def validate(self, value):
        # On neutralise la validation standard du ChoiceField
        # car la valeur finale est booléenne.
        pass


# ============================================================
# CLASSE DE BASE DES SOUS-FORMULAIRES D'EXAMEN
# ============================================================

class BaseExamenAppareilForm(forms.Form):
    """
    Classe de base pour éditer un JSONField d'examen clinique.

    Chaque formulaire :
    - lit le JSON existant,
    - le transforme en champs Django,
    - permet de le retransformer en JSON structuré.
    """

    appareil_key = None

    CATEGORY_LABELS = {
        "inspection": "Inspection",
        "palpation": "Palpation",
        "percussion": "Percussion",
        "auscultation": "Auscultation",
        "emission": "Émission",
        "reflexes": "Réflexes",
        "fille": "Chez la fille",
        "garcon": "Chez le garçon",
        "general": "Exceptions / Conclusion",
    }

    def __init__(self, *args, json_data=None, **kwargs):
        self.json_data = json_data if isinstance(json_data, dict) else {}

        initial = flatten_json(
            deepcopy(C.EXAMEN_DEFAULTS.get(self.appareil_key, {}))
        )
        initial.update(flatten_json(self.json_data))

        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    def get_json(self):
        if not self.is_valid():
            raise ValueError("Le formulaire d'examen doit être valide avant conversion JSON.")

        base = deepcopy(C.EXAMEN_DEFAULTS.get(self.appareil_key, {}))

        flat = {}
        for field_name in self.fields.keys():
            flat[field_name] = self.cleaned_data.get(field_name)

        updates = unflatten_flat(flat)
        return deep_update(base, updates)

    def grouped_fields(self):
        """
        Regroupe les champs visibles par catégorie :
        inspection, palpation, percussion, auscultation, etc.
        """
        groups = {}
        order = []

        for bound_field in self.visible_fields():
            name = bound_field.name

            if "__" in name:
                category_key = name.split("__", 1)[0]
            else:
                category_key = "general"

            if category_key not in groups:
                groups[category_key] = []
                order.append(category_key)

            groups[category_key].append(bound_field)

        return [
            (self.CATEGORY_LABELS.get(key, key.replace("_", " ").capitalize()), groups[key])
            for key in order
        ]


# ============================================================
# APPAREIL PLEUROPULMONAIRE
# ============================================================

class PleuroPulmonaireExamenForm(BaseExamenAppareilForm):
    appareil_key = "pleuropulmonaire"

    inspection__frequence_respiratoire = optional_integer(
        min_value=0,
        max_value=200,
    )
    inspection__frequence_respiratoire.label = "Fréquence respiratoire (cpm)"

    inspection__type_respiration = optional_choice(C.TYPE_RESPIRATION_CHOICES)
    inspection__type_respiration.label = "Type de respiration"

    inspection__amplitude_thoracique = optional_choice(C.AMPLITUDE_THORACIQUE_CHOICES)
    inspection__amplitude_thoracique.label = "Amplitude thoracique"

    inspection__symetrie_thoracique = optional_choice(C.SYMETRIE_THORACIQUE_CHOICES)
    inspection__symetrie_thoracique.label = "Symétrie thoracique"

    inspection__signes_de_lutte = optional_multiple(C.SIGNES_LUTTE_CHOICES)
    inspection__signes_de_lutte.label = "Signes de lutte"

    inspection__turgescence_jugulaire = optional_choice(C.ABSENTE_PRESENTE_CHOICES)
    inspection__turgescence_jugulaire.label = "Turgescence jugulaire"

    inspection__deformation_thoracique = optional_choice(C.DEFORMATION_THORACIQUE_CHOICES)
    inspection__deformation_thoracique.label = "Déformation thoracique"

    palpation__vibrations_vocales = optional_choice(C.VIBRATIONS_VOCALES_CHOICES)
    palpation__vibrations_vocales.label = "Vibrations vocales"

    palpation__expansion_thoracique = optional_choice(C.EXPANSION_THORACIQUE_CHOICES)
    palpation__expansion_thoracique.label = "Expansion thoracique"

    palpation__douleur_palpation = optional_choice(C.ABSENTE_PRESENTE_CHOICES)
    palpation__douleur_palpation.label = "Douleur à la palpation"

    palpation__crepitations_sous_cutanees = optional_choice(ABSENTES_PRESENTES_CHOICES)
    palpation__crepitations_sous_cutanees.label = "Crépitations sous-cutanées"

    percussion__sonorite_globale = optional_choice(C.SONORITE_PULMONAIRE_CHOICES)
    percussion__sonorite_globale.label = "Sonorité globale"

    percussion__localisation_anormale = optional_choice(C.LOCALISATION_PULMONAIRE_CHOICES)
    percussion__localisation_anormale.label = "Localisation anormale"

    percussion__mobilite_bord_inferieur_poumon = optional_choice(
        C.MOBILITE_BORD_INFERIEUR_POUMON_CHOICES
    )
    percussion__mobilite_bord_inferieur_poumon.label = "Mobilité du bord inférieur du poumon"

    auscultation__murmure_vesiculaire = optional_choice(C.MURMURE_VESICULAIRE_CHOICES)
    auscultation__murmure_vesiculaire.label = "Murmure vésiculaire"

    auscultation__rales_crepitants = optional_choice(C.RALES_CREPITANTS_CHOICES)
    auscultation__rales_crepitants.label = "Râles crépitants"

    auscultation__rales_sous_crepitants = optional_choice(C.RALES_SOUS_CREPITANTS_CHOICES)
    auscultation__rales_sous_crepitants.label = "Râles sous-crépitants"

    auscultation__sibilances = optional_multiple(C.SIBILANCES_CHOICES)
    auscultation__sibilances.label = "Sibilances / Wheezing"

    auscultation__rales_ronflants = optional_choice(C.RALES_RONFLANTS_CHOICES)
    auscultation__rales_ronflants.label = "Râles ronflants"

    auscultation__souffle_tubaire = optional_choice(C.SOUFFLE_TUBAIRE_CHOICES)
    auscultation__souffle_tubaire.label = "Souffle tubaire"

    auscultation__frottement_pleural = optional_choice(C.FROTTEMENT_PLEURAL_CHOICES)
    auscultation__frottement_pleural.label = "Frottement pleural"

    auscultation__localisation_anomalies = optional_multiple(C.LOCALISATION_PULMONAIRE_CHOICES)
    auscultation__localisation_anomalies.label = "Localisation des anomalies"

    exceptions = optional_textarea(3)
    exceptions.label = "Exceptions / Imprévus"

    conclusion = optional_textarea(3)
    conclusion.label = "Conclusion pleuropulmonaire"


# ============================================================
# APPAREIL CARDIOVASCULAIRE
# ============================================================

class CardiovasculaireExamenForm(BaseExamenAppareilForm):
    appareil_key = "cardiovasculaire"

    inspection__cyanose = optional_choice(C.CYANOSE_CHOICES)
    inspection__paleur = optional_choice(C.PALEUR_CHOICES)
    inspection__ictere = optional_choice(C.ABSENT_PRESENT_CHOICES)
    inspection__oedemes = optional_choice(C.OEDEMES_CHOICES)
    inspection__turgescence_jugulaire = optional_choice(C.ABSENTE_PRESENTE_CHOICES)
    inspection__hippocratisme_digital = optional_choice(C.HIPPOCRATISME_DIGITAL_CHOICES)

    palpation__frequence_cardiaque = optional_integer(min_value=0, max_value=250)
    palpation__frequence_cardiaque.label = "Fréquence cardiaque (bpm)"

    palpation__choc_de_pointe = optional_choice(C.CHOC_DE_POINTE_CHOICES)
    palpation__rythme = optional_choice(C.RYTHME_CARDIAQUE_CHOICES)
    palpation__thrill = optional_choice(C.ABSENT_PRESENT_CHOICES)
    palpation__thrill.label = "Thrill (frémissement)"

    palpation__chaleur_extremites = optional_choice(C.CHALEUR_EXTREMITES_CHOICES)

    palpation__trc_secondes = optional_integer(min_value=0, max_value=15)
    palpation__trc_secondes.label = "TRC (secondes)"

    palpation__pouls_peripheriques = optional_choice(C.POULS_PERIPHERIQUES_CHOICES)
    palpation__pouls_femoraux = optional_choice(C.POULS_FEMORAUX_CHOICES)

    percussion__matite_cardiaque = optional_choice(C.MATITE_CARDIAQUE_CHOICES)

    auscultation__bdc = optional_choice(C.BDC_CHOICES)
    auscultation__bdc.label = "BDC (Bruits du Cœur)"

    auscultation__souffle_cardiaque = optional_choice(C.SOUFFLE_CARDIAQUE_CHOICES)
    auscultation__intensite_souffle_levine = optional_choice(C.LEVINE_CHOICES)
    auscultation__intensite_souffle_levine.label = "Intensité du souffle (Levine)"

    auscultation__localisation_souffle = optional_select(C.LOCALISATION_SOUFFLE_CHOICES)
    auscultation__localisation_souffle.label = "Localisation du souffle"

    auscultation__bruits_surajoutes = optional_choice(C.BRUITS_SURAJOUTES_CHOICES)
    auscultation__dedoublement = optional_choice(C.DEDOUBLEMENT_CHOICES)

    exceptions = optional_textarea(3)
    exceptions.label = "Exceptions / Imprévus"

    conclusion = optional_textarea(3)
    conclusion.label = "Conclusion cardiovasculaire"


# ============================================================
# APPAREIL DIGESTIF
# ============================================================

class DigestifExamenForm(BaseExamenAppareilForm):
    appareil_key = "digestif"

    inspection__volume_abdominal = optional_choice(C.VOLUME_ABDOMINAL_CHOICES)
    inspection__voussures = optional_choice(C.VOUSSURES_CHOICES)
    inspection__circulation_collaterale = optional_choice(C.CIRCULATION_COLLATERALE_CHOICES)
    inspection__ombilic = optional_choice(C.OMBILIC_CHOICES)

    palpation__souplesse_abdominale = optional_choice(C.SOUPLESSE_ABDOMINALE_CHOICES)
    palpation__douleur = optional_choice(C.DOULEUR_ABDOMINALE_CHOICES)

    palpation__localisation_douleur = optional_text()
    palpation__localisation_douleur.label = "Localisation de la douleur"

    palpation__signe_de_murphy = optional_choice(C.SIGNE_MURPHY_CHOICES)
    palpation__point_de_mcburney = optional_choice(C.POINT_MCBURNEY_CHOICES)

    palpation__hepatomegalie = optional_choice(C.HEPATOMEGALIE_CHOICES)

    palpation__taille_hepatomegalie_cm = optional_decimal()
    palpation__taille_hepatomegalie_cm.label = "Taille hépatomégalie (cm)"

    palpation__splenomegalie = optional_choice(C.SPLENOMEGALIE_CHOICES)

    palpation__taille_splenomegalie_cm = optional_decimal()
    palpation__taille_splenomegalie_cm.label = "Taille splénomégalie (cm)"

    palpation__masse_palpable = optional_choice(C.MASSE_PALPABLE_CHOICES)

    palpation__localisation_masse = optional_text()
    palpation__localisation_masse.label = "Localisation de la masse"

    palpation__globe_vesical = optional_choice(C.GLOBE_VESICAL_CHOICES)
    palpation__pli_cutane = optional_choice(C.PLI_CUTANE_CHOICES)

    percussion__sonorite_abdominale = optional_choice(C.SONORITE_ABDOMINALE_CHOICES)
    percussion__matite_hepatique = optional_choice(C.MATITE_HEPATIQUE_CHOICES)
    percussion__matite_declive = optional_choice(C.MATITE_DECLIVE_CHOICES)

    auscultation__bruits_hydro_aeriques = optional_choice(C.BRUITS_HYDRO_AERIQUES_CHOICES)
    auscultation__souffle_vasculaire = optional_choice(C.SOUFFLE_VASCULAIRE_CHOICES)

    emission__selles = optional_multiple(C.SELLES_CHOICES)
    emission__vomissements = optional_multiple(C.VOMISSEMENTS_CHOICES)
    emission__emission_meconium = optional_choice(C.MECONIUM_CHOICES)
    emission__emission_meconium.label = "Émission de méconium"

    emission__autres_precisions = optional_textarea(2)
    emission__autres_precisions.label = "Autres précisions"

    exceptions = optional_textarea(3)
    exceptions.label = "Exceptions / Imprévus"

    conclusion = optional_textarea(3)
    conclusion.label = "Conclusion digestive"


# ============================================================
# APPAREIL NEUROLOGIQUE
# ============================================================

class NeurologiqueExamenForm(BaseExamenAppareilForm):
    appareil_key = "neurologique"

    inspection__etat_de_conscience = optional_choice(C.ETAT_CONSCIENCE_CHOICES)

    inspection__score_glasgow = optional_integer(min_value=3, max_value=15)
    inspection__score_glasgow.label = "Score de Glasgow (3-15)"

    inspection__score_blantyre = optional_integer(min_value=0, max_value=5)
    inspection__score_blantyre.label = "Score de Blantyre (0-5)"

    inspection__mouvements_anormaux = optional_multiple(C.MOUVEMENTS_ANORMAUX_CHOICES)
    inspection__attitude_posture = optional_choice(C.ATTITUDE_POSTURE_CHOICES)
    inspection__attitude_posture.label = "Attitude / Posture"

    inspection__pupilles = optional_choice(C.PUPILLES_CHOICES)

    palpation__fontanelle = optional_choice(C.FONTANELLE_CHOICES)

    palpation__permeabilite_sutures = optional_text()
    palpation__permeabilite_sutures.label = "Perméabilité des sutures (travers de doigt)"

    palpation__raideur_nuque = optional_choice(C.RAIDEUR_NUQUE_CHOICES)
    palpation__signe_kernig_bragard = optional_choice(C.KERNIG_BRAGARD_CHOICES)
    palpation__signe_kernig_bragard.label = "Signe de Kernig / Bragard"

    palpation__ton_musculaire = optional_choice(C.TON_MUSCULAIRE_CHOICES)
    palpation__force_musculaire = optional_choice(C.FORCE_MUSCULAIRE_CHOICES)
    palpation__sensibilite = optional_choice(C.SENSIBILITE_CHOICES)

    reflexes__reflexes_osteo_tendineux = optional_choice(C.REFLEXES_OSTEO_TENDINEUX_CHOICES)
    reflexes__reflexes_osteo_tendineux.label = "Réflexes ostéo-tendineux"

    reflexes__babinski = optional_choice(C.BABINSKI_CHOICES)
    reflexes__reflexes_archaiques = optional_multiple(C.REFLEXES_ARCHEAQUES_CHOICES)
    reflexes__reflexes_archaiques.label = "Réflexes archaïques"

    exceptions = optional_textarea(3)
    exceptions.label = "Exceptions / Imprévus"

    conclusion = optional_textarea(3)
    conclusion.label = "Conclusion neurologique"


# ============================================================
# SPHÈRE ORL / TÊTE ET COU
# ============================================================

class ORLExamenForm(BaseExamenAppareilForm):
    appareil_key = "orl"

    inspection__pc_cm = optional_decimal()
    inspection__pc_cm.label = "PC (cm)"

    inspection__dysmorphie_faciale = optional_choice(C.DYSMORPHIE_FACIALE_CHOICES)

    inspection__type_dysmorphie = optional_text()
    inspection__type_dysmorphie.label = "Type de dysmorphie"

    inspection__yeux = optional_multiple(C.YEUX_CHOICES)
    inspection__nez = optional_multiple(C.NEZ_CHOICES)
    inspection__oreilles = optional_multiple(C.OREILLES_CHOICES)
    inspection__levres = optional_choice(C.LEVRES_CHOICES)
    inspection__muqueuse_buccale = optional_multiple(C.MUQUEUSE_BUCCALE_CHOICES)
    inspection__langue = optional_choice(C.LANGUE_CHOICES)
    inspection__amygdales = optional_choice(AMYgDALES_CHOICES)
    inspection__fente_bec_lievre = optional_choice(C.FENTE_CHOICES)
    inspection__fente_bec_lievre.label = "Fente / Bec de lièvre"
    inspection__frein_langue = optional_choice(C.FREIN_LANGUE_CHOICES)
    inspection__frein_langue.label = "Frein de langue"

    inspection__cou_mobilite = optional_choice(C.COU_MOBILITE_CHOICES)
    inspection__cou_mobilite.label = "Mobilité du cou"

    inspection__adenopathies_cervicales = optional_choice(C.ADENOPATHIES_CERVICALES_CHOICES)
    inspection__hematome_scm = optional_choice(C.HEMATOME_SCM_CHOICES)
    inspection__hematome_scm.label = "Hématome SCM"

    palpation__ganglions_cervicaux = optional_multiple(C.GANGLIONS_CERVICAUX_CHOICES)
    palpation__masse_cervicale = optional_choice(C.MASSE_CERVICALE_CHOICES)
    palpation__thyroide = optional_choice(C.THYROIDE_CHOICES)

    exceptions = optional_textarea(3)
    exceptions.label = "Exceptions / Imprévus"

    conclusion = optional_textarea(3)
    conclusion.label = "Conclusion ORL"


# ============================================================
# REVÊTEMENT CUTANÉOMUQUEUX
# ============================================================

class CutaneomuqueuxExamenForm(BaseExamenAppareilForm):
    appareil_key = "cutaneomuqueux"

    inspection__coloration = optional_multiple(C.COLORATION_CUTANEE_CHOICES)
    inspection__hydratation = optional_choice(C.HYDRATATION_CHOICES)
    inspection__turgor_cutane = optional_choice(C.TURGOR_CUTANE_CHOICES)

    inspection__eruption_exantheme = optional_multiple(C.ERUPTION_CHOICES)
    inspection__eruption_exantheme.label = "Éruption / Exanthème"

    inspection__desquamation = optional_choice(C.DESQUAMATION_CHOICES)
    inspection__purpura = optional_choice(C.PURPURA_CHOICES)
    inspection__petechies = optional_choice(C.PETECHIES_CHOICES)
    inspection__syndrome_hemorragique = optional_choice(C.SYNDROME_HEMORRAGIQUE_CHOICES)
    inspection__oedemes = optional_choice(C.OEDEMES_CHOICES)

    palpation__temperature_cutanee = optional_choice(C.TEMPERATURE_CUTANEE_CHOICES)
    palpation__texture = optional_choice(C.TEXTURE_CUTANEE_CHOICES)

    exceptions = optional_textarea(3)
    exceptions.label = "Exceptions / Imprévus"

    conclusion = optional_textarea(3)
    conclusion.label = "Conclusion cutanéomuqueuse"


# ============================================================
# APPAREILS GÉNITAUX
# ============================================================

class GenitauxExamenForm(BaseExamenAppareilForm):
    appareil_key = "genitaux"

    fille__petite_levre_clitoris = optional_text()
    fille__petite_levre_clitoris.label = "Petite lèvre et clitoris"

    fille__grande_levre = optional_text()
    fille__grande_levre.label = "Grande lèvre"

    fille__orifices_verifies = OuiNonField(label="Orifices vérifiés ?")

    fille__secretion_vaginale_metrorragie = OuiNonField(
        label="Sécrétion vaginale / métrorragie ?"
    )

    garcon__scrotum = optional_text()
    garcon__scrotum.label = "Scrotum"

    garcon__presence_testicules = OuiNonField(label="Présence des testicules ?")
    garcon__mar = OuiNonField(label="Absence de MAR ?")
    garcon__hydrocele_vaginale = OuiNonField(label="Hydrocèle vaginale ?")

    exceptions = optional_textarea(3)
    exceptions.label = "Exceptions / Imprévus"

    conclusion = optional_textarea(3)
    conclusion.label = "Conclusion génitaux"


# ============================================================
# APPAREIL OSTÉO-ARTICULAIRE
# ============================================================

class OsteoarticulaireExamenForm(BaseExamenAppareilForm):
    appareil_key = "osteoarticulaire"

    ms = optional_textarea(2)
    ms.label = "MS (lésions, doigts, pli palmaire)"

    mi = optional_textarea(2)
    mi.label = "MI (orteils, malposition)"

    rachis = optional_textarea(2)
    rachis.label = "Rachis (malformations)"

    hanche_lch = optional_choice(C.HANCHE_LCH_CHOICES)
    hanche_lch.label = "Hanche (Recherche LCH)"

    exceptions = optional_textarea(3)
    exceptions.label = "Exceptions / Imprévus"

    conclusion = optional_textarea(3)
    conclusion.label = "Conclusion ostéo-articulaire"


# ============================================================
# LISTE OFFICIELLE DES SOUS-FORMULAIRES
# ============================================================

EXAM_SUBFORMS = [
    ("pleuropulmonaire", PleuroPulmonaireExamenForm, "Appareil pleuropulmonaire"),
    ("cardiovasculaire", CardiovasculaireExamenForm, "Appareil cardiovasculaire"),
    ("digestif", DigestifExamenForm, "Appareil digestif"),
    ("neurologique", NeurologiqueExamenForm, "Appareil neurologique"),
    ("orl", ORLExamenForm, "Sphère ORL / Tête et cou"),
    ("cutaneomuqueux", CutaneomuqueuxExamenForm, "Revêtement cutanéomuqueux"),
    ("genitaux", GenitauxExamenForm, "Appareils génitaux"),
    ("osteoarticulaire", OsteoarticulaireExamenForm, "Appareil ostéo-articulaire"),
]
