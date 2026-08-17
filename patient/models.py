# models.py
from copy import deepcopy

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from . import constants as C
from django.utils import timezone


# ============================================================
# DEFAULT CALLABLES POUR JSONFIELD
# ============================================================

def default_serologies():
    return deepcopy(C.DEFAULT_SEROLOGIES)


def default_pleuropulmonaire():
    return deepcopy(C.EXAMEN_DEFAULTS["pleuropulmonaire"])


def default_cardiovasculaire():
    return deepcopy(C.EXAMEN_DEFAULTS["cardiovasculaire"])


def default_digestif():
    return deepcopy(C.EXAMEN_DEFAULTS["digestif"])


def default_neurologique():
    return deepcopy(C.EXAMEN_DEFAULTS["neurologique"])


def default_orl():
    return deepcopy(C.EXAMEN_DEFAULTS["orl"])


def default_cutaneomuqueux():
    return deepcopy(C.EXAMEN_DEFAULTS["cutaneomuqueux"])


def default_genitaux():
    return deepcopy(C.EXAMEN_DEFAULTS["genitaux"])


def default_osteoarticulaire():
    return deepcopy(C.EXAMEN_DEFAULTS["osteoarticulaire"])


# ============================================================
# OBSERVATION PRINCIPALE
# ============================================================

class ObservationMedicale(models.Model):
    """
    Modèle principal.
    Contient l'état civil minimal requis et le type d'observation.
    Toutes les autres sections sont optionnelles et reliées par OneToOne ou FK.
    """

    # --- État civil de base (requis) ---
    type_observation = models.CharField(
        max_length=10,
        choices=C.TYPE_OBSERVATION_CHOICES,
        verbose_name="Type d'observation",
    )
    nom = models.CharField(
        max_length=255,
        verbose_name="Nom",
    )
    prenoms = models.CharField(
        max_length=255,
        verbose_name="Prénom(s)",
    )
    sexe = models.CharField(
        max_length=1,
        choices=C.SEXE_CHOICES,
        verbose_name="Sexe",
    )
    age_valeur = models.PositiveIntegerField(
        verbose_name="Âge",
    )
    age_unite = models.CharField(
        max_length=10,
        choices=C.AGE_UNITE_CHOICES,
        verbose_name="Unité d'âge",
    )

    # --- État civil / admission (optionnel) ---
    date_naissance = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance",
    )
    adresse = models.TextField(
        null=True,
        blank=True,
        verbose_name="Adresse",
    )
    telephone = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Contact",
    )
    lit = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="Lit n°",
    )
    numero_dossier = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="N° dossier",
    )
    date_admission = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'entrée / admission",
    )
    motif_admission = models.TextField(
        null=True,
        blank=True,
        verbose_name="Motif d'entrée / admission",
    )

    # --- Discussion diagnostique ---
    diagnostic_retenu = models.TextField(
        null=True,
        blank=True,
        verbose_name="Diagnostic retenu",
    )

    # --- Métadonnées ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Observation médicale"
        verbose_name_plural = "Observations médicales"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nom} {self.prenoms} ({self.get_type_observation_display()})"

    @property
    def age_display(self):
        return f"{self.age_valeur} {self.get_age_unite_display()}"


# ============================================================
# ANTÉCÉDENTS FAMILIAUX
# ============================================================

class AntecedentsFamiliaux(models.Model):
    observation = models.OneToOneField(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="antecedents_familiaux",
        verbose_name="Observation",
    )

    rang_fratrie = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Rang dans la fratrie",
    )
    etat_sante_ascendants = models.TextField(
        null=True,
        blank=True,
        verbose_name="État de santé des ascendants",
    )
    etat_sante_collateraux = models.TextField(
        null=True,
        blank=True,
        verbose_name="État de santé des collatéraux",
    )
    tares_familiales = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tares familiales",
        help_text="Liste de codes : hta, diabete, asthme, epilepsie, cardiopathie, nephropathie, autre",
    )

    class Meta:
        verbose_name = "Antécédents familiaux"
        verbose_name_plural = "Antécédents familiaux"

    def __str__(self):
        return f"Antécédents familiaux de {self.observation}"


# ============================================================
# ANTÉCÉDENTS PERSONNELS : GROSSESSE
# ============================================================

class Grossesse(models.Model):
    observation = models.OneToOneField(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="grossesse",
        verbose_name="Observation",
    )

    age_mere = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Âge de la mère",
    )
    gpa = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="G / P / A",
        help_text="Exemple : G2 P1 A0",
    )

    # CPN
    debut_cpn = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Début CPN",
    )
    rythme_cpn = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Rythme CPN",
    )
    nombre_cpn = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre de CPN",
    )
    lieu_cpn = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Lieu CPN",
    )
    nombre_vat = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre de VAT",
    )

    # Sérologies : structure JSON
    serologies = models.JSONField(
        default=default_serologies,
        blank=True,
        verbose_name="Sérologies",
        help_text="Structure : bw, vih, toxoplasmose, rubeole, hb avec fait/resultat",
    )

    # Échographies
    nombre_echographies = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre d'échographies",
    )
    resultat_echographie = models.TextField(
        null=True,
        blank=True,
        verbose_name="Résultat d'échographie",
    )

    # Pathologies de la grossesse
    pathologies_grossesse = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Pathologies de la grossesse",
        help_text="Liste de codes : leucorrhees, fievre_peripartum, dysurie, hta_gravidique, diabete_gestationnel, autre",
    )

    # Détails leucorrhées si cochée
    leucorrhees_couleur = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Leucorrhées - Couleur",
    )
    leucorrhees_odeur = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Leucorrhées - Odeur",
    )
    leucorrhees_abondance = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Leucorrhées - Abondance",
    )
    leucorrhees_traitees = models.BooleanField(
        null=True,
        blank=True,
        choices=C.OUI_NON_CHOICES,
        verbose_name="Leucorrhées traitées ?",
    )

    # Médicaments / toxiques
    prise_medicaments = models.TextField(
        null=True,
        blank=True,
        verbose_name="Prise de médicaments",
        help_text="Début-arrêt / FAF",
    )
    prise_toxiques = models.TextField(
        null=True,
        blank=True,
        verbose_name="Prise toxique",
        help_text="Décoction, alcool, tabac...",
    )

    conclusion = models.CharField(
        max_length=50,
        choices=C.CONCLUSION_GROSSESSE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Conclusion grossesse",
    )

    class Meta:
        verbose_name = "Grossesse"
        verbose_name_plural = "Grossesses"

    def __str__(self):
        return f"Grossesse de {self.observation}"


# ============================================================
# ANTÉCÉDENTS PERSONNELS : ACCOUCHEMENT
# ============================================================

class Accouchement(models.Model):
    observation = models.OneToOneField(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="accouchement",
        verbose_name="Observation",
    )

    lieu = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Lieu d'accouchement",
    )
    ddr = models.DateField(
        null=True,
        blank=True,
        verbose_name="DDR",
    )
    dpa = models.DateField(
        null=True,
        blank=True,
        verbose_name="DPA",
    )
    presentation = models.CharField(
        max_length=30,
        choices=C.PRESENTATION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Présentation",
    )

    duree_travail_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Durée du travail (minutes)",
    )
    duree_poussee_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Durée de poussée (minutes)",
    )

    terme = models.CharField(
        max_length=20,
        choices=C.TERME_CHOICES,
        null=True,
        blank=True,
        verbose_name="Terme",
    )
    voie = models.CharField(
        max_length=20,
        choices=C.VOIE_ACCOUCHEMENT_CHOICES,
        null=True,
        blank=True,
        verbose_name="Voie d'accouchement",
    )
    manoeuvre_obstetricale = models.JSONField(
        default=list,
        blank=True, null=True,
        verbose_name="Manœuvre obstétricale",
        help_text="Liste de codes : forceps, ventouse, extraction_manuelle, autre, aucune",
    )

    cri_immediat = models.BooleanField(
        null=True,
        blank=True,
        choices=C.OUI_NON_CHOICES,
        verbose_name="Cri immédiat ?",
    )
    indice_apgar = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Indice d'Apgar",
    )
    asphyxie = models.BooleanField(
        null=True,
        blank=True,
        choices=C.OUI_NON_CHOICES,
        verbose_name="Asphyxié ?",
    )
    reanimation = models.BooleanField(
        null=True,
        blank=True,
        choices=C.OUI_NON_CHOICES,
        verbose_name="Réanimation ?",
    )
    duree_reanimation_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Durée de réanimation (min)",
    )

    liquide_amniotique_couleur = models.CharField(
        max_length=30,
        choices=C.COULEUR_LIQUIDE_AMNIOTIQUE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Couleur du liquide amniotique",
    )
    liquide_amniotique_abondance = models.CharField(
        max_length=20,
        choices=C.ABONDANCE_LIQUIDE_AMNIOTIQUE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Abondance du liquide amniotique",
    )

    poids_naissance_kg = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Poids de naissance (kg)",
    )
    poids_naissance_type = models.CharField(
        max_length=20,
        choices=C.POIDS_NAISSANCE_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Type de poids de naissance",
    )

    type_accouchement = models.CharField(
        max_length=20,
        choices=C.TYPE_ACCOUCHEMENT_CHOICES,
        null=True,
        blank=True,
        verbose_name="Type d'accouchement",
    )
    adaptation_neonatale = models.CharField(
        max_length=20,
        choices=C.ADAPTATION_NEONATALE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Adaptation néonatale",
    )

    conclusion = models.TextField(
        null=True,
        blank=True,
        verbose_name="Conclusion accouchement",
    )

    class Meta:
        verbose_name = "Accouchement"
        verbose_name_plural = "Accouchements"

    def __str__(self):
        return f"Accouchement de {self.observation}"


# ============================================================
# ALIMENTATION
# ============================================================

class Alimentation(models.Model):
    observation = models.OneToOneField(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="alimentation",
        verbose_name="Observation",
    )

    type_alimentation = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Type d'alimentation",
        help_text="Liste de codes : ame, nursie, ranombary, autre",
    )
    ame_jusqua_mois = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="AME jusqu'à (mois)",
    )
    diversification_mois = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Diversification à partir de (mois)",
    )
    diversification_aliments = models.TextField(
        null=True,
        blank=True,
        verbose_name="Détails de la diversification",
    )
    sevrage = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Sevrage à",
    )
    alimentation_actuelle = models.TextField(
        null=True,
        blank=True,
        verbose_name="Alimentation actuelle",
    )
    regime = models.CharField(
        max_length=30,
        choices=C.REGIME_CHOICES,
        null=True,
        blank=True,
        verbose_name="Régime",
    )

    class Meta:
        verbose_name = "Alimentation"
        verbose_name_plural = "Alimentations"

    def __str__(self):
        return f"Alimentation de {self.observation}"


# ============================================================
# VACCINATION
# ============================================================

class Vaccination(models.Model):
    observation = models.OneToOneField(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="vaccination",
        verbose_name="Observation",
    )

    vaccins_recus = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Vaccins reçus",
        help_text="Liste de codes vaccins",
    )
    vaccination_correcte = models.BooleanField(
        null=True,
        blank=True,
        choices=C.OUI_NON_CHOICES,
        verbose_name="Vaccination correcte ?",
    )
    nom_carnet = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Nom (carnet)",
    )
    details_vaccination = models.TextField(
        null=True,
        blank=True,
        verbose_name="Détails vaccination",
    )

    class Meta:
        verbose_name = "Vaccination"
        verbose_name_plural = "Vaccinations"

    def __str__(self):
        return f"Vaccination de {self.observation}"


# ============================================================
# CONTEXTE ÉPIDÉMIOLOGIQUE
# ============================================================

class ContexteEpidemiologique(models.Model):
    observation = models.OneToOneField(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="contexte_epidemiologique",
        verbose_name="Observation",
    )

    dyspnee_contexte = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Contexte dyspnée",
        help_text="Liste : virose, tb, cas_similaire, allergie, tabagisme_passif, autre",
    )
    diarrhee_contexte = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Contexte diarrhée",
        help_text="Liste : cas_similaire, aliments_suspects, zep, autre",
    )
    convulsion_parents_bas_age = models.BooleanField(
        null=True,
        blank=True,
        choices=C.OUI_NON_CHOICES,
        verbose_name="Crise convulsive chez les parents à bas âge ?",
    )
    convulsion_hyperthermique = models.BooleanField(
        null=True,
        blank=True,
        choices=C.OUI_NON_CHOICES,
        verbose_name="Convulsion hyperthermique ?",
    )

    class Meta:
        verbose_name = "Contexte épidémiologique"
        verbose_name_plural = "Contextes épidémiologiques"

    def __str__(self):
        return f"Contexte épidémiologique de {self.observation}"


# ============================================================
# FICHE SOCIALE
# ============================================================

class FicheSociale(models.Model):
    observation = models.OneToOneField(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="fiche_sociale",
        verbose_name="Observation",
    )

    profession_pere = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Profession du père",
    )
    profession_mere = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Profession de la mère",
    )

    type_maison = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Type de maison",
    )
    nombre_chambres = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre de chambres",
    )
    nombre_personnes = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre de personnes y vivant",
    )

    eclairage = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Éclairage",
        help_text="Liste : bougie, petrole, electricite, autre",
    )
    eau = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Eau",
        help_text="Liste : jirama, riviere, fontaine, autre",
    )
    combustible = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Combustible",
        help_text="Liste : charbon, gaz, bois, resistance, autre",
    )
    wc = models.CharField(
        max_length=30,
        choices=C.WC_CHOICES,
        null=True,
        blank=True,
        verbose_name="WC",
    )

    niveau_social = models.CharField(
        max_length=20,
        choices=C.NIVEAU_SOCIAL_CHOICES,
        null=True,
        blank=True,
        verbose_name="Niveau social",
    )

    class Meta:
        verbose_name = "Fiche sociale"
        verbose_name_plural = "Fiches sociales"

    def __str__(self):
        return f"Fiche sociale de {self.observation}"


# ============================================================
# HISTOIRE DE LA MALADIE (ÉPISODES MULTIPLES)
# ============================================================

class EpisodeHistoireMaladie(models.Model):
    observation = models.ForeignKey(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="episodes_histoire_maladie",
        verbose_name="Observation",
    )

    ordre = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Ordre",
    )
    date_debut = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de début",
    )
    signes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Signes",
    )
    contexte = models.TextField(
        null=True,
        blank=True,
        verbose_name="Contexte",
    )
    signes_associes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Signes associés",
    )
    traitement_recu = models.TextField(
        null=True,
        blank=True,
        verbose_name="Traitement reçu",
    )
    evolution = models.CharField(
        max_length=20,
        choices=C.EVOLUTION_EPISODE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Évolution",
    )

    class Meta:
        verbose_name = "Épisode de l'histoire de la maladie"
        verbose_name_plural = "Épisodes de l'histoire de la maladie"
        ordering = ["ordre", "date_debut"]

    def __str__(self):
        return f"Épisode {self.ordre} de {self.observation}"


# ============================================================
# SPÉCIFIQUE ENFANT : DÉVELOPPEMENT PSYCHOMOTEUR
# ============================================================

class DeveloppementPsychomoteur(models.Model):
    observation = models.OneToOneField(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="developpement_psychomoteur",
        verbose_name="Observation",
    )

    langage = models.TextField(
        null=True,
        blank=True,
        verbose_name="Langage",
    )
    motricite = models.TextField(
        null=True,
        blank=True,
        verbose_name="Motricité",
    )
    prehension = models.TextField(
        null=True,
        blank=True,
        verbose_name="Préhension",
    )
    relationnelle = models.TextField(
        null=True,
        blank=True,
        verbose_name="Relationnelle",
    )
    conclusion = models.CharField(
        max_length=20,
        choices=C.DPM_CONCLUSION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Conclusion DPM",
    )

    class Meta:
        verbose_name = "Développement psychomoteur"
        verbose_name_plural = "Développements psychomoteurs"

    def __str__(self):
        return f"DPM de {self.observation}"


# ============================================================
# SPÉCIFIQUE ENFANT : ANTÉCÉDENTS MÉDICAUX / CHIRURGICAUX
# ============================================================

class AntecedentsPersonnels(models.Model):
    observation = models.OneToOneField(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="antecedents_personnels",
        verbose_name="Observation",
    )

    hospitalisation_anterieure = models.TextField(
        null=True,
        blank=True,
        verbose_name="Hospitalisation antérieure",
    )
    atcd_medicaux = models.TextField(
        null=True,
        blank=True,
        verbose_name="ATCD médicaux en rapport avec le ME",
    )
    atcd_chirurgicaux = models.TextField(
        null=True,
        blank=True,
        verbose_name="ATCD chirurgicaux",
    )

    class Meta:
        verbose_name = "Antécédents personnels"
        verbose_name_plural = "Antécédents personnels"

    def __str__(self):
        return f"Antécédents personnels de {self.observation}"


# ============================================================
# EXAMEN CLINIQUE
# ============================================================

class ExamenClinique(models.Model):
    observation = models.OneToOneField(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="examen_clinique",
        verbose_name="Observation",
    )

    date_examen = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de l'examen",
    )

    # --------------------------------------------------------
    # BIOMÉTRIE
    # --------------------------------------------------------
    pc_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="PC (cm)",
    )
    pt_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="PT (cm)",
    )
    pbd_mm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="PB droit (mm)",
    )
    pbg_mm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="PB gauche (mm)",
    )
    pb_mm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="PB (mm)",
    )
    poids_kg = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Poids (kg)",
    )
    taille_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Taille (cm)",
    )

    p_t = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="P/T (poids pour taille)",
    )
    t_a = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="T/A (taille pour âge)",
    )
    p_a = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="P/A (poids pour aâge)",
    )

    nombre_dents = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre de dents",
    )
    conclusion_biometrie = models.CharField(
        max_length=20,
        choices=C.BIOMETRIE_CONCLUSION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Conclusion biométrie",
    )

    # --------------------------------------------------------
    # SIGNES GÉNÉRAUX
    # --------------------------------------------------------
    signes_3a2s = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Signes 3A2S",
        help_text="Liste : asthenie, amaigrissement, anorexie, fievre, hypersudation",
    )
    signes_generaux_precision = models.TextField(
        null=True,
        blank=True,
        verbose_name="Autres précisions / Détails",
    )

    # --------------------------------------------------------
    # SIGNES FONCTIONNELS
    # --------------------------------------------------------
    signes_fonctionnels = models.TextField(
        null=True,
        blank=True,
        verbose_name="Signes fonctionnels",
    )

    # --------------------------------------------------------
    # EXAMENS PAR APPAREIL (JSON STRUCTURÉ)
    # --------------------------------------------------------
    pleuropulmonaire = models.JSONField(
        default=default_pleuropulmonaire,
        blank=True,
        verbose_name="Appareil pleuropulmonaire",
    )
    cardiovasculaire = models.JSONField(
        default=default_cardiovasculaire,
        blank=True,
        verbose_name="Appareil cardiovasculaire",
    )
    digestif = models.JSONField(
        default=default_digestif,
        blank=True,
        verbose_name="Appareil digestif",
    )
    neurologique = models.JSONField(
        default=default_neurologique,
        blank=True,
        verbose_name="Appareil neurologique",
    )
    orl = models.JSONField(
        default=default_orl,
        blank=True,
        verbose_name="Sphère ORL / Tête et cou",
    )
    cutaneomuqueux = models.JSONField(
        default=default_cutaneomuqueux,
        blank=True,
        verbose_name="Revêtement cutanéomuqueux",
    )
    genitaux = models.JSONField(
        default=default_genitaux,
        blank=True,
        verbose_name="Appareils génitaux",
    )
    osteoarticulaire = models.JSONField(
        default=default_osteoarticulaire,
        blank=True,
        verbose_name="Appareil ostéo-articulaire",
    )

    class Meta:
        verbose_name = "Examen clinique"
        verbose_name_plural = "Examens cliniques"

    def __str__(self):
        return f"Examen clinique de {self.observation}"


# ============================================================
# DISCUSSION DIAGNOSTIQUE
# ============================================================

class HypotheseDiagnostic(models.Model):
    observation = models.ForeignKey(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="hypotheses_diagnostiques",
        verbose_name="Observation",
    )

    ordre = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Ordre",
    )
    diagnostic_propose = models.TextField(
        null=True,
        blank=True,
        verbose_name="Diagnostic proposé",
    )
    arguments_pour = models.TextField(
        null=True,
        blank=True,
        verbose_name="Arguments pour",
    )
    arguments_contre = models.TextField(
        null=True,
        blank=True,
        verbose_name="Arguments contre",
    )
    paraclinique = models.TextField(
        null=True,
        blank=True,
        verbose_name="Paraclinique",
    )

    class Meta:
        verbose_name = "Hypothèse diagnostique"
        verbose_name_plural = "Hypothèses diagnostiques"
        ordering = ["ordre"]

    def __str__(self):
        return f"Hypothèse {self.ordre} de {self.observation}"


# ============================================================
# TRAITEMENT
# ============================================================

class Traitement(models.Model):
    observation = models.OneToOneField(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="traitement",
        verbose_name="Observation",
    )

    but = models.TextField(
        null=True,
        blank=True,
        verbose_name="But",
    )
    symptomatique = models.TextField(
        null=True,
        blank=True,
        verbose_name="Traitement symptomatique",
    )
    etiologique = models.TextField(
        null=True,
        blank=True,
        verbose_name="Traitement étiologique",
    )
    surveillance = models.TextField(
        null=True,
        blank=True,
        verbose_name="Surveillance",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notes",
    )

    class Meta:
        verbose_name = "Traitement"
        verbose_name_plural = "Traitements"

    def __str__(self):
        return f"Traitement de {self.observation}"


# ============================================================
# ÉVOLUTION (OPTIONNEL, POUR SUIVI ULTÉRIEUR)
# ============================================================

class Evolution(models.Model):
    observation = models.ForeignKey(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="evolutions",
        verbose_name="Observation",
    )

    date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date",
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Description",
    )
    statut = models.CharField(
        max_length=20,
        choices=C.EVOLUTION_STATUT_CHOICES,
        null=True,
        blank=True,
        verbose_name="Statut",
    )

    class Meta:
        verbose_name = "Évolution"
        verbose_name_plural = "Évolutions"
        ordering = ["-date"]

    def __str__(self):
        return f"Évolution de {self.observation} le {self.date}"


# ============================================================
# SUIVI HOSPITALISATION - EXAMEN PHYSIQUE RÉPÉTÉ
# ============================================================

class ExamenPhysique(models.Model):
    """
    Examen physique répété pendant l'hospitalisation.

    Une observation peut avoir plusieurs examens physiques,
    enregistrés à des dates/heures différentes.
    """

    observation = models.ForeignKey(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="examens_physiques",
        verbose_name="Observation",
    )

    date_heure = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Date et heure de l'examen",
    )

    examine_par = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Examiné par",
    )

    # --------------------------------------------------------
    # CONSTANTES RAPIDES
    # --------------------------------------------------------

    poids_kg = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Poids (kg)",
    )

    temperature_c = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Température (°C)",
    )

    frequence_respiratoire = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Fréquence respiratoire (cpm)",
    )

    frequence_cardiaque = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Fréquence cardiaque (bpm)",
    )

    tension_arterielle = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="Tension artérielle mmHg",
        help_text="Exemple : 100/60",
    )

    saturation_oxygene = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="SpO₂ (%)",
    )

    glycelie = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Glycémie capillaire (g/l)",
    )

    # --------------------------------------------------------
    # SIGNES CLINIQUES
    # --------------------------------------------------------

    signes_generaux = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Signes généraux",
        help_text="Liste de codes : asthenie, fievre, amaigrissement, anorexie, sueur profuse",
    )

    signes_fonctionnels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Signes fonctionnels",
        help_text="Liste de codes : dyspnee, toux, douleur, vomissements, diarrhee, etc.",
    )

    # --------------------------------------------------------
    # EXAMEN PAR APPAREIL
    # --------------------------------------------------------

    donnees_appareils = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Examen par appareil",
        help_text=(
            "Structure JSON prévue pour recevoir les examens par appareil : "
            "pleuropulmonaire, cardiovasculaire, digestif, neurologique, ORL, "
            "cutaneomuqueux, genitaux, osteoarticulaire."
        ),
    )

    # --------------------------------------------------------
    # TEXTES LIBRES UTILES
    # --------------------------------------------------------

    exceptions = models.TextField(
        null=True,
        blank=True,
        verbose_name="Exceptions / Imprévus",
    )

    conclusion = models.TextField(
        null=True,
        blank=True,
        verbose_name="Conclusion",
    )

    # --------------------------------------------------------
    # MÉTADONNÉES
    # --------------------------------------------------------

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Examen physique de suivi"
        verbose_name_plural = "Examens physiques de suivi"
        ordering = ["-date_heure"]
        indexes = [
            models.Index(fields=["observation", "-date_heure"]),
        ]

    def __str__(self):
        return f"Examen du {self.date_heure.strftime('%d/%m/%Y %H:%M')} - {self.observation}"


# ============================================================
# FICHE DE RÉHYDRATATION
# ============================================================

class FicheRehydratation(models.Model):
    """
    Fiche principale de réhydratation.

    Elle contient les paramètres initiaux et finaux :
    - heure de début
    - poids initial
    - quantité de liquide
    - durée
    - signes cliniques initiaux
    - poids final
    - gain de poids calculé automatiquement
    """

    observation = models.ForeignKey(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="fiches_rehydratation",
        verbose_name="Observation",
    )

    statut = models.CharField(
        max_length=20,
        choices=C.REHYDRATATION_STATUT_CHOICES,
        default="en_cours",
        verbose_name="Statut",
    )

    heure_debut = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Heure de début",
    )

    heure_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Heure de fin",
    )

    poids_initial_kg = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Poids initial (kg)",
    )

    poids_final_kg = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Poids final (kg)",
    )

    quantite_liquide_ml = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Quantité de liquide (mL)",
    )

    duree_heure = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Durée (heure)",
        help_text="Si vide, la durée peut être calculée entre heure de début et heure de fin.",
    )

    signes_generaux = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Signes généraux",
        help_text="Liste de codes : asthenie, fievre, lethargie, etc.",
    )

    signes_fonctionnels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Signes fonctionnels",
        help_text="Liste de codes : dyspnee, douleur, vomissements, diarrhee, oligurie, etc.",
    )

    etat_yeux = models.CharField(
        max_length=30,
        choices=C.ETAT_YEUX_CHOICES,
        null=True,
        blank=True,
        verbose_name="État des yeux",
    )

    etat_muqueuses = models.CharField(
        max_length=30,
        choices=C.ETAT_MUQUEUSES_CHOICES,
        null=True,
        blank=True,
        verbose_name="État des muqueuses",
    )

    pli_cutane = models.CharField(
        max_length=30,
        choices=C.PLI_CUTANE_REHYDRATATION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Pli cutané",
    )

    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notes",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fiche de réhydratation"
        verbose_name_plural = "Fiches de réhydratation"
        ordering = ["-heure_debut"]
        indexes = [
            models.Index(fields=["observation", "-heure_debut"]),
        ]

    def __str__(self):
        if self.heure_debut:
            return f"Réhydratation du {self.heure_debut.strftime('%d/%m/%Y %H:%M')} - {self.observation}"

        return f"Réhydratation - {self.observation}"

    @property
    def gain_poids_kg(self):
        if self.poids_initial_kg is None or self.poids_final_kg is None:
            return None

        return self.poids_final_kg - self.poids_initial_kg

    @property
    def gain_poids_display(self):
        gain = self.gain_poids_kg

        if gain is None:
            return ""

        text = format(gain, "f")

        if "." in text:
            text = text.rstrip("0").rstrip(".")

        return f"{text} kg"


    @property
    def duree_display(self):
        total_heure = self.duree_heure

        if total_heure is None:
            return "Durée non spécifiée"
        
        return f"{total_heure} h"


# ============================================================
# ÉVALUATION HORAIRE - RÉHYDRATATION
# ============================================================

class EvaluationHoraireRehydratation(models.Model):
    """
    Évaluation horaire liée à une fiche de réhydratation.

    Les paramètres horaires incluent maintenant :
    - signes généraux
    - signes fonctionnels
    - état des yeux
    - état des muqueuses
    - pli cutané
    - urine
    - selles
    - vomissements
    - température
    - fréquence respiratoire
    - fréquence cardiaque

    Les poids, quantité de liquide et poids final restent
    dans la fiche principale de réhydratation.
    """

    fiche_rehydratation = models.ForeignKey(
        FicheRehydratation,
        on_delete=models.CASCADE,
        related_name="evaluations_horaires",
        verbose_name="Fiche de réhydratation",
    )

    heure_evaluation = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Heure d'évaluation",
    )

    # --------------------------------------------------------
    # SIGNES CLINIQUES HORAIRES
    # --------------------------------------------------------

    signes_generaux = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Signes généraux",
        help_text="Liste de codes : asthenie, fievre, lethargie, etc.",
    )

    signes_fonctionnels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Signes fonctionnels",
        help_text="Liste de codes : dyspnee, douleur, vomissements, diarrhee, oligurie, anurie, etc.",
    )

    etat_yeux = models.CharField(
        max_length=30,
        choices=C.ETAT_YEUX_CHOICES,
        null=True,
        blank=True,
        verbose_name="État des yeux",
    )

    etat_muqueuses = models.CharField(
        max_length=30,
        choices=C.ETAT_MUQUEUSES_CHOICES,
        null=True,
        blank=True,
        verbose_name="État des muqueuses",
    )

    pli_cutane = models.CharField(
        max_length=30,
        choices=C.PLI_CUTANE_REHYDRATATION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Pli cutané",
    )

    # --------------------------------------------------------
    # ÉLIMINATION / PERTES
    # --------------------------------------------------------

    urine = models.CharField(
        max_length=10,
        choices=C.URINE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Urine",
    )

    selles = models.CharField(
        max_length=30,
        choices=C.SELLES_REHYDRATATION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Selles",
    )

    vomissements = models.CharField(
        max_length=30,
        choices=C.VOMISSEMENTS_REHYDRATATION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Vomissements",
    )

    # --------------------------------------------------------
    # CONSTANTES
    # --------------------------------------------------------

    temperature_c = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Température (°C)",
    )

    frequence_respiratoire = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Fréquence respiratoire (cpm)",
    )

    frequence_cardiaque = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Fréquence cardiaque (bpm)",
    )

    # --------------------------------------------------------
    # REMARQUE
    # --------------------------------------------------------

    remarque = models.TextField(
        null=True,
        blank=True,
        verbose_name="Remarque",
    )

    date_heure = models.DateTimeField(verbose_name="Date et heure", default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Évaluation horaire de réhydratation"
        verbose_name_plural = "Évaluations horaires de réhydratation"
        ordering = ["heure_evaluation"]
        indexes = [
            models.Index(fields=["fiche_rehydratation", "heure_evaluation"]),
        ]

    def __str__(self):
        return f"Évaluation horaire du {self.heure_evaluation.strftime('%d/%m/%Y %H:%M')}"


# ============================================================
# TRAITEMENTS AJUSTÉS ET TRACÉS
# ============================================================

class TraitementAjustement(models.Model):
    """
    Chaque ajustement de traitement est une nouvelle version.

    Les versions précédentes ne sont jamais modifiées.
    La dernière version est considérée comme la version actuelle.
    """

    observation = models.ForeignKey(
        ObservationMedicale,
        on_delete=models.CASCADE,
        related_name="traitements_ajustes",
        verbose_name="Observation",
    )

    version = models.PositiveIntegerField(
        default=1,
        editable=False,
        verbose_name="Ajustement N°",
    )

    date_heure = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Date et heure",
    )

    type_ajustement = models.CharField(
        max_length=30,
        choices=C.TRAITEMENT_AJUSTEMENT_TYPE_CHOICES,
        default="ajustement",
        verbose_name="Type d'ajustement",
    )

    motif = models.TextField(
        null=True,
        blank=True,
        verbose_name="Motif",
    )

    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notes",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ajustement de traitement"
        verbose_name_plural = "Ajustements de traitement"
        ordering = ["-version"]
        constraints = [
            models.UniqueConstraint(
                fields=["observation", "version"],
                name="unique_version_traitement_ajustement_par_observation",
            )
        ]

    def __str__(self):
        return f"Traitement v{self.version} - {self.observation}"

    def save(self, *args, **kwargs):
        """
        Attribue automatiquement un numéro de version croissant
        pour une même observation.
        """
        if not self.pk:
            dernier = (
                TraitementAjustement.objects.filter(observation=self.observation)
                .order_by("-version")
                .first()
            )

            if dernier:
                self.version = dernier.version + 1
            else:
                self.version = 1

        super().save(*args, **kwargs)

    @property
    def est_arret(self):
        return self.type_ajustement == "arret"

    @property
    def est_suspension(self):
        return self.type_ajustement == "suspension"

    @classmethod
    def dernier_pour_observation(cls, observation):
        return (
            cls.objects.filter(observation=observation)
            .order_by("-version")
            .first()
        )

# ============================================================
# LIGNES DE TRAITEMENT
# ============================================================

class LigneTraitement(models.Model):
    """
    Ligne de traitement appartenant à une version d'ajustement.

    Exemple :
    - Paracétamol
    - dose : 500 mg
    - voie : orale
    - fréquence : 3 fois/jour
    - durée : 5 jours
    """

    ajustement = models.ForeignKey(
        TraitementAjustement,
        on_delete=models.CASCADE,
        related_name="lignes",
        verbose_name="Ajustement",
    )

    type_ligne = models.CharField(
        max_length=20,
        choices=C.TYPE_LIGNE_TRAITEMENT_CHOICES,
        default="medicament",
        verbose_name="Type de ligne",
    )

    nom = models.CharField(
        max_length=255,
        verbose_name="Nom / Médicament / Soin",
    )

    dose = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Dose",
        help_text="Exemple : 500 mg, 10 mL, 1 g",
    )

    voie = models.CharField(
        max_length=30,
        choices=C.VOIE_TRAITEMENT_CHOICES,
        null=True,
        blank=True,
        verbose_name="Voie",
    )

    frequence = models.CharField(
        max_length=30,
        choices=C.FREQUENCE_TRAITEMENT_CHOICES,
        null=True,
        blank=True,
        verbose_name="Fréquence",
    )

    duree = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Durée",
        help_text="Exemple : 5 jours, 48 heures",
    )

    date_debut = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de début",
    )

    date_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de fin",
    )

    instructions = models.TextField(
        null=True,
        blank=True,
        verbose_name="Instructions",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ligne de traitement"
        verbose_name_plural = "Lignes de traitement"
        ordering = ["nom"]

    def __str__(self):
        return f"{self.nom} - {self.get_voie_display() if self.voie else ''}"



