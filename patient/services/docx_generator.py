# patient/services/docx_generator.py
from io import BytesIO
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils.text import slugify

from docxtpl import DocxTemplate

from .. import constants as C


# ============================================================
# HELPERS GÉNÉRAUX
# ============================================================

def get_related(observation, related_name):
    """
    Récupère un objet OneToOne lié sans lever d'exception s'il n'existe pas.
    """
    if not observation:
        return None

    try:
        return getattr(observation, related_name)
    except ObjectDoesNotExist:
        return None


def is_empty(value):
    """
    Permet de savoir si une valeur est vide.
    """
    if value is None:
        return True

    if isinstance(value, str) and not value.strip():
        return True

    if isinstance(value, (list, tuple, set)) and not value:
        return True

    if isinstance(value, dict):
        return all(is_empty(v) for v in value.values())

    return False


def clean_text(value):
    if value is None:
        return ""

    return str(value).strip()


def format_date(value):
    if not value:
        return ""

    try:
        return value.strftime("%d/%m/%Y")
    except Exception:
        return str(value)


def format_decimal(value):
    if value is None:
        return ""

    try:
        text = format(value, "f")
    except Exception:
        return str(value)

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text


def format_duration(minutes):
    if minutes is None or minutes == "":
        return ""

    try:
        total_minutes = int(minutes)
    except Exception:
        return str(minutes)

    if total_minutes < 60:
        return f"{total_minutes} min"

    hours, remaining_minutes = divmod(total_minutes, 60)

    if remaining_minutes:
        return f"{hours} h {remaining_minutes:02d}"

    return f"{hours} h"


def add_line(lines, label, value):
    """
    Ajoute une ligne si la valeur n'est pas vide.
    """
    value = clean_text(value)

    if not value:
        return

    lines.append(f"{label} : {value}")


def add_bool_line(lines, label, value):
    """
    Ajoute une ligne Oui / Non si la valeur est définie.
    """
    if value is None:
        return

    if isinstance(value, str):
        value = value.lower() in ("true", "oui", "1", "yes")

    lines.append(f"{label} : {'Oui' if value else 'Non'}")


def model_display(obj, field_name):
    """
    Récupère la valeur d'un champ ModelForm/ModelChoiceField avec son label.
    """
    if not obj:
        return ""

    value = getattr(obj, field_name, None)

    if is_empty(value):
        return ""

    display_method = getattr(obj, f"get_{field_name}_display", None)

    if callable(display_method):
        return display_method()

    return str(value)


def choice_map(attr_name, fallback=None):
    """
    Transforme un tuple de choices Django en dictionnaire value -> label.
    """
    choices = getattr(C, attr_name, fallback if fallback is not None else [])
    return dict(choices)


def labels_from_choices(values, choices_dict):
    """
    Convertit une liste de codes en liste de labels lisibles.
    """
    if not values:
        return []

    choices_dict = choices_dict or {}
    labels = []

    for value in values:
        if is_empty(value):
            continue

        labels.append(str(choices_dict.get(value, value)))

    return labels


def add_list_line(lines, label, values, choices_dict):
    """
    Ajoute une ligne pour une liste de choix multiples.
    """
    labels = labels_from_choices(values, choices_dict)

    if not labels:
        return

    lines.append(f"{label} : {', '.join(labels)}")


# ============================================================
# MAPPING DES CHOIX POUR LES JSONFIELDS
# ============================================================

FIELD_CHOICE_MAP = {
    # Pleuropulmonaire
    "type_respiration": choice_map("TYPE_RESPIRATION_CHOICES"),
    "amplitude_thoracique": choice_map("AMPLITUDE_THORACIQUE_CHOICES"),
    "symetrie_thoracique": choice_map("SYMETRIE_THORACIQUE_CHOICES"),
    "signes_de_lutte": choice_map("SIGNES_LUTTE_CHOICES"),
    "turgescence_jugulaire": choice_map("ABSENTE_PRESENTE_CHOICES"),
    "deformation_thoracique": choice_map("DEFORMATION_THORACIQUE_CHOICES"),
    "vibrations_vocales": choice_map("VIBRATIONS_VOCALES_CHOICES"),
    "expansion_thoracique": choice_map("EXPANSION_THORACIQUE_CHOICES"),
    "douleur_palpation": choice_map("ABSENTE_PRESENTE_CHOICES"),
    "crepitations_sous_cutanees": choice_map(
        "ABSENTES_PRESENTES_CHOICES",
        [
            ("absentes", "Absentes"),
            ("presentes", "Présentes"),
        ],
    ),
    "sonorite_globale": choice_map("SONORITE_PULMONAIRE_CHOICES"),
    "localisation_anormale": choice_map("LOCALISATION_PULMONAIRE_CHOICES"),
    "mobilite_bord_inferieur_poumon": choice_map("MOBILITE_BORD_INFERIEUR_POUMON_CHOICES"),
    "murmure_vesiculaire": choice_map("MURMURE_VESICULAIRE_CHOICES"),
    "rales_crepitants": choice_map("RALES_CREPITANTS_CHOICES"),
    "rales_sous_crepitants": choice_map("RALES_SOUS_CREPITANTS_CHOICES"),
    "sibilances": choice_map("SIBILANCES_CHOICES"),
    "rales_ronflants": choice_map("RALES_RONFLANTS_CHOICES"),
    "souffle_tubaire": choice_map("SOUFFLE_TUBAIRE_CHOICES"),
    "frottement_pleural": choice_map("FROTTEMENT_PLEURAL_CHOICES"),
    "localisation_anomalies": choice_map("LOCALISATION_PULMONAIRE_CHOICES"),

    # Cardiovasculaire
    "cyanose": choice_map("CYANOSE_CHOICES"),
    "paleur": choice_map("PALEUR_CHOICES"),
    "ictere": choice_map("ABSENT_PRESENT_CHOICES"),
    "oedemes": choice_map("OEDEMES_CHOICES"),
    "hippocratisme_digital": choice_map("HIPPOCRATISME_DIGITAL_CHOICES"),
    "choc_de_pointe": choice_map("CHOC_DE_POINTE_CHOICES"),
    "rythme": choice_map("RYTHME_CARDIAQUE_CHOICES"),
    "thrill": choice_map("ABSENT_PRESENT_CHOICES"),
    "chaleur_extremites": choice_map("CHALEUR_EXTREMITES_CHOICES"),
    "pouls_peripheriques": choice_map("POULS_PERIPHERIQUES_CHOICES"),
    "pouls_femoraux": choice_map("POULS_FEMORAUX_CHOICES"),
    "matite_cardiaque": choice_map("MATITE_CARDIAQUE_CHOICES"),
    "bdc": choice_map("BDC_CHOICES"),
    "souffle_cardiaque": choice_map("SOUFFLE_CARDIAQUE_CHOICES"),
    "intensite_souffle_levine": choice_map("LEVINE_CHOICES"),
    "localisation_souffle": choice_map("LOCALISATION_SOUFFLE_CHOICES"),
    "bruits_surajoutes": choice_map("BRUITS_SURAJOUTES_CHOICES"),
    "dedoublement": choice_map("DEDOUBLEMENT_CHOICES"),

    # Digestif
    "volume_abdominal": choice_map("VOLUME_ABDOMINAL_CHOICES"),
    "voussures": choice_map("VOUSSURES_CHOICES"),
    "circulation_collaterale": choice_map("CIRCULATION_COLLATERALE_CHOICES"),
    "ombilic": choice_map("OMBILIC_CHOICES"),
    "souplesse_abdominale": choice_map("SOUPLESSE_ABDOMINALE_CHOICES"),
    "douleur": choice_map("DOULEUR_ABDOMINALE_CHOICES"),
    "signe_de_murphy": choice_map("SIGNE_MURPHY_CHOICES"),
    "point_de_mcburney": choice_map("POINT_MCBURNEY_CHOICES"),
    "hepatomegalie": choice_map("HEPATOMEGALIE_CHOICES"),
    "splenomegalie": choice_map("SPLENOMEGALIE_CHOICES"),
    "masse_palpable": choice_map("MASSE_PALPABLE_CHOICES"),
    "globe_vesical": choice_map("GLOBE_VESICAL_CHOICES"),
    "pli_cutane": choice_map("PLI_CUTANE_CHOICES"),
    "sonorite_abdominale": choice_map("SONORITE_ABDOMINALE_CHOICES"),
    "matite_hepatique": choice_map("MATITE_HEPATIQUE_CHOICES"),
    "matite_declive": choice_map("MATITE_DECLIVE_CHOICES"),
    "bruits_hydro_aeriques": choice_map("BRUITS_HYDRO_AERIQUES_CHOICES"),
    "souffle_vasculaire": choice_map("SOUFFLE_VASCULAIRE_CHOICES"),
    "selles": choice_map("SELLES_CHOICES"),
    "vomissements": choice_map("VOMISSEMENTS_CHOICES"),
    "emission_meconium": choice_map("MECONIUM_CHOICES"),

    # Neurologique
    "etat_de_conscience": choice_map("ETAT_CONSCIENCE_CHOICES"),
    "mouvements_anormaux": choice_map("MOUVEMENTS_ANORMAUX_CHOICES"),
    "attitude_posture": choice_map("ATTITUDE_POSTURE_CHOICES"),
    "pupilles": choice_map("PUPILLES_CHOICES"),
    "fontanelle": choice_map("FONTANELLE_CHOICES"),
    "raideur_nuque": choice_map("RAIDEUR_NUQUE_CHOICES"),
    "signe_kernig_bragard": choice_map("KERNIG_BRAGARD_CHOICES"),
    "ton_musculaire": choice_map("TON_MUSCULAIRE_CHOICES"),
    "force_musculaire": choice_map("FORCE_MUSCULAIRE_CHOICES"),
    "sensibilite": choice_map("SENSIBILITE_CHOICES"),
    "reflexes_osteo_tendineux": choice_map("REFLEXES_OSTEO_TENDINEUX_CHOICES"),
    "babinski": choice_map("BABINSKI_CHOICES"),
    "reflexes_archaiques": choice_map("REFLEXES_ARCHEAQUES_CHOICES"),

    # ORL
    "dysmorphie_faciale": choice_map("DYSMORPHIE_FACIALE_CHOICES"),
    "yeux": choice_map("YEUX_CHOICES"),
    "nez": choice_map("NEZ_CHOICES"),
    "oreilles": choice_map("OREILLES_CHOICES"),
    "levres": choice_map("LEVRES_CHOICES"),
    "muqueuse_buccale": choice_map("MUQUEUSE_BUCCALE_CHOICES"),
    "langue": choice_map("LANGUE_CHOICES"),
    "amygdales": choice_map(
        "AMYgDALES_CHOICES",
        [
            ("normales", "Normales"),
            ("hypertrophiees", "Hypertrophiées"),
            ("erythemateuses", "Érythémateuses"),
            ("enduites", "Enduites"),
        ],
    ),
    "fente_bec_lievre": choice_map("FENTE_CHOICES"),
    "frein_langue": choice_map("FREIN_LANGUE_CHOICES"),
    "cou_mobilite": choice_map("COU_MOBILITE_CHOICES"),
    "adenopathies_cervicales": choice_map("ADENOPATHIES_CERVICALES_CHOICES"),
    "hematome_scm": choice_map("HEMATOME_SCM_CHOICES"),
    "ganglions_cervicaux": choice_map("GANGLIONS_CERVICAUX_CHOICES"),
    "masse_cervicale": choice_map("MASSE_CERVICALE_CHOICES"),
    "thyroide": choice_map("THYROIDE_CHOICES"),

    # Cutanéomuqueux
    "coloration": choice_map("COLORATION_CUTANEE_CHOICES"),
    "hydratation": choice_map("HYDRATATION_CHOICES"),
    "turgor_cutane": choice_map("TURGOR_CUTANE_CHOICES"),
    "eruption_exantheme": choice_map("ERUPTION_CHOICES"),
    "desquamation": choice_map("DESQUAMATION_CHOICES"),
    "purpura": choice_map("PURPURA_CHOICES"),
    "petechies": choice_map("PETECHIES_CHOICES"),
    "syndrome_hemorragique": choice_map("SYNDROME_HEMORRAGIQUE_CHOICES"),
    "temperature_cutanee": choice_map("TEMPERATURE_CUTANEE_CHOICES"),
    "texture": choice_map("TEXTURE_CUTANEE_CHOICES"),

    # Ostéo-articulaire
    "hanche_lch": choice_map("HANCHE_LCH_CHOICES"),
}


KEY_LABEL_OVERRIDES = {
    "frequence_respiratoire": "Fréquence respiratoire (cpm)",
    "frequence_cardiaque": "Fréquence cardiaque (bpm)",
    "trc_secondes": "TRC (secondes)",
    "pc_cm": "PC (cm)",
    "taille_hepatomegalie_cm": "Taille hépatomégalie (cm)",
    "taille_splenomegalie_cm": "Taille splénomégalie (cm)",
    "signe_de_murphy": "Signe de Murphy",
    "point_de_mcburney": "Point de McBurney",
    "signe_kernig_bragard": "Signe de Kernig/Bragard",
    "score_glasgow": "Score de Glasgow (3-15)",
    "score_blantyre": "Score de Blantyre (0-5)",
    "fente_bec_lievre": "Fente / Bec de lièvre",
    "frein_langue": "Frein de langue",
    "hematome_scm": "Hématome SCM",
    "petite_levre_clitoris": "Petite lèvre et clitoris",
    "grande_levre": "Grande lèvre",
    "orifices_verifies": "Orifices vérifiés",
    "secretion_vaginale_metrorragie": "Sécrétion vaginale / métrorragie",
    "presence_testicules": "Présence testicules",
    "mar": "Absence MAR",
    "hydrocele_vaginale": "Hydrocèle vaginale",
    "hanche_lch": "Hanche (Recherche LCH)",
    "ms": "MS (lésions, doigts, pli palmaire)",
    "mi": "MI (orteils, malposition)",
    "rachis": "Rachis (malformations)",
}


def humanize_key(key):
    if key in KEY_LABEL_OVERRIDES:
        return KEY_LABEL_OVERRIDES[key]

    text = key.replace("_", " ")
    return text.capitalize()


def display_exam_value(key, value):
    """
    Convertit une valeur JSON d'examen en texte lisible.
    """
    if is_empty(value):
        return ""

    if isinstance(value, bool):
        return "Oui" if value else "Non"

    if isinstance(value, list):
        labels = []
        choice_dict = FIELD_CHOICE_MAP.get(key, {})

        for item in value:
            if is_empty(item):
                continue

            labels.append(str(choice_dict.get(item, item)))

        return ", ".join(labels)

    choice_dict = FIELD_CHOICE_MAP.get(key, {})

    if isinstance(value, (int, float)):
        return format_decimal(value)

    return str(choice_dict.get(value, value))


def format_exam_lines(appareil_key, data):
    """
    Transforme le JSON d'un appareil en lignes lisibles pour Word.
    """
    lines = []

    if not isinstance(data, dict):
        return lines

    category_labels = {
        "inspection": "Inspection",
        "palpation": "Palpation",
        "percussion": "Percussion",
        "auscultation": "Auscultation",
        "emission": "Émission",
        "reflexes": "Réflexes",
        "fille": "Chez la fille",
        "garcon": "Chez le garçon",
    }

    for category, fields in data.items():
        if category in ("exceptions", "conclusion"):
            continue

        # Cas des catégories imbriquées : inspection, palpation, etc.
        if isinstance(fields, dict):
            category_lines = []

            for key, value in fields.items():
                display_value = display_exam_value(key, value)

                if display_value:
                    category_lines.append(f"{humanize_key(key)} : {display_value}")

            if category_lines:
                lines.append(f"▸ {category_labels.get(category, category.capitalize())}")
                lines.extend(category_lines)

        # Cas des champs simples au premier niveau : ms, mi, rachis, etc.
        else:
            display_value = display_exam_value(category, fields)

            if display_value:
                lines.append(f"{humanize_key(category)} : {display_value}")

    if not is_empty(data.get("exceptions")):
        lines.append(f"Autres précisions : {data.get('exceptions')}")

    if not is_empty(data.get("conclusion")):
        lines.append(f"Conclusion : {data.get('conclusion')}")

    return lines


def format_serologies(serologies):
    """
    Formate les sérologies de grossesse.
    """
    if not serologies:
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
        entry = serologies.get(key) or {}

        fait = entry.get("fait")
        resultat = entry.get("resultat")

        if not fait and not resultat:
            continue

        resultat_display = ""

        if resultat == "positif":
            resultat_display = "+"
        elif resultat == "negatif":
            resultat_display = "-"

        if resultat_display:
            items.append(f"{label} : {resultat_display}")
        elif fait:
            items.append(f"{label} : fait")

    return ", ".join(items)


# ============================================================
# CONSTRUCTION DES LIGNES PAR SECTION
# ============================================================

def build_etat_civil_lines(observation):
    lines = []

    add_line(lines, "Nom", observation.nom)
    add_line(lines, "Prénom(s)", observation.prenoms)
    add_line(lines, "Date de naissance", format_date(observation.date_naissance))

    age_display = getattr(observation, "age_display", None)
    if not age_display:
        age_display = f"{observation.age_valeur} {observation.get_age_unite_display()}"

    add_line(lines, "Âge", age_display)
    add_line(lines, "Sexe", observation.get_sexe_display())
    add_line(lines, "Adresse", observation.adresse)
    add_line(lines, "N° Tél", observation.telephone)
    add_line(lines, "Lit N°", observation.lit)
    add_line(lines, "N° Dossier", observation.numero_dossier)

    return lines


def build_admission_lines(observation):
    lines = []

    add_line(lines, "Date d'entrée / admission", format_date(observation.date_admission))
    add_line(lines, "Motif d'entrée / admission", observation.motif_admission)

    return lines


def build_antecedents_familiaux_lines(observation):
    antecedents = get_related(observation, "antecedents_familiaux")
    lines = []

    if not antecedents:
        return lines

    add_line(lines, "Rang dans la fratrie", antecedents.rang_fratrie)
    add_line(lines, "État de santé des ascendants", antecedents.etat_sante_ascendants)
    add_line(lines, "État de santé des collatéraux", antecedents.etat_sante_collateraux)

    add_list_line(
        lines,
        "Tares familiales",
        antecedents.tares_familiales,
        choice_map("TARES_FAMILIALES_CHOICES"),
    )

    return lines


def build_grossesse_lines(observation):
    grossesse = get_related(observation, "grossesse")
    lines = []

    if not grossesse:
        return lines

    add_line(lines, "Âge de la mère", grossesse.age_mere)
    add_line(lines, "G P A", grossesse.gpa)

    add_line(lines, "Début CPN", grossesse.debut_cpn)
    add_line(lines, "Rythme CPN", grossesse.rythme_cpn)
    add_line(lines, "Nombre CPN", grossesse.nombre_cpn)
    add_line(lines, "Lieu CPN", grossesse.lieu_cpn)
    add_line(lines, "Nombre VAT fait", grossesse.nombre_vat)

    add_line(lines, "Sérologies", format_serologies(grossesse.serologies))

    add_line(lines, "Nombre d'échographies", grossesse.nombre_echographies)
    add_line(lines, "Résultat échographie", grossesse.resultat_echographie)

    add_list_line(
        lines,
        "Pathologies de la grossesse",
        grossesse.pathologies_grossesse,
        choice_map("PATHOLOGIES_GROSSESSE_CHOICES"),
    )

    pathologies = grossesse.pathologies_grossesse or []

    if "leucorrhees" in pathologies:
        add_line(lines, "Leucorrhées - Couleur", grossesse.leucorrhees_couleur)
        add_line(lines, "Leucorrhées - Odeur", grossesse.leucorrhees_odeur)
        add_line(lines, "Leucorrhées - Abondance", grossesse.leucorrhees_abondance)
        add_bool_line(lines, "Leucorrhées traitées ?", grossesse.leucorrhees_traitees)

    add_line(lines, "Prise médicaments", grossesse.prise_medicaments)
    add_line(lines, "Prise toxique", grossesse.prise_toxiques)
    add_line(lines, "Conclusion grossesse", model_display(grossesse, "conclusion"))

    return lines


def build_accouchement_lines(observation):
    accouchement = get_related(observation, "accouchement")
    lines = []

    if not accouchement:
        return lines

    add_line(lines, "Lieu", accouchement.lieu)
    add_line(lines, "DDR", format_date(accouchement.ddr))
    add_line(lines, "DPA", format_date(accouchement.dpa))
    add_line(lines, "Présentation", model_display(accouchement, "presentation"))
    add_line(lines, "Durée du travail", format_duration(accouchement.duree_travail_minutes))
    add_line(lines, "Durée de poussée", format_duration(accouchement.duree_poussee_minutes))
    add_line(lines, "Terme", model_display(accouchement, "terme"))
    add_line(lines, "Voie", model_display(accouchement, "voie"))

    add_list_line(
        lines,
        "Manœuvre obstétricale",
        accouchement.manoeuvre_obstetricale,
        choice_map("MANOEUVRE_OBSTETRICALE_CHOICES"),
    )

    add_bool_line(lines, "Cri immédiat ?", accouchement.cri_immediat)
    add_line(lines, "Indice d'Apgar", accouchement.indice_apgar)
    add_bool_line(lines, "Asphyxié ?", accouchement.asphyxie)
    add_bool_line(lines, "Réanimation ?", accouchement.reanimation)
    add_line(lines, "Durée réanimation", format_duration(accouchement.duree_reanimation_minutes))

    add_line(lines, "Couleur liquide amniotique", model_display(accouchement, "liquide_amniotique_couleur"))
    add_line(lines, "Abondance LA", model_display(accouchement, "liquide_amniotique_abondance"))

    add_line(lines, "Poids exact (kg)", format_decimal(accouchement.poids_naissance_kg))
    add_line(lines, "Poids naissance", model_display(accouchement, "poids_naissance_type"))

    add_line(lines, "Type d'accouchement", model_display(accouchement, "type_accouchement"))
    add_line(lines, "Adaptation néonatale", model_display(accouchement, "adaptation_neonatale"))
    add_line(lines, "Conclusion", accouchement.conclusion)

    return lines


def build_alimentation_lines(observation):
    alimentation = get_related(observation, "alimentation")
    lines = []

    if not alimentation:
        return lines

    add_list_line(
        lines,
        "Type d'alimentation",
        alimentation.type_alimentation,
        choice_map("ALIMENTATION_TYPE_CHOICES"),
    )

    add_line(lines, "AME jusqu'à (mois)", alimentation.ame_jusqua_mois)
    add_line(lines, "Diversification à partir de (mois)", alimentation.diversification_mois)
    add_line(lines, "Par / Aliments", alimentation.diversification_aliments)
    add_line(lines, "Sevrage à", alimentation.sevrage)
    add_line(lines, "Actuellement", alimentation.alimentation_actuelle)
    add_line(lines, "Régime", model_display(alimentation, "regime"))

    return lines


def build_vaccination_lines(observation):
    vaccination = get_related(observation, "vaccination")
    lines = []

    if not vaccination:
        return lines

    add_list_line(
        lines,
        "Vaccins reçus",
        vaccination.vaccins_recus,
        choice_map("VACCINS_CHOICES"),
    )

    add_bool_line(lines, "Vaccination correcte ?", vaccination.vaccination_correcte)
    add_line(lines, "Nom (Carnet)", vaccination.nom_carnet)
    add_line(lines, "Détails vaccination", vaccination.details_vaccination)

    return lines


def build_contexte_epidemiologique_lines(observation):
    contexte = get_related(observation, "contexte_epidemiologique")
    lines = []

    if not contexte:
        return lines

    add_list_line(
        lines,
        "Dyspnée",
        contexte.dyspnee_contexte,
        choice_map("CONTEXTE_DYSPNEE_CHOICES"),
    )

    add_list_line(
        lines,
        "Diarrhée",
        contexte.diarrhee_contexte,
        choice_map("CONTEXTE_DIARRHEE_CHOICES"),
    )

    add_bool_line(
        lines,
        "Crise convulsive chez les parents à bas âge",
        contexte.convulsion_parents_bas_age,
    )

    add_bool_line(
        lines,
        "Hyperthermique ?",
        contexte.convulsion_hyperthermique,
    )

    return lines


def build_fiche_sociale_lines(observation):
    fiche = get_related(observation, "fiche_sociale")
    lines = []

    if not fiche:
        return lines

    add_line(lines, "Profession du père", fiche.profession_pere)
    add_line(lines, "Profession de la mère", fiche.profession_mere)
    add_line(lines, "Type de maison", fiche.type_maison)
    add_line(lines, "Nombre de chambres", fiche.nombre_chambres)
    add_line(lines, "Nombre de personnes y vivant", fiche.nombre_personnes)

    add_list_line(lines, "Éclairage", fiche.eclairage, choice_map("ECLAIRAGE_CHOICES"))
    add_list_line(lines, "Eau", fiche.eau, choice_map("EAU_CHOICES"))
    add_list_line(lines, "Combustible", fiche.combustible, choice_map("COMBUSTIBLE_CHOICES"))

    add_line(lines, "WC", model_display(fiche, "wc"))
    add_line(lines, "Conclusion sociale", model_display(fiche, "niveau_social"))

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
    add_line(lines, "Conclusion DPM", model_display(dpm, "conclusion"))

    return lines


def build_antecedents_personnels_lines(observation):
    antecedents = get_related(observation, "antecedents_personnels")
    lines = []

    if not antecedents:
        return lines

    add_line(lines, "Hospitalisation antérieure", antecedents.hospitalisation_anterieure)
    add_line(lines, "ATCD médicaux en rapport avec le ME", antecedents.atcd_medicaux)
    add_line(lines, "ATCD chirurgicaux", antecedents.atcd_chirurgicaux)

    return lines


def build_episode_blocks(observation):
    episodes = observation.episodes_histoire_maladie.all()
    blocks = []

    if not episodes:
        return [
            {
                "title": "",
                "lines": ["Aucun épisode renseigné."],
            }
        ]

    for index, episode in enumerate(episodes, start=1):
        lines = []

        add_line(lines, "Date de début", format_date(episode.date_debut))
        add_line(lines, "Signes", episode.signes)
        add_line(lines, "Contexte", episode.contexte)
        add_line(lines, "Signes associés", episode.signes_associes)
        add_line(lines, "Traitement reçu", episode.traitement_recu)
        add_line(lines, "Évolution", model_display(episode, "evolution"))

        blocks.append(
            {
                "title": f"Épisode {episode.ordre or index}",
                "lines": lines,
            }
        )

    return blocks


def build_examen_blocks(observation):
    examen = get_related(observation, "examen_clinique")
    blocks = []

    if not examen:
        return [
            {
                "title": "",
                "lines": ["Examen clinique non renseigné."],
            }
        ]

    biometrie_lines = []

    add_line(biometrie_lines, "Date de l'examen", format_date(examen.date_examen))
    add_line(biometrie_lines, "PC (cm)", format_decimal(examen.pc_cm))
    add_line(biometrie_lines, "PT (cm)", format_decimal(examen.pt_cm))
    add_line(biometrie_lines, "PBd (cm)", format_decimal(examen.pbd_cm))
    add_line(biometrie_lines, "PBg (cm)", format_decimal(examen.pbg_cm))
    add_line(biometrie_lines, "PB (cm)", format_decimal(examen.pb_cm))
    add_line(biometrie_lines, "Poids (kg)", format_decimal(examen.poids_kg))
    add_line(biometrie_lines, "Taille (cm)", format_decimal(examen.taille_cm))
    add_line(biometrie_lines, "P/T", format_decimal(examen.p_t))
    add_line(biometrie_lines, "T/A", format_decimal(examen.t_a))
    add_line(biometrie_lines, "P/A", format_decimal(examen.p_a))
    add_line(biometrie_lines, "Nombre de dents", examen.nombre_dents)
    add_line(biometrie_lines, "Conclusion biométrie", model_display(examen, "conclusion_biometrie"))

    blocks.append(
        {
            "title": "1) Biométrie à l'entrée",
            "lines": biometrie_lines or ["Non renseignée."],
        }
    )

    signes_generaux_lines = []

    add_list_line(
        signes_generaux_lines,
        "Présence des signes 3A2S",
        examen.signes_3a2s,
        choice_map("SIGNES_3A2S_CHOICES"),
    )

    add_line(
        signes_generaux_lines,
        "Autres précisions / Détails",
        examen.signes_generaux_precision,
    )

    blocks.append(
        {
            "title": "2) Signes Généraux (3A2S)",
            "lines": signes_generaux_lines or ["Non renseignés."],
        }
    )

    signes_fonctionnels_lines = []

    add_line(
        signes_fonctionnels_lines,
        "Signes fonctionnels",
        examen.signes_fonctionnels,
    )

    blocks.append(
        {
            "title": "3) Signes Fonctionnels",
            "lines": signes_fonctionnels_lines or ["Non renseignés."],
        }
    )

    exam_sections = [
        ("pleuropulmonaire", "Appareil Pleuropulmonaire"),
        ("cardiovasculaire", "Appareil Cardiovasculaire"),
        ("digestif", "Appareil Digestif"),
        ("neurologique", "Appareil Neurologique"),
        ("orl", "Sphère ORL (Tête et Cou)"),
        ("cutaneomuqueux", "Revêtement Cutanéomuqueux"),
        ("genitaux", "Appareils Génitaux"),
        ("osteoarticulaire", "Appareil Ostéo-Articulaire"),
    ]

    for key, title in exam_sections:
        data = getattr(examen, key, None)
        lines = format_exam_lines(key, data)

        blocks.append(
            {
                "title": title,
                "lines": lines or ["Non renseigné."],
            }
        )

    return blocks


def build_discussion_blocks(observation):
    hypotheses = observation.hypotheses_diagnostiques.all()
    blocks = []

    if hypotheses:
        for index, hypo in enumerate(hypotheses, start=1):
            lines = []

            add_line(lines, "Diagnostic proposé", hypo.diagnostic_propose)
            add_line(lines, "Argument pour", hypo.arguments_pour)
            add_line(lines, "Argument contre", hypo.arguments_contre)
            add_line(lines, "Paraclinique", hypo.paraclinique)

            blocks.append(
                {
                    "title": f"Diagnostic {hypo.ordre or index}",
                    "lines": lines,
                }
            )

    if observation.diagnostic_retenu:
        blocks.append(
            {
                "title": "Diagnostic retenu",
                "lines": [observation.diagnostic_retenu],
            }
        )

    if not blocks:
        blocks.append(
            {
                "title": "",
                "lines": ["Discussion diagnostique non renseignée."],
            }
        )

    return blocks


def build_traitement_lines(observation):
    traitement = get_related(observation, "traitement")
    lines = []

    if not traitement:
        return ["Traitement non renseigné."]

    add_line(lines, "But", traitement.but)
    add_line(lines, "1) Traitement symptomatique", traitement.symptomatique)
    add_line(lines, "2) Traitement étiologique", traitement.etiologique)
    add_line(lines, "Notes", traitement.notes)

    return lines or ["Traitement non renseigné."]


def build_surveillance_blocks(observation):
    traitement = get_related(observation, "traitement")
    evolutions = observation.evolutions.all()

    blocks = []

    surveillance_lines = []

    if traitement and traitement.surveillance:
        surveillance_lines.append(traitement.surveillance)

    blocks.append(
        {
            "title": "Surveillance",
            "lines": surveillance_lines or ["Non renseignée."],
        }
    )

    for evolution in evolutions:
        lines = []

        add_line(lines, "Date", format_date(evolution.date))
        add_line(lines, "Description", evolution.description)
        add_line(lines, "Statut", model_display(evolution, "statut"))

        blocks.append(
            {
                "title": "Évolution",
                "lines": lines,
            }
        )

    return blocks


# ============================================================
# CONSTRUCTION DU CONTEXTE GLOBAL
# ============================================================

def build_observation_context(observation):
    is_enfant = observation.type_observation == "ENFANT"

    if is_enfant:
        main_title = "OBSERVATION MÉDICALE D'UN NOURRISSON ET D'UN ENFANT"
    else:
        main_title = "OBSERVATION MÉDICALE D'UN NOUVEAU-NÉ"

    etat_civil_lines = build_etat_civil_lines(observation)
    admission_lines = build_admission_lines(observation)

    antecedents_blocks = []

    antecedents_familiaux_lines = build_antecedents_familiaux_lines(observation)
    antecedents_blocks.append(
        {
            "title": "1) Familiaux",
            "lines": antecedents_familiaux_lines or ["Non renseignés."],
        }
    )

    antecedents_personnels_blocks = []

    grossesse_lines = build_grossesse_lines(observation)
    antecedents_personnels_blocks.append(
        {
            "title": "Déroulement de la grossesse",
            "lines": grossesse_lines or ["Non renseignée."],
        }
    )

    accouchement_lines = build_accouchement_lines(observation)
    antecedents_personnels_blocks.append(
        {
            "title": "Déroulement de l'accouchement",
            "lines": accouchement_lines or ["Non renseigné."],
        }
    )

    alimentation_lines = build_alimentation_lines(observation)
    antecedents_personnels_blocks.append(
        {
            "title": "Alimentation",
            "lines": alimentation_lines or ["Non renseignée."],
        }
    )

    if is_enfant:
        dpm_lines = build_dpm_lines(observation)
        antecedents_personnels_blocks.append(
            {
                "title": "Développement psychomoteur",
                "lines": dpm_lines or ["Non renseigné."],
            }
        )

    vaccination_lines = build_vaccination_lines(observation)
    antecedents_personnels_blocks.append(
        {
            "title": "Vaccination",
            "lines": vaccination_lines or ["Non renseignée."],
        }
    )

    if is_enfant:
        atcd_personnels_lines = build_antecedents_personnels_lines(observation)
        antecedents_personnels_blocks.append(
            {
                "title": "Antécédents médicaux et chirurgicaux",
                "lines": atcd_personnels_lines or ["Non renseignés."],
            }
        )

    contexte_lines = build_contexte_epidemiologique_lines(observation)
    antecedents_personnels_blocks.append(
        {
            "title": "Contexte épidémiologique",
            "lines": contexte_lines or ["Non renseigné."],
        }
    )

    fiche_sociale_lines = build_fiche_sociale_lines(observation)
    antecedents_personnels_blocks.append(
        {
            "title": "Fiche sociale",
            "lines": fiche_sociale_lines or ["Non renseignée."],
        }
    )

    antecedents_blocks.extend(antecedents_personnels_blocks)

    episode_blocks = build_episode_blocks(observation)
    examen_blocks = build_examen_blocks(observation)
    discussion_blocks = build_discussion_blocks(observation)
    traitement_lines = build_traitement_lines(observation)
    surveillance_blocks = build_surveillance_blocks(observation)

    sections = []

    sections.append(
        {
            "title": "I. ÉTAT CIVIL",
            "blocks": [
                {
                    "title": "",
                    "lines": etat_civil_lines or ["Non renseigné."],
                }
            ],
        }
    )

    if is_enfant:
        sections.append(
            {
                "title": "II. DATE ET MOTIF D'ADMISSION",
                "blocks": [
                    {
                        "title": "",
                        "lines": admission_lines or ["Non renseigné."],
                    }
                ],
            }
        )

        sections.append(
            {
                "title": "III. HISTOIRE DE LA MALADIE",
                "blocks": episode_blocks,
            }
        )

        sections.append(
            {
                "title": "IV. ANTÉCÉDENTS",
                "blocks": antecedents_blocks,
            }
        )

        sections.append(
            {
                "title": "V. EXAMEN CLINIQUE",
                "blocks": examen_blocks,
            }
        )

        sections.append(
            {
                "title": "VI. DISCUSSION DIAGNOSTIQUE",
                "blocks": discussion_blocks,
            }
        )

        sections.append(
            {
                "title": "VII. TRAITEMENT PROPOSÉ",
                "blocks": [
                    {
                        "title": "",
                        "lines": traitement_lines,
                    }
                ],
            }
        )

        sections.append(
            {
                "title": "VIII. SURVEILLANCE",
                "blocks": surveillance_blocks,
            }
        )

    else:
        sections.append(
            {
                "title": "II. DATE ET MOTIF D'ENTRÉE",
                "blocks": [
                    {
                        "title": "",
                        "lines": admission_lines or ["Non renseigné."],
                    }
                ],
            }
        )

        sections.append(
            {
                "title": "III. ANTÉCÉDENTS",
                "blocks": antecedents_blocks,
            }
        )

        sections.append(
            {
                "title": "IV. HISTOIRE DE LA MALADIE",
                "blocks": episode_blocks,
            }
        )

        sections.append(
            {
                "title": "V. EXAMEN CLINIQUE",
                "blocks": examen_blocks,
            }
        )

        sections.append(
            {
                "title": "VI. DISCUSSION DIAGNOSTIQUE",
                "blocks": discussion_blocks,
            }
        )

        sections.append(
            {
                "title": "VII. TRAITEMENT PROPOSÉ",
                "blocks": [
                    {
                        "title": "",
                        "lines": traitement_lines,
                    }
                ],
            }
        )

        sections.append(
            {
                "title": "VIII. SURVEILLANCE",
                "blocks": surveillance_blocks,
            }
        )

    return {
        "title": main_title,
        "sections": sections,
    }


# ============================================================
# GÉNÉRATION DE LA RÉPONSE HTTP DOCX
# ============================================================

def generate_observation_docx(observation):
    """
    Génère le fichier Word pour une observation donnée.
    """
    template_path = Path(__file__).resolve().parents[1] / "docx_templates" / "observation.docx"

    if not template_path.exists():
        raise FileNotFoundError(
            f"Template DOCX introuvable : {template_path}. "
            "Lance la commande : python manage.py create_docx_template"
        )

    context = build_observation_context(observation)

    template = DocxTemplate(str(template_path))
    template.render(context)

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