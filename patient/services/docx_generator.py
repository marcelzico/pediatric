# patient/services/docx_generator.py
from io import BytesIO
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils.text import slugify

from docxtpl import DocxTemplate

from .. import constants as C


TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "docx_templates" / "observation.docx"


# ============================================================
# SUPPRESSION DES PARAGRAPHES VIDES
# ============================================================

def remove_empty_paragraphs(doc):
    """
    Supprime tous les paragraphes vides du corps du document.
    Cela élimine les lignes vides laissées par les balises Jinja
    ({% for %}, {% endfor %}, {% if %}, etc.) après le rendu.
    """
    for paragraph in list(doc.paragraphs):
        # On supprime uniquement les paragraphes complètement vides
        if not paragraph.text.strip():
            paragraph._element.getparent().remove(paragraph._element)


# ============================================================
# HELPERS GÉNÉRAUX
# ============================================================

def get_related(observation, related_name):
    if not observation:
        return None
    try:
        return getattr(observation, related_name)
    except ObjectDoesNotExist:
        return None


def is_empty(value):
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, tuple, set)) and not value:
        return True
    if isinstance(value, dict) and not value:
        return True
    return False


def clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def add_line(lines, label, value):
    value = clean_text(value)
    if not value:
        return
    lines.append(f"{label} : {value}")


def format_date(value):
    if not value:
        return ""
    try:
        return value.strftime("%d/%m/%Y")
    except Exception:
        return str(value)


def format_datetime(value):
    if not value:
        return ""
    try:
        return value.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(value)


def format_number(value):
    if is_empty(value):
        return ""
    try:
        text = format(value, "f")
    except Exception:
        return str(value)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def format_duration_heures(heures):
    if is_empty(heures):
        return ""
    try:
        total = int(heures)
    except Exception:
        return str(heures)
    if total < 1:
        return f"{total} h"
    return f"{total} h"


def yn(value):
    if value is True:
        return "Oui"
    if value is False:
        return "Non"
    if isinstance(value, str):
        low = value.lower().strip()
        if low in ("true", "1", "oui", "yes"):
            return "Oui"
        if low in ("false", "0", "non", "no"):
            return "Non"
        return value
    return ""


def _strip_key(key):
    """Supprime les espaces avant/après d'une clé."""
    if isinstance(key, str):
        return key.strip()
    return key


def _get_value(d, key):
    """Récupère une valeur dans un dict en gérant les clés avec espaces."""
    if not isinstance(d, dict):
        return None
    if key in d:
        return d[key]
    for k, v in d.items():
        if _strip_key(k) == key:
            return v
    return None


def _iter_dict_items(d):
    """Itère sur les items d'un dict en nettoyant les clés."""
    if not isinstance(d, dict):
        return []
    return [(_strip_key(k), v) for k, v in d.items()]


def display_choice(field_key, value):
    """Affiche la valeur d'un choice en utilisant le label lisible."""
    if is_empty(value):
        return ""

    if isinstance(value, bool):
        return yn(value)

    if isinstance(value, (list, tuple, set)):
        items = []
        for item in value:
            if not is_empty(item):
                displayed = display_choice(field_key, item)
                if displayed:
                    items.append(displayed)
        return ",`\n ".join(items)

    if isinstance(value, dict):
        return ""

    value_str = str(value).strip()

    # Chercher dans les choices constants
    choice_map = FIELD_CHOICE_MAP.get(field_key, {})
    if value_str in choice_map:
        return str(choice_map[value_str]).strip()

    # Chercher avec strip sur les clés
    for choice_value, choice_label in choice_map.items():
        if str(choice_value).strip() == value_str:
            return str(choice_label).strip()

    return value_str


# ============================================================
# MAPPING DES CHOICES
# ============================================================

def _choices_map(attr_name):
    """Construit un dict {valeur: label} depuis une constante de choices."""
    choices = getattr(C, attr_name, [])
    result = {}
    for item in choices:
        if len(item) == 2:
            val, label = item
            result[str(val).strip()] = str(label).strip()
    return result


FIELD_CHOICE_MAP = {
    # Antécédents familiaux
    "tares_familiales": _choices_map("TARES_FAMILIALES_CHOICES"),
    # Grossesse
    "pathologies_grossesse": _choices_map("PATHOLOGIES_GROSSESSE_CHOICES"),
    "conclusion_grossesse": _choices_map("CONCLUSION_GROSSESSE_CHOICES"),
    # Accouchement
    "presentation": _choices_map("PRESENTATION_CHOICES"),
    "terme": _choices_map("TERME_CHOICES"),
    "voie": _choices_map("VOIE_ACCOUCHEMENT_CHOICES"),
    "manoeuvre_obstetricale": _choices_map("MANOEUVRE_OBSTETRICALE_CHOICES"),
    "liquide_amniotique_couleur": _choices_map("COULEUR_LIQUIDE_AMNIOTIQUE_CHOICES"),
    "liquide_amniotique_abondance": _choices_map("ABONDANCE_LIQUIDE_AMNIOTIQUE_CHOICES"),
    "poids_naissance_type": _choices_map("POIDS_NAISSANCE_TYPE_CHOICES"),
    "type_accouchement": _choices_map("TYPE_ACCOUCHEMENT_CHOICES"),
    "adaptation_neonatale": _choices_map("ADAPTATION_NEONATALE_CHOICES"),
    # Alimentation
    "type_alimentation": _choices_map("ALIMENTATION_TYPE_CHOICES"),
    "regime": _choices_map("REGIME_CHOICES"),
    # Vaccination
    "vaccins_recus": _choices_map("VACCINS_CHOICES"),
    # Contexte épidémiologique
    "dyspnee_contexte": _choices_map("CONTEXTE_DYSPNEE_CHOICES"),
    "diarrhee_contexte": _choices_map("CONTEXTE_DIARRHEE_CHOICES"),
    # Fiche sociale
    "eclairage": _choices_map("ECLAIRAGE_CHOICES"),
    "eau": _choices_map("EAU_CHOICES"),
    "combustible": _choices_map("COMBUSTIBLE_CHOICES"),
    "wc": _choices_map("WC_CHOICES"),
    "niveau_social": _choices_map("NIVEAU_SOCIAL_CHOICES"),
    # Histoire de la maladie
    "evolution_episode": _choices_map("EVOLUTION_EPISODE_CHOICES"),
    # DPM
    "dpm_conclusion": _choices_map("DPM_CONCLUSION_CHOICES"),
    # Biométrie
    "biometrie_conclusion": _choices_map("BIOMETRIE_CONCLUSION_CHOICES"),
    "signes_3a2s": _choices_map("SIGNES_3A2S_CHOICES"),
    # Examens par appareil
    "type_respiration": _choices_map("TYPE_RESPIRATION_CHOICES"),
    "amplitude_thoracique": _choices_map("AMPLITUDE_THORACIQUE_CHOICES"),
    "symetrie_thoracique": _choices_map("SYMETRIE_THORACIQUE_CHOICES"),
    "signes_de_lutte": _choices_map("SIGNES_LUTTE_CHOICES"),
    "deformation_thoracique": _choices_map("DEFORMATION_THORACIQUE_CHOICES"),
    "turgescence_jugulaire": _choices_map("ABSENTE_PRESENTE_CHOICES"),
    "vibrations_vocales": _choices_map("VIBRATIONS_VOCALES_CHOICES"),
    "expansion_thoracique": _choices_map("EXPANSION_THORACIQUE_CHOICES"),
    "douleur_palpation": _choices_map("ABSENTE_PRESENTE_CHOICES"),
    "crepitations_sous_cutanees": _choices_map("ABSENTS_PRESENTS_CHOICES"),
    "sonorite_globale": _choices_map("SONORITE_PULMONAIRE_CHOICES"),
    "localisation_anormale": _choices_map("LOCALISATION_PULMONAIRE_CHOICES"),
    "mobilite_bord_inferieur_poumon": _choices_map("MOBILITE_BORD_INFERIEUR_POUMON_CHOICES"),
    "murmure_vesiculaire": _choices_map("MURMURE_VESICULAIRE_CHOICES"),
    "rales_crepitants": _choices_map("RALES_CREPITANTS_CHOICES"),
    "rales_sous_crepitants": _choices_map("RALES_SOUS_CREPITANTS_CHOICES"),
    "sibilances": _choices_map("SIBILANCES_CHOICES"),
    "rales_ronflants": _choices_map("RALES_RONFLANTS_CHOICES"),
    "souffle_tubaire": _choices_map("SOUFFLE_TUBAIRE_CHOICES"),
    "frottement_pleural": _choices_map("FROTTEMENT_PLEURAL_CHOICES"),
    "localisation_anomalies": _choices_map("LOCALISATION_PULMONAIRE_CHOICES"),
    # Cardiovasculaire
    "cyanose": _choices_map("CYANOSE_CHOICES"),
    "paleur": _choices_map("PALEUR_CHOICES"),
    "ictere": _choices_map("ABSENT_PRESENT_CHOICES"),
    "oedemes": _choices_map("OEDEMES_CHOICES"),
    "hippocratisme_digital": _choices_map("HIPPOCRATISME_DIGITAL_CHOICES"),
    "frequence_cardiaque": {},
    "choc_de_pointe": _choices_map("CHOC_DE_POINTE_CHOICES"),
    "rythme": _choices_map("RYTHME_CARDIAQUE_CHOICES"),
    "thrill": _choices_map("ABSENT_PRESENT_CHOICES"),
    "chaleur_extremites": _choices_map("CHALEUR_EXTREMITES_CHOICES"),
    "trc_secondes": {},
    "pouls_peripheriques": _choices_map("POULS_PERIPHERIQUES_CHOICES"),
    "pouls_femoraux": _choices_map("POULS_FEMORAUX_CHOICES"),
    "matite_cardiaque": _choices_map("MATITE_CARDIAQUE_CHOICES"),
    "bdc": _choices_map("BDC_CHOICES"),
    "souffle_cardiaque": _choices_map("SOUFFLE_CARDIAQUE_CHOICES"),
    "intensite_souffle_levine": _choices_map("LEVINE_CHOICES"),
    "localisation_souffle": _choices_map("LOCALISATION_SOUFFLE_CHOICES"),
    "bruits_surajoutes": _choices_map("BRUITS_SURAJOUTES_CHOICES"),
    "dedoublement": _choices_map("DEDOUBLEMENT_CHOICES"),
    # Digestif
    "volume_abdominal": _choices_map("VOLUME_ABDOMINAL_CHOICES"),
    "voussures": _choices_map("VOUSSURES_CHOICES"),
    "circulation_collaterale": _choices_map("CIRCULATION_COLLATERALE_CHOICES"),
    "ombilic": _choices_map("OMBILIC_CHOICES"),
    "souplesse_abdominale": _choices_map("SOUPLESSE_ABDOMINALE_CHOICES"),
    "douleur": _choices_map("DOULEUR_ABDOMINALE_CHOICES"),
    "localisation_douleur": {},
    "signe_de_murphy": _choices_map("SIGNE_MURPHY_CHOICES"),
    "point_de_mcburney": _choices_map("POINT_MCBURNEY_CHOICES"),
    "hepatomegalie": _choices_map("HEPATOMEGALIE_CHOICES"),
    "taille_hepatomegalie_cm": {},
    "splenomegalie": _choices_map("SPLENOMEGALIE_CHOICES"),
    "taille_splenomegalie_cm": {},
    "masse_palpable": _choices_map("MASSE_PALPABLE_CHOICES"),
    "localisation_masse": {},
    "globe_vesical": _choices_map("GLOBE_VESICAL_CHOICES"),
    "pli_cutane": _choices_map("PLI_CUTANE_CHOICES"),
    "sonorite_abdominale": _choices_map("SONORITE_ABDOMINALE_CHOICES"),
    "matite_hepatique": _choices_map("MATITE_HEPATIQUE_CHOICES"),
    "matite_declive": _choices_map("MATITE_DECLIVE_CHOICES"),
    "bruits_hydro_aeriques": _choices_map("BRUITS_HYDRO_AERIQUES_CHOICES"),
    "souffle_vasculaire": _choices_map("SOUFFLE_VASCULAIRE_CHOICES"),
    "selles": _choices_map("SELLES_CHOICES"),
    "vomissements": _choices_map("VOMISSEMENTS_CHOICES"),
    "emission_meconium": _choices_map("MECONIUM_CHOICES"),
    "autres_precisions": {},
    # Neurologique
    "etat_de_conscience": _choices_map("ETAT_CONSCIENCE_CHOICES"),
    "score_glasgow": {},
    "score_blantyre": {},
    "mouvements_anormaux": _choices_map("MOUVEMENTS_ANORMAUX_CHOICES"),
    "attitude_posture": _choices_map("ATTITUDE_POSTURE_CHOICES"),
    "pupilles": _choices_map("PUPILLES_CHOICES"),
    "fontanelle": _choices_map("FONTANELLE_CHOICES"),
    "permeabilite_sutures": {},
    "raideur_nuque": _choices_map("RAIDEUR_NUQUE_CHOICES"),
    "signe_kernig_bragard": _choices_map("KERNIG_BRAGARD_CHOICES"),
    "ton_musculaire": _choices_map("TON_MUSCULAIRE_CHOICES"),
    "force_musculaire": _choices_map("FORCE_MUSCULAIRE_CHOICES"),
    "sensibilite": _choices_map("SENSIBILITE_CHOICES"),
    "reflexes_osteo_tendineux": _choices_map("REFLEXES_OSTEO_TENDINEUX_CHOICES"),
    "babinski": _choices_map("BABINSKI_CHOICES"),
    "reflexes_archaiques": _choices_map("REFLEXES_ARCHEAQUES_CHOICES"),
    # ORL
    "pc_cm": {},
    "dysmorphie_faciale": _choices_map("DYSMORPHIE_FACIALE_CHOICES"),
    "type_dysmorphie": {},
    "yeux": _choices_map("YEUX_CHOICES"),
    "nez": _choices_map("NEZ_CHOICES"),
    "oreilles": _choices_map("OREILLES_CHOICES"),
    "levres": _choices_map("LEVRES_CHOICES"),
    "muqueuse_buccale": _choices_map("MUQUEUSE_BUCCALE_CHOICES"),
    "langue": _choices_map("LANGUE_CHOICES"),
    "amygdales": _choices_map("AMYgDALES_CHOICES"),
    "fente_bec_lievre": _choices_map("FENTE_CHOICES"),
    "frein_langue": _choices_map("FREIN_LANGUE_CHOICES"),
    "cou_mobilite": _choices_map("COU_MOBILITE_CHOICES"),
    "adenopathies_cervicales": _choices_map("ADENOPATHIES_CERVICALES_CHOICES"),
    "hematome_scm": _choices_map("HEMATOME_SCM_CHOICES"),
    "ganglions_cervicaux": _choices_map("GANGLIONS_CERVICAUX_CHOICES"),
    "masse_cervicale": _choices_map("MASSE_CERVICALE_CHOICES"),
    "thyroide": _choices_map("THYROIDE_CHOICES"),
    # Cutanéomuqueux
    "coloration": _choices_map("COLORATION_CUTANEE_CHOICES"),
    "hydratation": _choices_map("HYDRATATION_CHOICES"),
    "turgor_cutane": _choices_map("TURGOR_CUTANE_CHOICES"),
    "eruption_exantheme": _choices_map("ERUPTION_CHOICES"),
    "desquamation": _choices_map("DESQUAMATION_CHOICES"),
    "purpura": _choices_map("PURPURA_CHOICES"),
    "petechies": _choices_map("PETECHIES_CHOICES"),
    "syndrome_hemorragique": _choices_map("SYNDROME_HEMORRAGIQUE_CHOICES"),
    "temperature_cutanee": _choices_map("TEMPERATURE_CUTANEE_CHOICES"),
    "texture": _choices_map("TEXTURE_CUTANEE_CHOICES"),
    # Génitaux
    "petite_levre_clitoris": {},
    "grande_levre": {},
    "orifices_verifies": _choices_map("OUI_NON_CHOICES"),
    "secretion_vaginale_metrorragie": _choices_map("OUI_NON_CHOICES"),
    "scrotum": {},
    "presence_testicules": _choices_map("OUI_NON_CHOICES"),
    "mar": _choices_map("OUI_NON_CHOICES"),
    "hydrocele_vaginale": _choices_map("OUI_NON_CHOICES"),
    # Ostéo-articulaire
    "ms": {},
    "mi": {},
    "rachis": {},
    "hanche_lch": _choices_map("HANCHE_LCH_CHOICES"),
    # Suivi
    "signes_generaux": _choices_map("SIGNES_GENERAUX_SUIVI_CHOICES"),
    "signes_fonctionnels": _choices_map("SIGNES_FONCTIONNELS_SUIVI_CHOICES"),
    # Réhydratation
    "etat_yeux": _choices_map("ETAT_YEUX_CHOICES"),
    "etat_muqueuses": _choices_map("ETAT_MUQUEUSES_CHOICES"),
    "pli_cutane_rehydratation": _choices_map("PLI_CUTANE_REHYDRATATION_CHOICES"),
    "urine": _choices_map("URINE_CHOICES"),
    "selles_rehydratation": _choices_map("SELLES_REHYDRATATION_CHOICES"),
    "vomissements_rehydratation": _choices_map("VOMISSEMENTS_REHYDRATATION_CHOICES"),
    # Traitements ajustés
    "type_ajustement": _choices_map("TRAITEMENT_AJUSTEMENT_TYPE_CHOICES"),
    "type_ligne": _choices_map("TYPE_LIGNE_TRAITEMENT_CHOICES"),
    "voie_traitement": _choices_map("VOIE_TRAITEMENT_CHOICES"),
    "frequence_traitement": _choices_map("FREQUENCE_TRAITEMENT_CHOICES"),
}


# ============================================================
# LABELS HUMAINS POUR LES CLÉS JSON
# ============================================================

KEY_LABELS = {
    "frequence_respiratoire": "Fréquence respiratoire (cpm)",
    "type_respiration": "Type de respiration",
    "amplitude_thoracique": "Amplitude thoracique",
    "symetrie_thoracique": "Symétrie thoracique",
    "signes_de_lutte": "Signes de lutte",
    "turgescence_jugulaire": "Turgescence jugulaire",
    "deformation_thoracique": "Déformation thoracique",
    "vibrations_vocales": "Vibrations vocales",
    "expansion_thoracique": "Expansion thoracique",
    "douleur_palpation": "Douleur à la palpation",
    "crepitations_sous_cutanees": "Crépitations sous-cutanées",
    "sonorite_globale": "Sonorité globale",
    "localisation_anormale": "Localisation anormale",
    "mobilite_bord_inferieur_poumon": "Mobilité bord inférieur poumon",
    "murmure_vesiculaire": "Murmure vésiculaire",
    "rales_crepitants": "Râles crépitants",
    "rales_sous_crepitants": "Râles sous-crépitants",
    "sibilances": "Sibilances / Wheezing",
    "rales_ronflants": "Râles ronflants",
    "souffle_tubaire": "Souffle tubaire",
    "frottement_pleural": "Frottement pleural",
    "localisation_anomalies": "Localisation anomalies",
    "cyanose": "Cyanose",
    "paleur": "Pâleur",
    "ictere": "Ictère",
    "oedemes": "Œdèmes",
    "hippocratisme_digital": "Hippocratisme digital",
    "frequence_cardiaque": "Fréquence cardiaque (bpm)",
    "choc_de_pointe": "Choc de pointe",
    "rythme": "Rythme",
    "thrill": "Thrill (frémissement)",
    "chaleur_extremites": "Chaleur des extrémités",
    "trc_secondes": "TRC (secondes)",
    "pouls_peripheriques": "Pouls périphériques",
    "pouls_femoraux": "Pouls fémoraux",
    "matite_cardiaque": "Matité cardiaque",
    "bdc": "BDC (Bruits du Cœur)",
    "souffle_cardiaque": "Souffle cardiaque",
    "intensite_souffle_levine": "Intensité souffle (Levine)",
    "localisation_souffle": "Localisation souffle",
    "bruits_surajoutes": "Bruits surajoutés",
    "dedoublement": "Dédoublement",
    "volume_abdominal": "Volume abdominal",
    "voussures": "Voussures",
    "circulation_collaterale": "Circulation collatérale",
    "ombilic": "Ombilic",
    "souplesse_abdominale": "Souplesse abdominale",
    "douleur": "Douleur",
    "localisation_douleur": "Localisation douleur",
    "signe_de_murphy": "Signe de Murphy",
    "point_de_mcburney": "Point de McBurney",
    "hepatomegalie": "Hépatomégalie",
    "taille_hepatomegalie_cm": "Taille hépatomégalie (cm)",
    "splenomegalie": "Splénomégalie",
    "taille_splenomegalie_cm": "Taille splénomégalie (cm)",
    "masse_palpable": "Masse palpable",
    "localisation_masse": "Localisation masse",
    "globe_vesical": "Globe vésical",
    "pli_cutane": "Pli cutané",
    "sonorite_abdominale": "Sonorité abdominale",
    "matite_hepatique": "Matité hépatique",
    "matite_declive": "Matité déclive",
    "bruits_hydro_aeriques": "Bruits hydro-aériques",
    "souffle_vasculaire": "Souffle vasculaire",
    "selles": "Selles",
    "vomissements": "Vomissements",
    "emission_meconium": "Émission de méconium",
    "autres_precisions": "Autres précisions",
    "etat_de_conscience": "État de conscience",
    "score_glasgow": "Score de Glasgow (3-15)",
    "score_blantyre": "Score de Blantyre (0-5)",
    "mouvements_anormaux": "Mouvements anormaux",
    "attitude_posture": "Attitude / Posture",
    "pupilles": "Pupilles",
    "fontanelle": "Fontanelle",
    "permeabilite_sutures": "Perméabilité sutures",
    "raideur_nuque": "Raideur de nuque",
    "signe_kernig_bragard": "Signe de Kernig/Bragard",
    "ton_musculaire": "Ton musculaire",
    "force_musculaire": "Force musculaire",
    "sensibilite": "Sensibilité",
    "reflexes_osteo_tendineux": "Réflexes ostéo-tendineux",
    "babinski": "Signe de Babinski",
    "reflexes_archaiques": "Réflexes archaïques",
    "pc_cm": "PC (cm)",
    "dysmorphie_faciale": "Dysmorphie faciale",
    "type_dysmorphie": "Type dysmorphie",
    "yeux": "Yeux",
    "nez": "Nez",
    "oreilles": "Oreilles",
    "levres": "Lèvres",
    "muqueuse_buccale": "Muqueuse buccale",
    "langue": "Langue",
    "amygdales": "Amygdales",
    "fente_bec_lievre": "Fente / Bec de lièvre",
    "frein_langue": "Frein de langue",
    "cou_mobilite": "Cou - Mobilité",
    "adenopathies_cervicales": "Adénopathies cervicales",
    "hematome_scm": "Hématome SCM",
    "ganglions_cervicaux": "Ganglions cervicaux",
    "masse_cervicale": "Masse cervicale",
    "thyroide": "Thyroïde",
    "coloration": "Coloration",
    "hydratation": "Hydratation",
    "turgor_cutane": "Turgor cutané",
    "eruption_exantheme": "Éruption / Exanthème",
    "desquamation": "Desquamation",
    "purpura": "Purpura",
    "petechies": "Pétéchies",
    "syndrome_hemorragique": "Syndrome hémorragique",
    "temperature_cutanee": "Température cutanée",
    "texture": "Texture",
    "petite_levre_clitoris": "Petite lèvre et clitoris",
    "grande_levre": "Grande lèvre",
    "orifices_verifies": "Orifices vérifiés",
    "secretion_vaginale_metrorragie": "Sécrétion vaginale / métrorragie",
    "scrotum": "Scrotum",
    "presence_testicules": "Présence testicules",
    "mar": "Absence MAR",
    "hydrocele_vaginale": "Hydrocèle vaginale",
    "ms": "MS (lésions, doigts, pli palmaire)",
    "mi": "MI (orteils, malposition)",
    "rachis": "Rachis (malformations)",
    "hanche_lch": "Hanche (Recherche LCH)",
    "signes_generaux": "Signes généraux",
    "signes_fonctionnels": "Signes fonctionnels",
    "etat_yeux": "État des yeux",
    "etat_muqueuses": "État des muqueuses",
    "pli_cutane_rehydratation": "Pli cutané",
    "urine": "Urine",
    "selles_rehydratation": "Selles",
    "vomissements_rehydratation": "Vomissements",
    "temperature_c": "Température (°C)",
    "frequence_respiratoire_suivi": "Fréquence respiratoire (cpm)",
    "frequence_cardiaque_suivi": "Fréquence cardiaque (bpm)",
    "remarque": "Remarque",
}

CATEGORY_LABELS = {
    "inspection": "▸ Inspection",
    "palpation": "▸ Palpation",
    "percussion": "▸ Percussion",
    "auscultation": "▸ Auscultation",
    "emission": "▸ Émission",
    "reflexes": "▸ Réflexes",
    "fille": "Chez la fille",
    "garcon": "Chez le garçon",
}


def humanize_key(key):
    key = _strip_key(key)
    if key in KEY_LABELS:
        return KEY_LABELS[key]
    return key.replace("_", " ").capitalize()


# ============================================================
# FORMATAGE DES EXAMENS PAR APPAREIL
# ============================================================

def format_exam_data(data):
    """Formate les données JSON d'un examen par appareil en lignes lisibles."""
    lines = []

    if not isinstance(data, dict):
        return lines

    for raw_category, fields in _iter_dict_items(data):
        category = raw_category.lower()

        # Ignorer exceptions et conclusion (traités séparément)
        if category in ("exceptions", "conclusion"):
            continue

        if isinstance(fields, dict):
            category_lines = []
            for raw_key, value in _iter_dict_items(fields):
                key = raw_key.lower()
                display_value = display_choice(key, value)
                if display_value:
                    label = humanize_key(key)
                    category_lines.append(f"{label} : {display_value}")

            if category_lines:
                cat_label = CATEGORY_LABELS.get(category, category.capitalize())
                lines.append(cat_label)
                lines.extend(category_lines)
        else:
            display_value = display_choice(category, fields)
            if display_value:
                label = humanize_key(category)
                lines.append(f"{label} : {display_value}")

    # Exceptions et conclusion
    exceptions_val = _get_value(data, "exceptions")
    if exceptions_val and str(exceptions_val).strip():
        lines.append(f"Autres précisions : {str(exceptions_val).strip()}")

    conclusion_val = _get_value(data, "conclusion")
    if conclusion_val and str(conclusion_val).strip():
        lines.append(f"Conclusion : {str(conclusion_val).strip()}")

    return lines


# ============================================================
# FORMATAGE DES SÉROLOGIES
# ============================================================

def format_serologies(serologies):
    """Formate les sérologies en texte lisible."""
    if not isinstance(serologies, dict):
        return ""

    labels = {
        "bw": "BW",
        "vih": "VIH",
        "toxoplasmose": "Toxoplasmose",
        "rubeole": "Rubéole",
        "hb": "HB",
    }

    items = []
    for key, label in labels.items():
        entry = _get_value(serologies, key)
        if not isinstance(entry, dict):
            continue

        fait = _get_value(entry, "fait")
        resultat = _get_value(entry, "resultat")

        if is_empty(fait) and is_empty(resultat):
            continue

        resultat_display = ""
        if resultat:
            res_str = str(resultat).strip().lower()
            if res_str == "positif":
                resultat_display = "+"
            elif res_str == "negatif":
                resultat_display = "-"

        if resultat_display:
            items.append(f"{label} : {resultat_display}")
        elif fait:
            items.append(f"{label} : fait")

    return ", ".join(items)


# ============================================================
# CONSTRUCTION DES SECTIONS DU DOCUMENT
# ============================================================

def build_etat_civil_lines(observation):
    lines = []
    add_line(lines, "Nom", observation.nom)
    add_line(lines, "Prénom(s)", observation.prenoms)
    add_line(lines, "Date de naissance", format_date(observation.date_naissance))
    add_line(lines, "Âge", observation.age_display)
    add_line(lines, "Sexe", observation.get_sexe_display())
    add_line(lines, "Adresse", observation.adresse)
    add_line(lines, "N° Tél", observation.telephone)
    add_line(lines, "Lit N°", observation.lit)
    add_line(lines, "N° Dossier", observation.lit)
    return lines


def build_admission_lines(observation):
    lines = []
    add_line(lines, "Date d'entrée / admission", format_date(observation.date_admission))
    add_line(lines, "Motif d'entrée / admission", observation.motif_admission)
    return lines


def build_familiaux_lines(observation):
    af = get_related(observation, "antecedents_familiaux")
    lines = []
    if not af:
        return lines
    add_line(lines, "Rang dans la fratrie", af.rang_fratrie)
    add_line(lines, "État de santé ascendants", af.etat_sante_ascendants)
    add_line(lines, "État de santé collatéraux", af.etat_sante_collateraux)
    add_line(lines, "Tares familiales", display_choice("tares_familiales", af.tares_familiales))
    return lines


def build_grossesse_lines(observation):
    g = get_related(observation, "grossesse")
    lines = []
    if not g:
        return lines
    add_line(lines, "Âge de la mère", g.age_mere)
    add_line(lines, "G P A", g.gpa)
    add_line(lines, "Début CPN", g.debut_cpn)
    add_line(lines, "Rythme CPN", g.rythme_cpn)
    add_line(lines, "Nombre CPN", g.nombre_cpn)
    add_line(lines, "Lieu CPN", g.lieu_cpn)
    add_line(lines, "Nombre VAT fait", g.nombre_vat)
    add_line(lines, "Sérologies", format_serologies(g.serologies))
    add_line(lines, "Nombre de l'échographies", g.nombre_echographies)
    add_line(lines, "Résultat de l'échographie", g.resultat_echographie)
    add_line(lines, "Pathologies de grossesse", display_choice("pathologies_grossesse", g.pathologies_grossesse))

    # Détails leucorrhées si cochées
    pathologies = g.pathologies_grossesse if isinstance(g.pathologies_grossesse, list) else []
    pathologies_stripped = [str(p).strip() for p in pathologies]
    if any("leucorrhees" in p for p in pathologies_stripped):
        add_line(lines, "Leucorrhées - Couleur", g.leucorrhees_couleur)
        add_line(lines, "Leucorrhées - Odeur", g.leucorrhees_odeur)
        add_line(lines, "Leucorrhées - Abondance", g.leucorrhees_abondance)
        add_line(lines, "Leucorrhées traitées ?", yn(g.leucorrhees_traitees))

    add_line(lines, "Prise médicaments (FAF)", g.prise_medicaments)
    add_line(lines, "Prise toxique", g.prise_toxiques)

    if g.conclusion:
        conclusion_display = display_choice("conclusion_grossesse", g.conclusion)
        add_line(lines, "Conclusion grossesse", conclusion_display)

    return lines


def build_accouchement_lines(observation):
    a = get_related(observation, "accouchement")
    lines = []
    if not a:
        return lines
    add_line(lines, "Lieu", a.lieu)
    add_line(lines, "DDR", format_date(a.ddr))
    add_line(lines, "DPA", format_date(a.dpa))
    add_line(lines, "Présentation", display_choice("presentation", a.presentation))
    add_line(lines, "Durée du travail (min)", a.duree_travail_minutes)
    add_line(lines, "Durée de poussée (min)", a.duree_poussee_minutes)
    add_line(lines, "Terme", display_choice("terme", a.terme))
    add_line(lines, "Voie", display_choice("voie", a.voie))
    add_line(lines, "Manœuvre obstétricale", display_choice("manoeuvre_obstetricale", a.manoeuvre_obstetricale))
    add_line(lines, "Cri immédiat ?", yn(a.cri_immediat))
    add_line(lines, "Indice d'Apgar", a.indice_apgar)
    add_line(lines, "Asphyxié ?", yn(a.asphyxie))
    add_line(lines, "Réanimation ?", yn(a.reanimation))
    add_line(lines, "Durée réanimation (min)", a.duree_reanimation_minutes)
    add_line(lines, "Couleur liquide amniotique", display_choice("liquide_amniotique_couleur", a.liquide_amniotique_couleur))
    add_line(lines, "Abondance liquide amniotique", display_choice("liquide_amniotique_abondance", a.liquide_amniotique_abondance))
    add_line(lines, "Poids naissance (g)", format_number(a.poids_naissance_kg))
    add_line(lines, "Type poids naissance", display_choice("poids_naissance_type", a.poids_naissance_type))
    add_line(lines, "Type d'accouchement", display_choice("type_accouchement", a.type_accouchement))
    add_line(lines, "Adaptation néonatale", display_choice("adaptation_neonatale", a.adaptation_neonatale))
    add_line(lines, "Conclusion", a.conclusion)
    return lines


def build_alimentation_lines(observation):
    al = get_related(observation, "alimentation")
    lines = []
    if not al:
        return lines
    add_line(lines, "Type d'alimentation", display_choice("type_alimentation", al.type_alimentation))
    add_line(lines, "AME jusqu'à (mois)", al.ame_jusqua_mois)
    add_line(lines, "Diversification à partir de (mois)", al.diversification_mois)
    add_line(lines, "Détails diversification", al.diversification_aliments)
    add_line(lines, "Sevrage à", al.sevrage)
    add_line(lines, "Alimentation actuelle", al.alimentation_actuelle)
    add_line(lines, "Régime", display_choice("regime", al.regime))
    return lines


def build_vaccination_lines(observation):
    v = get_related(observation, "vaccination")
    lines = []
    if not v:
        return lines
    add_line(lines, "Vaccins reçus", display_choice("vaccins_recus", v.vaccins_recus))
    add_line(lines, "Vaccination correcte ?", yn(v.vaccination_correcte))
    add_line(lines, "Nom (carnet)", v.nom_carnet)
    add_line(lines, "Détails vaccination", v.details_vaccination)
    return lines


def build_dpm_lines(observation):
    dpm = get_related(observation, "developpement_psychomoteur")
    lines = []
    if not dpm:
        return lines
    add_line(lines, "Langage", dpm.langage)
    add_line(lines, "Motricité", dpm.motricite)
    add_line(lines, "Préhension", dpm.prehension)
    add_line(lines, "Relationnelle", dpm.relationnelle)
    add_line(lines, "Conclusion DPM", display_choice("dpm_conclusion", dpm.conclusion))
    return lines


def build_atcd_personnels_lines(observation):
    atcd = get_related(observation, "antecedents_personnels")
    lines = []
    if not atcd:
        return lines
    add_line(lines, "Hospitalisation antérieure", atcd.hospitalisation_anterieure)
    add_line(lines, "ATCD médicaux en rapport avec le ME", atcd.atcd_medicaux)
    add_line(lines, "ATCD chirurgicaux", atcd.atcd_chirurgicaux)
    return lines


def build_contexte_lines(observation):
    ctx = get_related(observation, "contexte_epidemiologique")
    lines = []
    if not ctx:
        return lines
    add_line(lines, "Contexte dyspnée", display_choice("dyspnee_contexte", ctx.dyspnee_contexte))
    add_line(lines, "Contexte diarrhée", display_choice("diarrhee_contexte", ctx.diarrhee_contexte))
    add_line(lines, "Crise convulsive parents bas âge ?", yn(ctx.convulsion_parents_bas_age))
    add_line(lines, "Hyperthermique ?", yn(ctx.convulsion_hyperthermique))
    return lines


def build_fiche_sociale_lines(observation):
    fs = get_related(observation, "fiche_sociale")
    lines = []
    if not fs:
        return lines
    add_line(lines, "Profession père", fs.profession_pere)
    add_line(lines, "Profession mère", fs.profession_mere)
    add_line(lines, "Type maison", fs.type_maison)
    add_line(lines, "Nombre de chambres", fs.nombre_chambres)
    add_line(lines, "Nombre personnes y vivant", fs.nombre_personnes)
    add_line(lines, "Éclairage", display_choice("eclairage", fs.eclairage))
    add_line(lines, "Eau", display_choice("eau", fs.eau))
    add_line(lines, "Combustible", display_choice("combustible", fs.combustible))
    add_line(lines, "WC", display_choice("wc", fs.wc))
    add_line(lines, "Conclusion Sociale", display_choice("niveau_social", fs.niveau_social))
    return lines


def build_examen_lines(observation):
    ec = get_related(observation, "examen_clinique")
    if not ec:
        return [], []

    biometrie_lines = []
    add_line(biometrie_lines, "Date de l'examen", format_date(ec.date_examen))
    add_line(biometrie_lines, "PC (cm)", format_number(ec.pc_cm))
    add_line(biometrie_lines, "PT (cm)", format_number(ec.pt_cm))
    add_line(biometrie_lines, "PB droit (mm)", format_number(ec.pbd_mm))
    add_line(biometrie_lines, "PB gauche (mm)", format_number(ec.pbg_mm))
    add_line(biometrie_lines, "PB (mm)", format_number(ec.pb_mm))
    add_line(biometrie_lines, "Poids P (kg)", format_number(ec.poids_kg))
    add_line(biometrie_lines, "Taille T (cm)", format_number(ec.taille_cm))
    add_line(biometrie_lines, "P/T", format_number(ec.p_t))
    add_line(biometrie_lines, "T/A", format_number(ec.t_a))
    add_line(biometrie_lines, "P/A", format_number(ec.p_a))
    add_line(biometrie_lines, "Nombre de dents", ec.nombre_dents)
    add_line(biometrie_lines, "Conclusion Biométrie", display_choice("biometrie_conclusion", ec.conclusion_biometrie))

    signes_generaux_lines = []
    add_line(signes_generaux_lines, "Présence des signes 3A2S", display_choice("signes_3a2s", ec.signes_3a2s))
    add_line(signes_generaux_lines, "Autres précisions / Détails", ec.signes_generaux_precision)

    signes_fonctionnels_lines = []
    add_line(signes_fonctionnels_lines, "Signes fonctionnels", ec.signes_fonctionnels)

    return biometrie_lines, signes_generaux_lines, signes_fonctionnels_lines


def build_examens_appareils_blocks(observation):
    """Construit les blocs pour chaque appareil de l'examen clinique."""
    ec = get_related(observation, "examen_clinique")
    blocks = []
    if not ec:
        return blocks

    appareils = [
        ("pleuropulmonaire", "Appareil Pleuropulmonaire"),
        ("cardiovasculaire", "Appareil Cardiovasculaire"),
        ("digestif", "Appareil Digestif"),
        ("neurologique", "Appareil Neurologique"),
        ("orl", "Sphère ORL (Tête et Cou)"),
        ("cutaneomuqueux", "Revêtement Cutanéomuqueux"),
        ("genitaux", "Appareils Génitaux"),
        ("osteoarticulaire", "Appareil Ostéo-Articulaire"),
    ]

    for appareil_key, appareil_title in appareils:
        data = getattr(ec, appareil_key, None)
        lines = format_exam_data(data)
        if lines:
            blocks.append({
                "title": appareil_title,
                "lines": lines,
            })

    return blocks


def build_mise_en_equation_lines(observation):
    """
    Construit la section MISE EN ÉQUATION :
    résumé narratif des antécédents, de l'examen physique
    et des hypothèses diagnostiques.
    """
    lines = []

    # ----------------------------------------------------------
    # 1. PHRASE D'INTRODUCTION
    # ----------------------------------------------------------
    nom_complet = f"{observation.nom} {observation.prenoms}".strip()
    sexe_display = observation.get_sexe_display()
    age = observation.age_display
    date_entree = format_date(observation.date_admission)
    motif = clean_text(observation.motif_admission)

    intro = f"• Il s'agit de {nom_complet}, âgé de {age}, de sexe {sexe_display}"
    if date_entree:
        intro += f", entré le {date_entree}"
    if motif:
        intro += f" pour {motif}"
    intro += "."
    lines.append(intro)

    # ----------------------------------------------------------
    # 2. ANTÉCÉDENTS (résumé)
    # ----------------------------------------------------------

    # Antécédents familiaux
    af = get_related(observation, "antecedents_familiaux")
    tares = ""
    if af:
        tares = display_choice("tares_familiales", af.tares_familiales)
    lines.append(f"  o Antécédents familiaux : {tares if tares else 'Non renseigné.'}")

    # Antécédents personnels
    atcd = get_related(observation, "antecedents_personnels")
    atcd_parts = []

    if atcd:
        if atcd.hospitalisation_anterieure:
            atcd_parts.append(f"hospitalisation antérieure : {atcd.hospitalisation_anterieure}")
        if atcd.atcd_medicaux:
            atcd_parts.append(f"ATCD médicaux : {atcd.atcd_medicaux}")
        if atcd.atcd_chirurgicaux:
            atcd_parts.append(f"ATCD chirurgicaux : {atcd.atcd_chirurgicaux}")

    # Vaccination
    v = get_related(observation, "vaccination")
    if v:
        vaccins = v.vaccins_recus if isinstance(v.vaccins_recus, list) else []
        nb_vaccins = len([x for x in vaccins if x])
        if nb_vaccins > 0:
            atcd_parts.append(f"vacciné ({nb_vaccins} vaccins)")
        elif v.vaccination_correcte:
            atcd_parts.append("vaccination correcte")

    if atcd_parts:
        lines.append(f"  o Antécédents personnels : {'; '.join(atcd_parts)}.")

    # DPM
    dpm = get_related(observation, "developpement_psychomoteur")
    if dpm and dpm.conclusion:
        dpm_display = display_choice("dpm_conclusion", dpm.conclusion)
        lines.append(f"  o Développement psychomoteur : {dpm_display}.")

    # Alimentation
    al = get_related(observation, "alimentation")
    if al:
        alim_parts = []
        if al.ame_jusqua_mois:
            alim_parts.append(f"AME jusqu'à {al.ame_jusqua_mois} mois")
        if al.regime:
            regime_display = display_choice("regime", al.regime)
            alim_parts.append(f"régime {regime_display.lower()}")
        if al.alimentation_actuelle:
            alim_parts.append(f"actuellement : {al.alimentation_actuelle}")
        if alim_parts:
            lines.append(f"  o Alimentation : {', '.join(alim_parts)}.")

    # Niveau socio-économique
    fs = get_related(observation, "fiche_sociale")
    if fs and fs.niveau_social:
        niveau_display = display_choice("niveau_social", fs.niveau_social)
        lines.append(f"  o Niveau socio-économique : {niveau_display}.")

    # ----------------------------------------------------------
    # 3. EXAMEN PHYSIQUE (résumé)
    # ----------------------------------------------------------
    ec = get_related(observation, "examen_clinique")
    if ec:
        lines.append("")
        lines.append("• L'examen physique a objectivé :")

        # Signes généraux
        signes_3a2s = display_choice("signes_3a2s", ec.signes_3a2s)
        if signes_3a2s:
            lines.append(f"  o Sur le plan général : {signes_3a2s}")

        # Signes fonctionnels
        if ec.signes_fonctionnels and str(ec.signes_fonctionnels).strip():
            lines.append(f"  o Sur le plan fonctionnel : {str(ec.signes_fonctionnels).strip()}")

        # Appareils : utiliser la conclusion de chaque appareil
        appareils = [
            ("pleuropulmonaire", "appareil pleuropulmonaire"),
            ("cardiovasculaire", "appareil cardiovasculaire"),
            ("digestif", "appareil digestif"),
            ("neurologique", "système nerveux"),
            ("orl", "sphère ORL"),
            ("cutaneomuqueux", "revêtement cutanéomuqueux"),
            ("genitaux", "appareils génitaux"),
            ("osteoarticulaire", "appareil ostéo-articulaire"),
        ]

        appareils_avec_conclusion = []
        appareils_sans_conclusion = []

        for appareil_key, appareil_label in appareils:
            data = getattr(ec, appareil_key, None)
            conclusion = None

            if isinstance(data, dict):
                conclusion = _get_value(data, "conclusion")

            if conclusion and str(conclusion).strip():
                appareils_avec_conclusion.append(
                    f"  o Sur le plan {appareil_label} : {str(conclusion).strip()}"
                )
            else:
                appareils_sans_conclusion.append(appareil_label)

        lines.extend(appareils_avec_conclusion)

        if appareils_sans_conclusion:
            if len(appareils_sans_conclusion) == len(appareils):
                lines.append("  o Tous les appareils : examens normaux")
            else:
                lines.append("  o Les autres appareils : examens normaux")

    # ----------------------------------------------------------
    # 4. HYPOTHÈSES DIAGNOSTIQUES
    # ----------------------------------------------------------
    hypotheses = observation.hypotheses_diagnostiques.all()
    if hypotheses:
        lines.append("")
        lines.append("• Posant un problème de diagnostic étiologique de :")
        for i, hypo in enumerate(hypotheses, 1):
            if hypo.diagnostic_propose and str(hypo.diagnostic_propose).strip():
                lines.append(f"  {i}. {str(hypo.diagnostic_propose).strip()}")

    return lines


def build_discussion_blocks(observation):
    """
    Construit les blocs de discussion diagnostique sous forme de texte structuré.
    """
    hypotheses = observation.hypotheses_diagnostiques.all()
    blocks = []

    if hypotheses:
        lines = []
        for i, hypo in enumerate(hypotheses, 1):
            lines.append(f"Diagnostic {i}:")
            lines.append(f"  • Hypothèse : {clean_text(hypo.diagnostic_propose) or '-'}")
            lines.append(f"  • Arguments pour : {clean_text(hypo.arguments_pour) or '-'}")
            lines.append(f"  • Arguments contre : {clean_text(hypo.arguments_contre) or '-'}")
            lines.append(f"  • Paraclinique : {clean_text(hypo.paraclinique) or '-'}")
            lines.append("")  # Empty line between hypotheses
        
        blocks.append({
            "title": "Discussion diagnostique",
            "lines": lines,
        })

    if observation.diagnostic_retenu:
        blocks.append({
            "title": "Diagnostic retenu",
            "lines": [observation.diagnostic_retenu],
        })

    if not blocks:
        blocks.append({
            "title": "",
            "lines": ["Discussion diagnostique non renseignée."],
        })

    return blocks


def build_traitement_lines(observation):
    t = get_related(observation, "traitement")
    lines = []
    if not t:
        return lines
    add_line(lines, "But", t.but)
    add_line(lines, "1) Traitement symptomatique", t.symptomatique)
    add_line(lines, "2) Traitement étiologique", t.etiologique)
    return lines


def build_surveillance_lines(observation):
    t = get_related(observation, "traitement")
    lines = []
    if t and t.surveillance:
        lines.append(t.surveillance)

    evolutions = observation.evolutions.all()
    for evo in evolutions:
        evo_line = ""
        if evo.date:
            evo_line += f"[{format_date(evo.date)}] "
        if evo.description:
            evo_line += evo.description
        if evo.statut:
            statut_display = dict(C.EVOLUTION_STATUT_CHOICES).get(evo.statut, evo.statut)
            evo_line += f" ({statut_display})"
        if evo_line.strip():
            lines.append(evo_line)

    return lines


# ============================================================
# CONSTRUCTION DU CONTEXTE COMPLET
# ============================================================

def build_observation_context(observation):
    is_enfant = str(observation.type_observation).strip().upper() == "ENFANT"

    if is_enfant:
        title = "OBSERVATION MÉDICALE D'UN NOURRISSON ET D'UN ENFANT"
    else:
        title = "OBSERVATION MÉDICALE D'UN NOUVEAU-NÉ"

    sections = []

    # I. ÉTAT CIVIL
    sections.append({
        "title": "I. ÉTAT CIVIL",
        "blocks": [{
            "title": "",
            "lines": build_etat_civil_lines(observation) or ["Non renseigné."],
        }],
    })

    # II. DATE ET MOTIF
    if is_enfant:
        admission_title = "II. DATE ET MOTIF D'ADMISSION"
    else:
        admission_title = "II. DATE ET MOTIF D'ENTRÉE"

    sections.append({
        "title": admission_title,
        "blocks": [{
            "title": "",
            "lines": build_admission_lines(observation) or ["Non renseigné."],
        }],
    })

    # III et IV selon le type
    if is_enfant:
        # III. HISTOIRE DE LA MALADIE
        episodes = observation.episodes_histoire_maladie.all()
        episode_blocks = []
        for ep in episodes:
            lines = []
            add_line(lines, "Date de début", format_date(ep.date_debut))
            add_line(lines, "Signes", ep.signes)
            add_line(lines, "Contexte", ep.contexte)
            add_line(lines, "Signes associés", ep.signes_associes)
            add_line(lines, "Traitement reçu", ep.traitement_recu)
            add_line(lines, "Évolution", display_choice("evolution_episode", ep.evolution))
            if lines:
                episode_blocks.append({
                    "title": f"Épisode {ep.ordre}",
                    "lines": lines,
                })

        sections.append({
            "title": "III. HISTOIRE DE LA MALADIE",
            "blocks": episode_blocks or [{"title": "", "lines": ["Non renseignée."]}],
        })

        # IV. ANTÉCÉDENTS
        antcd_blocks = []
        antcd_blocks.append({
            "title": "1) Familiaux",
            "lines": build_familiaux_lines(observation) or ["Non renseignés."],
        })
        antcd_blocks.append({
            "title": "2) Personnels - A. Gynéco-obstétrique - Déroulement de la grossesse",
            "lines": build_grossesse_lines(observation) or ["Non renseignée."],
        })
        antcd_blocks.append({
            "title": "Déroulement de l'accouchement",
            "lines": build_accouchement_lines(observation) or ["Non renseigné."],
        })
        antcd_blocks.append({
            "title": "B. Alimentation",
            "lines": build_alimentation_lines(observation) or ["Non renseignée."],
        })
        antcd_blocks.append({
            "title": "C. Développement psychomoteur",
            "lines": build_dpm_lines(observation) or ["Non renseigné."],
        })
        antcd_blocks.append({
            "title": "D. Vaccination",
            "lines": build_vaccination_lines(observation) or ["Non renseignée."],
        })
        antcd_blocks.append({
            "title": "E. Médicaux / F. Chirurgicaux",
            "lines": build_atcd_personnels_lines(observation) or ["Non renseignés."],
        })
        antcd_blocks.append({
            "title": "G. Contexte épidémiologique",
            "lines": build_contexte_lines(observation) or ["Non renseigné."],
        })
        antcd_blocks.append({
            "title": "H. Fiche sociale",
            "lines": build_fiche_sociale_lines(observation) or ["Non renseignée."],
        })

        sections.append({
            "title": "IV. ANTÉCÉDENTS",
            "blocks": antcd_blocks,
        })

    else:
        # III. ANTÉCÉDENTS
        antcd_blocks = []
        antcd_blocks.append({
            "title": "1) Familiaux",
            "lines": build_familiaux_lines(observation) or ["Non renseignés."],
        })
        antcd_blocks.append({
            "title": "2) Personnels - a- Gynéco-obstétrique - Déroulement de la grossesse",
            "lines": build_grossesse_lines(observation) or ["Non renseignée."],
        })
        antcd_blocks.append({
            "title": "Déroulement de l'accouchement",
            "lines": build_accouchement_lines(observation) or ["Non renseigné."],
        })
        antcd_blocks.append({
            "title": "b- Alimentation",
            "lines": build_alimentation_lines(observation) or ["Non renseignée."],
        })
        antcd_blocks.append({
            "title": "c- Vaccination",
            "lines": build_vaccination_lines(observation) or ["Non renseignée."],
        })
        antcd_blocks.append({
            "title": "d- Contexte épidémiologique",
            "lines": build_contexte_lines(observation) or ["Non renseigné."],
        })
        antcd_blocks.append({
            "title": "e- Fiche sociale",
            "lines": build_fiche_sociale_lines(observation) or ["Non renseignée."],
        })

        sections.append({
            "title": "III. ANTÉCÉDENTS",
            "blocks": antcd_blocks,
        })

        # IV. HISTOIRE DE LA MALADIE
        episodes = observation.episodes_histoire_maladie.all()
        episode_blocks = []
        for ep in episodes:
            lines = []
            add_line(lines, "Date de début", format_date(ep.date_debut))
            add_line(lines, "Signes", ep.signes)
            add_line(lines, "Contexte", ep.contexte)
            add_line(lines, "Signes associés", ep.signes_associes)
            add_line(lines, "Traitement reçu", ep.traitement_recu)
            add_line(lines, "Évolution", display_choice("evolution_episode", ep.evolution))
            if lines:
                episode_blocks.append({
                    "title": f"Épisode {ep.ordre}",
                    "lines": lines,
                })

        sections.append({
            "title": "IV. HISTOIRE DE LA MALADIE",
            "blocks": episode_blocks or [{"title": "", "lines": ["Non renseignée."]}],
        })

    # V. EXAMEN CLINIQUE
    examen_result = build_examen_lines(observation)
    if len(examen_result) == 3:
        biometrie_lines, signes_generaux_lines, signes_fonctionnels_lines = examen_result
    else:
        biometrie_lines, signes_generaux_lines = [], []
        signes_fonctionnels_lines = []

    examen_blocks = []
    examen_blocks.append({
        "title": "1) Biométrie à l'entrée",
        "lines": biometrie_lines or ["Non renseignée."],
    })
    examen_blocks.append({
        "title": "2) Signes Généraux (3A2S)",
        "lines": signes_generaux_lines or ["Non renseignés."],
    })
    examen_blocks.append({
        "title": "3) Signes Fonctionnels",
        "lines": signes_fonctionnels_lines or ["Non renseignés."],
    })

    # Examens par appareil
    appareils_blocks = build_examens_appareils_blocks(observation)
    examen_blocks.extend(appareils_blocks)

    sections.append({
        "title": "V. EXAMEN CLINIQUE",
        "blocks": examen_blocks,
    })

    # MISE EN ÉQUATION
    mise_en_equation = build_mise_en_equation_lines(observation)
    if mise_en_equation:
        sections.append({
            "title": "VI. MISE EN ÉQUATION",
            "blocks": [{
                "title": "",
                "lines": mise_en_equation,
            }],
        })

    # VI. DISCUSSION DIAGNOSTIQUE
    sections.append({
        "title": "VII. DISCUSSION DIAGNOSTIQUE",
        "blocks": build_discussion_blocks(observation) or [{"title": "", "lines": ["Non renseignée."]}],
    })

    # VII. TRAITEMENT PROPOSÉ
    sections.append({
        "title": "VIII. TRAITEMENT PROPOSÉ",
        "blocks": [{
            "title": "",
            "lines": build_traitement_lines(observation) or ["Non renseigné."],
        }],
    })

    # VIII. SURVEILLANCE
    sections.append({
        "title": "IX. SURVEILLANCE",
        "blocks": [{
            "title": "",
            "lines": build_surveillance_lines(observation) or ["Non renseignée."],
        }],
    })

    return {
        "title": title,
        "sections": sections,
    }


# ============================================================
# GÉNÉRATION DU FICHIER DOCX
# ============================================================

def generate_observation_docx(observation):
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Template DOCX introuvable : {TEMPLATE_PATH}. "
            "Lance la commande : python manage.py create_docx_template"
        )

    context = build_observation_context(observation)

    template = DocxTemplate(str(TEMPLATE_PATH))
    template.render(context)

    # ✅ SUPPRIMER LES PARAGRAPHES VIDES APRÈS LE RENDU
    remove_empty_paragraphs(template.docx)

    buffer = BytesIO()
    template.save(buffer)
    buffer.seek(0)

    patient_name = slugify(observation.nom or "patient")
    filename = f"observation-{observation.pk}-{patient_name}.docx"

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response
