# constants.py
# Référentiel central de tous les choix de l'application.
# Ce fichier est la source unique de vérité pour les choices,
# les listes à cocher, et les structures JSON par défaut.

# ============================================================
# OBSERVATION - BASE
# ============================================================

TYPE_OBSERVATION_CHOICES = [
    ("NN", "Nouveau-né"),
    ("ENFANT", "Nourrisson / Enfant"),
]

SEXE_CHOICES = [
    ("M", "Masculin"),
    ("F", "Féminin"),
]

AGE_UNITE_CHOICES = [
    ("jour", "Jour(s)"),
    ("mois", "Mois"),
    ("an", "An(s)"),
]

OUI_NON_CHOICES = [
    (True, "Oui"),
    (False, "Non"),
]

RESULTAT_SEROLOGIE_CHOICES = [
    ("positif", "Positif (+)"),
    ("negatif", "Négatif (-)"),
]

# ============================================================
# ANTÉCÉDENTS FAMILIAUX
# ============================================================

TARES_FAMILIALES_CHOICES = [
    ("hta", "HTA"),
    ("diabete", "Diabète"),
    ("asthme", "Asthme"),
    ("epilepsie", "Épilepsie"),
    ("cardiopathie", "Cardiopathie"),
    ("nephropathie", "Néphropathie"),
    ("autre", "Autre"),
]

# ============================================================
# GROSSESSE
# ============================================================

PATHOLOGIES_GROSSESSE_CHOICES = [
    ("leucorrhees", "Leucorrhées pathologiques"),
    ("fievre_peripartum", "Fièvre péri/post-partum"),
    ("dysurie", "Dysurie / Infection urinaire"),
    ("hta_gravidique", "HTA gravidique"),
    ("diabete_gestationnel", "Diabète gestationnel"),
    ("autre", "Autre"),
]

CONCLUSION_GROSSESSE_CHOICES = [
    ("bien_suivie", "Bien suivie"),
    ("bien_suivie_sans_infection", "Bien suivie sans anamnèse infectieuse"),
    ("bien_suivie_avec_infection", "Bien suivie avec anamnèse infectieuse"),
    ("mal_suivie", "Mal suivie"),
]

# ============================================================
# ACCOUCHEMENT
# ============================================================

PRESENTATION_CHOICES = [
    ("cephalique", "Céphalique"),
    ("siege", "Siège"),
    ("transverse", "Transverse"),
    ("autre", "Autre"),
]

TERME_CHOICES = [
    ("terme", "Terme"),
    ("premature", "Prématuré"),
    ("rclu", "RCIU"),
]

VOIE_ACCOUCHEMENT_CHOICES = [
    ("voie_basse", "Voie basse"),
    ("cesarienne", "Césarienne / OC"),
]

MANOEUVRE_OBSTETRICALE_CHOICES = [
    ("aucune", "Aucune"),
    ("forceps", "Forceps"),
    ("ventouse", "Ventouse"),
    ("extraction_manuelle", "Extraction manuelle"),
    ("autre", "Autre"),
]

COULEUR_LIQUIDE_AMNIOTIQUE_CHOICES = [
    ("clair", "Clair"),
    ("meconial", "Méconial"),
    ("pur_pois", "En purée de pois"),
    ("fetide", "Fétide"),
    ("sanguinolent", "Sanguinolent"),
    ("autre", "Autre"),
]

ABONDANCE_LIQUIDE_AMNIOTIQUE_CHOICES = [
    ("faible", "Faible"),
    ("normale", "Normale"),
    ("abondante", "Abondante"),
]

POIDS_NAISSANCE_TYPE_CHOICES = [
    ("eutrophique", "Eutrophique (2,5–3,5 kg)"),
    ("hypotrophique", "Hypotrophique (< 2,5 kg)"),
    ("macrosomie", "Macrosomie (> 4 kg)"),
]

TYPE_ACCOUCHEMENT_CHOICES = [
    ("eutocique", "Eutocique"),
    ("dystocique", "Dystocique"),
]

ADAPTATION_NEONATALE_CHOICES = [
    ("bonne", "Bonne"),
    ("mauvaise", "Mauvaise"),
]

# ============================================================
# ALIMENTATION
# ============================================================

ALIMENTATION_TYPE_CHOICES = [
    ("ame", "AME"),
    ("nursie", "Nursie"),
    ("ranombary", "Ranombary"),
    ("autre", "Autre"),
]

REGIME_CHOICES = [
    ("normo_calorique", "Normo-calorique"),
    ("hypo_calorique", "Hypo-calorique"),
    ("hypo_protidique", "Hypo-protidique"),
]

# ============================================================
# VACCINATION
# ============================================================

VACCINS_CHOICES = [
    ("bcg", "BCG"),
    ("vpo0", "VPO 0"),
    ("dtc1", "DTC 1"),
    ("hep1", "Hep 1"),
    ("hib1", "Hib 1"),
    ("pentavalent1", "Pentavalent 1"),
    ("pcv10_1", "PCV-10 1"),
    ("rotarix1", "Rotarix 1"),
    ("vpo1", "VPO 1"),
    ("dtc2", "DTC 2"),
    ("hep2", "Hep 2"),
    ("hib2", "Hib 2"),
    ("pentavalent2", "Pentavalent 2"),
    ("pcv10_2", "PCV-10 2"),
    ("rotarix2", "Rotarix 2"),
    ("vpo2", "VPO 2"),
    ("dtc3", "DTC 3"),
    ("hep3", "Hep 3"),
    ("hib3", "Hib 3"),
    ("pentavalent3", "Pentavalent 3"),
    ("pcv10_3", "PCV-10 3"),
    ("vpi1", "VPI 1"),
    ("vpo3", "VPO 3 / rappel"),
    ("var1", "VAR 1"),
    ("vpi2", "VPI 2"),
    ("var2", "VAR 2"),
    ("autre", "Autre"),
]

# ============================================================
# CONTEXTE ÉPIDÉMIOLOGIQUE
# ============================================================

CONTEXTE_DYSPNEE_CHOICES = [
    ("virose", "Virose"),
    ("tb", "Tuberculose"),
    ("cas_similaire", "Cas similaire"),
    ("allergie", "Allergie"),
    ("tabagisme_passif", "Tabagisme passif"),
    ("autre", "Autre"),
]

CONTEXTE_DIARRHEE_CHOICES = [
    ("cas_similaire", "Cas similaire"),
    ("aliments_suspects", "Aliments suspects"),
    ("zep", "ZEP"),
    ("autre", "Autre"),
]

# ============================================================
# FICHE SOCIALE
# ============================================================

ECLAIRAGE_CHOICES = [
    ("bougie", "Bougie"),
    ("petrole", "Pétrole"),
    ("electricite", "Électricité"),
    ("autre", "Autre"),
]

EAU_CHOICES = [
    ("jirama", "JIRAMA"),
    ("riviere", "Rivière"),
    ("fontaine", "Fontaine"),
    ("autre", "Autre"),
]

COMBUSTIBLE_CHOICES = [
    ("charbon", "Charbon"),
    ("gaz", "Gaz"),
    ("bois", "Bois"),
    ("resistance", "Résistance"),
    ("autre", "Autre"),
]

WC_CHOICES = [
    ("interieur", "Intérieur"),
    ("exterieur", "Extérieur"),
    ("aucun", "Aucun"),
    ("autre", "Autre"),
]

NIVEAU_SOCIAL_CHOICES = [
    ("bas", "Bas niveau social"),
    ("moyen", "Moyen niveau social"),
    ("haut", "Haut niveau social"),
]

# ============================================================
# HISTOIRE DE LA MALADIE
# ============================================================

EVOLUTION_EPISODE_CHOICES = [
    ("aggravation", "Aggravation"),
    ("amelioration", "Amélioration"),
    ("stabilite", "Stabilité"),
]

# ============================================================
# DÉVELOPPEMENT PSYCHOMOTEUR (ENFANT)
# ============================================================

DPM_CONCLUSION_CHOICES = [
    ("normal", "Normal"),
    ("retarde", "Retardé"),
]

# ============================================================
# BIOMÉTRIE / SIGNES GÉNÉRAUX
# ============================================================

BIOMETRIE_CONCLUSION_CHOICES = [
    ("eutrophique", "Eutrophique"),
    ("hypotrophique", "Hypotrophique"),
]

SIGNES_3A2S_CHOICES = [
    ("asthenie", "Asthénie"),
    ("amaigrissement", "Amaigrissement"),
    ("anorexie", "Anorexie"),
    ("fievre", "Fièvre"),
    ("hypersudation", "Hypersudation / Sueurs nocturnes"),
]

# ============================================================
# CHOIX GÉNÉRIQUES UTILISÉS DANS LES EXAMENS
# ============================================================

ABSENT_PRESENT_CHOICES = [
    ("absent", "Absent"),
    ("present", "Présent"),
]

ABSENTE_PRESENTE_CHOICES = [
    ("absente", "Absente"),
    ("presente", "Présente"),
]

ABSENTS_PRESENTS_CHOICES = [
    ("absents", "Absents"),
    ("presents", "Présents"),
]

NORMAL_DIMINUE_AUGMENTE_CHOICES = [
    ("normale", "Normale"),
    ("diminuee", "Diminuée"),
    ("augmentee", "Augmentée"),
]

# ============================================================
# EXAMEN PLEUROPULMONAIRE
# ============================================================

TYPE_RESPIRATION_CHOICES = [
    ("calme_reguliere", "Calme et régulière"),
    ("polypnee", "Polypnée"),
    ("bradypnee", "Bradypnée"),
    ("irreguliere", "Irrégulière"),
]

AMPLITUDE_THORACIQUE_CHOICES = [
    ("normale", "Normale"),
    ("diminuee", "Diminuée"),
    ("exageree", "Exagérée"),
    ("asymetrique", "Asymétrique"),
]

SYMETRIE_THORACIQUE_CHOICES = [
    ("symetrique", "Symétrique"),
    ("asymetrique", "Asymétrique"),
]

SIGNES_LUTTE_CHOICES = [
    ("tirage_sus_claviculaire", "Tirage sus-claviculaire"),
    ("tirage_intercostal", "Tirage intercostal"),
    ("tirage_sous_costal", "Tirage sous-costal"),
    ("tirage_xiphoide", "Tirage xiphoïdien"),
    ("battement_ailes_nez", "Battement des ailes du nez"),
    ("balancement_thoraco_abdominal", "Balancement thoraco-abdominal"),
]

DEFORMATION_THORACIQUE_CHOICES = [
    ("aucune", "Aucune"),
    ("tonneau", "Thorax en tonneau"),
    ("carene", "Thorax en carène"),
    ("pectus_excavatum", "Pectus excavatum"),
    ("scoliose", "Scoliose"),
]

VIBRATIONS_VOCALES_CHOICES = [
    ("normales", "Normales"),
    ("diminuees", "Diminuées"),
    ("abolies", "Abolies"),
    ("exagerees", "Exagérées"),
]

EXPANSION_THORACIQUE_CHOICES = [
    ("normale", "Normale"),
    ("diminuee", "Diminuée"),
    ("asymetrique", "Asymétrique"),
]

SONORITE_PULMONAIRE_CHOICES = [
    ("normale", "Normale (sonore)"),
    ("matite", "Matité"),
    ("submatite", "Submatité"),
    ("hypersonore", "Hypersonore"),
    ("tympanisme", "Tympanisme"),
]

LOCALISATION_PULMONAIRE_CHOICES = [
    ("aucune", "Aucune"),
    ("diffuse", "Diffuse"),
    ("unilaterale_d", "Unilatérale droite"),
    ("unilaterale_g", "Unilatérale gauche"),
    ("bilaterale", "Bilatérale"),
    ("basale", "Basale"),
    ("apicale", "Apicale"),
    ("apicale_d", "Apicale droite"),
    ("apicale_g", "Apicale gauche"),
    ("basale_d", "Basale droite"),
    ("basale_g", "Basale gauche"),
    ("axillaire", "Axillaire"),
]

MOBILITE_BORD_INFERIEUR_POUMON_CHOICES = [
    ("normale", "Normale"),
    ("diminuee", "Diminuée"),
]

MURMURE_VESICULAIRE_CHOICES = [
    ("normal_bien_transmis", "Normal, bien transmis"),
    ("diminue", "Diminué"),
    ("aboli", "Aboli"),
    ("exagere", "Exagéré"),
    ("asymetrique", "Asymétrique"),
]

RALES_CREPITANTS_CHOICES = [
    ("absents", "Absents"),
    ("presents_fins", "Présents (fins)"),
    ("presents_grossiers", "Présents (grossiers)"),
    ("crepitants_velcro", "Crépitants de Velcro"),
]

RALES_SOUS_CREPITANTS_CHOICES = [
    ("absents", "Absents"),
    ("presents", "Présents"),
]

SIBILANCES_CHOICES = [
    ("absentes", "Absentes"),
    ("presentes_expiratoires", "Présentes expiratoires"),
    ("presentes_inspiratoires", "Présentes inspiratoires"),
    ("presentes_bilaterales", "Présentes bilatérales"),
]

RALES_RONFLANTS_CHOICES = [
    ("absents", "Absents"),
    ("presents", "Présents"),
]

SOUFFLE_TUBAIRE_CHOICES = [
    ("absent", "Absent"),
    ("present", "Présent"),
]

FROTTEMENT_PLEURAL_CHOICES = [
    ("absent", "Absent"),
    ("present", "Présent"),
]

# ============================================================
# EXAMEN CARDIOVASCULAIRE
# ============================================================

CYANOSE_CHOICES = [
    ("absente", "Absente"),
    ("centrale", "Centrale"),
    ("peripherique", "Périphérique"),
    ("generale", "Générale"),
]

PALEUR_CHOICES = [
    ("absente", "Absente"),
    ("moderee", "Présente modérée"),
    ("severe", "Présente sévère"),
]

OEDEMES_CHOICES = [
    ("absents", "Absents"),
    ("membres_inferieurs", "Membres inférieurs"),
    ("generalises", "Généralisés"),
    ("anasarque", "Anasarque"),
]

HIPPOCRATISME_DIGITAL_CHOICES = [
    ("absent", "Absent"),
    ("present", "Présent"),
]

CHOC_DE_POINTE_CHOICES = [
    ("normal", "Normal (5ème EIC MCL)"),
    ("deplace", "Déplacé"),
    ("diffus", "Diffus"),
    ("non_palpable", "Non palpable"),
]

RYTHME_CARDIAQUE_CHOICES = [
    ("regulier", "Régulier"),
    ("irregulier", "Irrégulier"),
    ("arythmie_complete", "Arythmie complète"),
]

CHALEUR_EXTREMITES_CHOICES = [
    ("chaudes", "Chaudes"),
    ("tiedes", "Tièdes"),
    ("froides", "Froides"),
]

POULS_PERIPHERIQUES_CHOICES = [
    ("presents_symetriques", "Présents et symétriques"),
    ("diminues", "Diminués"),
    ("absents", "Absents"),
    ("asymetriques", "Asymétriques"),
]

POULS_FEMORAUX_CHOICES = [
    ("presents", "Présents"),
    ("absents", "Absents"),
    ("diminues", "Diminués"),
]

MATITE_CARDIAQUE_CHOICES = [
    ("normale", "Normale"),
    ("augmentee", "Augmentée"),
    ("diminuee", "Diminuée"),
]

BDC_CHOICES = [
    ("bien_frappes", "Bien frappés"),
    ("assourdis", "Assourdis"),
    ("claquants", "Claquants"),
    ("rythme_de_galop", "Rythme de galop"),
]

SOUFFLE_CARDIAQUE_CHOICES = [
    ("absent", "Absent"),
    ("systolique", "Présent systolique"),
    ("diastolique", "Présent diastolique"),
    ("continu", "Présent continu"),
]

LEVINE_CHOICES = [
    ("1", "1/6"),
    ("2", "2/6"),
    ("3", "3/6"),
    ("4", "4/6"),
    ("5", "5/6"),
    ("6", "6/6"),
]

LOCALISATION_SOUFFLE_CHOICES = [
    ("foyer_aortique", "Foyer aortique"),
    ("foyer_pulmonaire", "Foyer pulmonaire"),
    ("foyer_mitral", "Foyer mitral"),
    ("foyer_tricuspide", "Foyer tricuspide"),
    ("meso_cardiaque", "Méso-cardiaque"),
    ("irradie", "Irradié"),
]

BRUITS_SURAJOUTES_CHOICES = [
    ("absents", "Absents"),
    ("claquements_ouverture", "Claquements d'ouverture"),
    ("galop_b3_b4", "Bruit de galop B3/B4"),
    ("frottement_pericardique", "Frottement péricardique"),
]

DEDOUBLEMENT_CHOICES = [
    ("absent", "Absent"),
    ("b1_double", "B1 dédoublé"),
    ("b2_double_fixe", "B2 dédoublé fixe"),
    ("b2_double_respiratoire", "B2 dédoublé respiratoire"),
]

# ============================================================
# EXAMEN DIGESTIF
# ============================================================

VOLUME_ABDOMINAL_CHOICES = [
    ("normal", "Normal"),
    ("distendu", "Distendu"),
    ("retracte", "Rétracté"),
    ("meteorise", "Météorisé"),
    ("globuleux", "Globuleux"),
]

VOUSSURES_CHOICES = [
    ("absentes", "Absentes"),
    ("localisees", "Présentes localisées"),
    ("diffuses", "Présentes diffuses"),
]

CIRCULATION_COLLATERALE_CHOICES = [
    ("absente", "Absente"),
    ("presente", "Présente"),
]

OMBILIC_CHOICES = [
    ("normal", "Normal"),
    ("hernie_ombilicale", "Hernie ombilicale"),
    ("inflamme", "Inflammé"),
    ("ecoulement", "Écoulement"),
]

SOUPLESSE_ABDOMINALE_CHOICES = [
    ("souple", "Souple"),
    ("depressible", "Dépressible"),
    ("defense", "Défense"),
    ("contracture", "Contracture"),
    ("ventre_de_bois", "Ventre de bois"),
]

DOULEUR_ABDOMINALE_CHOICES = [
    ("absente", "Absente"),
    ("diffuse", "Douleur diffuse"),
    ("localisee", "Douleur localisée"),
]

SIGNE_MURPHY_CHOICES = [
    ("negatif", "Négatif"),
    ("positif", "Positif"),
]

POINT_MCBURNEY_CHOICES = [
    ("negatif", "Négatif"),
    ("positif", "Positif"),
]

HEPATOMEGALIE_CHOICES = [
    ("absente", "Absente"),
    ("presente", "Présente"),
]

SPLENOMEGALIE_CHOICES = [
    ("absente", "Absente"),
    ("presente", "Présente"),
]

MASSE_PALPABLE_CHOICES = [
    ("absente", "Absente"),
    ("presente", "Présente"),
]

GLOBE_VESICAL_CHOICES = [
    ("absent", "Absent"),
    ("present", "Présent"),
]

PLI_CUTANE_CHOICES = [
    ("absent", "Absent (hydraté)"),
    ("present", "Présent (déshydraté)"),
]

SONORITE_ABDOMINALE_CHOICES = [
    ("tympanique", "Normale (tympanique)"),
    ("mate_ascite", "Mate (ascite)"),
    ("diminuee_masse", "Diminuée (masse)"),
]

MATITE_HEPATIQUE_CHOICES = [
    ("normale", "Normale"),
    ("augmentee", "Augmentée"),
    ("diminuee", "Diminuée"),
]

MATITE_DECLIVE_CHOICES = [
    ("absente", "Absente"),
    ("presente", "Présente"),
]

BRUITS_HYDRO_AERIQUES_CHOICES = [
    ("presents_normaux", "Présents normaux"),
    ("diminues", "Diminués"),
    ("absents", "Absents"),
    ("exageres", "Exagérés"),
]

SOUFFLE_VASCULAIRE_CHOICES = [
    ("absent", "Absent"),
    ("present", "Présent"),
]

SELLES_CHOICES = [
    ("normales", "Normales"),
    ("diarrhee", "Diarrhée"),
    ("constipation", "Constipation"),
    ("glaires", "Glaires"),
    ("sang", "Sang"),
    ("glairo_sanglantes", "Glairo-sanglantes"),
    ("melena", "Méléna"),
]

VOMISSEMENTS_CHOICES = [
    ("absents", "Absents"),
    ("alimentaires", "Alimentaires"),
    ("bilieux", "Bilieux"),
    ("hematiques", "Hématiques"),
    ("en_jet", "En jet"),
]

MECONIUM_CHOICES = [
    ("emis", "Émis"),
    ("non_emis", "Non émis"),
    ("retarde", "Retardé"),
]

# ============================================================
# EXAMEN NEUROLOGIQUE
# ============================================================

ETAT_CONSCIENCE_CHOICES = [
    ("vigilant", "Vigilant"),
    ("somnolent", "Somnolent"),
    ("obnubile", "Obnubilé"),
    ("stuporeux", "Stuporeux"),
    ("comateux", "Comateux"),
]

MOUVEMENTS_ANORMAUX_CHOICES = [
    ("absents", "Absents"),
    ("convulsions", "Convulsions"),
    ("tremblements", "Tremblements"),
    ("choree", "Chorée"),
    ("myoclonies", "Myoclonies"),
]

ATTITUDE_POSTURE_CHOICES = [
    ("normale", "Normale"),
    ("hypertonie", "Hypertonie"),
    ("hypotonie", "Hypotonie"),
    ("decerebration", "Décérébration"),
    ("decortication", "Décortication"),
]

PUPILLES_CHOICES = [
    ("isocores_reactives", "Isocores réactives"),
    ("mydriase_d", "Mydriase droite"),
    ("mydriase_g", "Mydriase gauche"),
    ("myosis_d", "Myosis droit"),
    ("myosis_g", "Myosis gauche"),
    ("areactives", "Aréactives"),
]

FONTANELLE_CHOICES = [
    ("plane", "Plane"),
    ("bombee", "Bombée"),
    ("deprimee", "Déprimée"),
    ("normo_tendue", "Normo-tendue"),
]

RAIDEUR_NUQUE_CHOICES = [
    ("souple", "Souple"),
    ("raide", "Raide"),
    ("resistance", "Résistance"),
]

KERNIG_BRAGARD_CHOICES = [
    ("negatif", "Négatif"),
    ("positif", "Positif"),
]

TON_MUSCULAIRE_CHOICES = [
    ("normal", "Normal"),
    ("hypertonie", "Hypertonie"),
    ("hypotonie", "Hypotonie"),
    ("spasticite", "Spasticité"),
]

FORCE_MUSCULAIRE_CHOICES = [
    ("normale", "Normale (5/5)"),
    ("paresie", "Parésie"),
    ("plegie", "Plégie"),
]

SENSIBILITE_CHOICES = [
    ("conservee", "Conservée"),
    ("diminuee", "Diminuée"),
    ("abolie", "Abolie"),
]

REFLEXES_OSTEO_TENDINEUX_CHOICES = [
    ("normaux", "Normaux"),
    ("vifs", "Vifs"),
    ("exageres_clonus", "Exagérés (clonus)"),
    ("diminues", "Diminués"),
    ("abolis", "Abolis"),
]

BABINSKI_CHOICES = [
    ("negatif", "Négatif (flexion)"),
    ("positif", "Positif (extension)"),
]

REFLEXES_ARCHEAQUES_CHOICES = [
    ("succion_deglutition", "Succion-déglutition"),
    ("points_cardinaux", "Points cardinaux"),
    ("grasping", "Grasping"),
    ("moro", "Moro"),
    ("marche_automatique", "Marche automatique"),
    ("allongement_croise", "Allongement croisé"),
]

# ============================================================
# ORL / TÊTE ET COU
# ============================================================

DYSMORPHIE_FACIALE_CHOICES = [
    ("absente", "Absente"),
    ("presente", "Présente"),
]

YEUX_CHOICES = [
    ("normaux", "Normaux"),
    ("conjonctivite_purulente", "Conjonctivite purulente"),
    ("conjonctivite_catarrhale", "Conjonctivite catarrhale"),
    ("oedeme_palpebral", "Œdème palpébral"),
    ("ictere_conjonctival", "Ictère conjonctival"),
    ("anemie_conjonctivale", "Anémie conjonctivale"),
]

NEZ_CHOICES = [
    ("permeable", "Perméable"),
    ("atresie_choanes", "Atrésie des choanes"),
    ("rhinorrhee_claire", "Rhinorrhée claire"),
    ("rhinorrhee_purulente", "Rhinorrhée purulente"),
    ("obstrue", "Obstrué"),
]

OREILLES_CHOICES = [
    ("normales", "Normales"),
    ("implantation_basse", "Implantation basse"),
    ("pavillon_mou", "Pavillon mou"),
    ("otorrhee", "Otorrhée"),
    ("otite", "Otite"),
]

LEVRES_CHOICES = [
    ("normales", "Normales"),
    ("fissuraires", "Fissuraires"),
    ("cyanosees", "Cyanosées"),
    ("seches", "Sèches"),
]

MUQUEUSE_BUCCALE_CHOICES = [
    ("rose_humide", "Rose humide"),
    ("seche", "Sèche"),
    ("pale", "Pâle"),
    ("erythemateuse", "Érythémateuse"),
    ("ulcerations", "Ulcérations"),
    ("muguet", "Muguet"),
]

LANGUE_CHOICES = [
    ("normale", "Normale"),
    ("saburrale", "Saburrale"),
    ("depapillee", "Dépapillée"),
    ("fissuraire", "Fissuraire"),
    ("tremblante", "Tremblante"),
]

AMYgDALES_CHOICES = [
    ("normales", "Normales"),
    ("hypertrophiees", "Hypertrophiées"),
    ("erythemateuses", "Érythémateuses"),
    ("enduites", "Enduites"),
]

FENTE_CHOICES = [
    ("absent", "Absent"),
    ("bec_lievre", "Bec de lièvre"),
    ("fente_palatine", "Fente palatine"),
    ("fente_velo_palatine", "Fente vélo-palatine"),
]

FREIN_LANGUE_CHOICES = [
    ("normal", "Normal"),
    ("court", "Court"),
]

COU_MOBILITE_CHOICES = [
    ("normale", "Normale"),
    ("limitee", "Limitée"),
    ("torticolis", "Torticolis"),
]

ADENOPATHIES_CERVICALES_CHOICES = [
    ("absentes", "Absentes"),
    ("presentes", "Présentes"),
]

HEMATOME_SCM_CHOICES = [
    ("absent", "Absent"),
    ("present", "Présent"),
]

GANGLIONS_CERVICAUX_CHOICES = [
    ("absents", "Absents"),
    ("presents_mobiles", "Présents mobiles"),
    ("presents_fixes", "Présents fixes"),
    ("presents_douloureux", "Présents douloureux"),
]

MASSE_CERVICALE_CHOICES = [
    ("absente", "Absente"),
    ("presente", "Présente"),
]

THYROIDE_CHOICES = [
    ("non_palpable", "Non palpable"),
    ("palpable_normale", "Palpable normale"),
    ("goitre", "Goitre"),
]

# ============================================================
# REVÊTEMENT CUTANÉOMUQUEUX
# ============================================================

COLORATION_CUTANEE_CHOICES = [
    ("rose", "Rose"),
    ("pale", "Pâle"),
    ("cyanose", "Cyanose"),
    ("ictere", "Ictère"),
    ("grisatre", "Grisâtre"),
    ("marbrures", "Marbrures"),
    ("erytheme", "Érythème"),
]

HYDRATATION_CHOICES = [
    ("normale", "Normale"),
    ("seche", "Sèche"),
    ("deshydratee", "Déshydratée"),
]

TURGOR_CUTANE_CHOICES = [
    ("normal", "Normal"),
    ("diminue", "Diminué"),
]

ERUPTION_CHOICES = [
    ("absent", "Absent"),
    ("macules", "Macules"),
    ("papules", "Papules"),
    ("vesicules", "Vésicules"),
    ("pustules", "Pustules"),
    ("bulles", "Bulles"),
    ("urticaire", "Urticaire"),
    ("purpura", "Purpura"),
]

DESQUAMATION_CHOICES = [
    ("absente", "Absente"),
    ("presente", "Présente"),
]

PURPURA_CHOICES = [
    ("absent", "Absent"),
    ("present", "Présent"),
]

PETECHIES_CHOICES = [
    ("absentes", "Absentes"),
    ("presentes", "Présentes"),
]

SYNDROME_HEMORRAGIQUE_CHOICES = [
    ("absent", "Absent"),
    ("present", "Présent"),
]

TEMPERATURE_CUTANEE_CHOICES = [
    ("normale", "Normale"),
    ("chaude", "Chaude"),
    ("froide", "Froide"),
]

TEXTURE_CUTANEE_CHOICES = [
    ("normale", "Normale"),
    ("reche", "Rêche"),
    ("lisse", "Lisse"),
    ("induree", "Indurée"),
]

# ============================================================
# OSTÉO-ARTICULAIRE
# ============================================================

HANCHE_LCH_CHOICES = [
    ("negative", "Négative"),
    ("positive", "Positive"),
]

# ============================================================
# TRAITEMENT / ÉVOLUTION
# ============================================================

EVOLUTION_STATUT_CHOICES = [
    ("favorable", "Favorable"),
    ("defavorable", "Défavorable"),
    ("stationnaire", "Stationnaire"),
]

# ============================================================
# STRUCTURES JSON PAR DÉFAUT
# ============================================================

DEFAULT_SEROLOGIES = {
    "bw": {
        "fait": None,
        "resultat": None,
    },
    "vih": {
        "fait": None,
        "resultat": None,
    },
    "toxoplasmose": {
        "fait": None,
        "resultat": None,
    },
    "rubeole": {
        "fait": None,
        "resultat": None,
    },
    "hb": {
        "fait": None,
        "resultat": None,
    },
}

EXAMEN_DEFAULTS = {
    "pleuropulmonaire": {
        "inspection": {
            "frequence_respiratoire": None,
            "type_respiration": None,
            "amplitude_thoracique": None,
            "symetrie_thoracique": None,
            "signes_de_lutte": [],
            "turgescence_jugulaire": None,
            "deformation_thoracique": None,
        },
        "palpation": {
            "vibrations_vocales": None,
            "expansion_thoracique": None,
            "douleur_palpation": None,
            "crepitations_sous_cutanees": None,
        },
        "percussion": {
            "sonorite_globale": None,
            "localisation_anormale": None,
            "mobilite_bord_inferieur_poumon": None,
        },
        "auscultation": {
            "murmure_vesiculaire": None,
            "rales_crepitants": None,
            "rales_sous_crepitants": None,
            "sibilances": [],
            "rales_ronflants": None,
            "souffle_tubaire": None,
            "frottement_pleural": None,
            "localisation_anomalies": [],
        },
        "exceptions": "",
        "conclusion": "",
    },
    "cardiovasculaire": {
        "inspection": {
            "cyanose": None,
            "paleur": None,
            "ictere": None,
            "oedemes": None,
            "turgescence_jugulaire": None,
            "hippocratisme_digital": None,
        },
        "palpation": {
            "frequence_cardiaque": None,
            "choc_de_pointe": None,
            "rythme": None,
            "thrill": None,
            "chaleur_extremites": None,
            "trc_secondes": None,
            "pouls_peripheriques": None,
            "pouls_femoraux": None,
        },
        "percussion": {
            "matite_cardiaque": None,
        },
        "auscultation": {
            "bdc": None,
            "souffle_cardiaque": None,
            "intensite_souffle_levine": None,
            "localisation_souffle": None,
            "bruits_surajoutes": None,
            "dedoublement": None,
        },
        "exceptions": "",
        "conclusion": "",
    },
    "digestif": {
        "inspection": {
            "volume_abdominal": None,
            "voussures": None,
            "circulation_collaterale": None,
            "ombilic": None,
        },
        "palpation": {
            "souplesse_abdominale": None,
            "douleur": None,
            "localisation_douleur": "",
            "signe_de_murphy": None,
            "point_de_mcburney": None,
            "hepatomegalie": None,
            "taille_hepatomegalie_cm": None,
            "splenomegalie": None,
            "taille_splenomegalie_cm": None,
            "masse_palpable": None,
            "localisation_masse": "",
            "globe_vesical": None,
            "pli_cutane": None,
        },
        "percussion": {
            "sonorite_abdominale": None,
            "matite_hepatique": None,
            "matite_declive": None,
        },
        "auscultation": {
            "bruits_hydro_aeriques": None,
            "souffle_vasculaire": None,
        },
        "emission": {
            "selles": [],
            "vomissements": [],
            "emission_meconium": None,
            "autres_precisions": "",
        },
        "exceptions": "",
        "conclusion": "",
    },
    "neurologique": {
        "inspection": {
            "etat_de_conscience": None,
            "score_glasgow": None,
            "score_blantyre": None,
            "mouvements_anormaux": [],
            "attitude_posture": None,
            "pupilles": None,
        },
        "palpation": {
            "fontanelle": None,
            "permeabilite_sutures": "",
            "raideur_nuque": None,
            "signe_kernig_bragard": None,
            "ton_musculaire": None,
            "force_musculaire": None,
            "sensibilite": None,
        },
        "reflexes": {
            "reflexes_osteo_tendineux": None,
            "babinski": None,
            "reflexes_archaiques": [],
        },
        "exceptions": "",
        "conclusion": "",
    },
    "orl": {
        "inspection": {
            "pc_cm": None,
            "dysmorphie_faciale": None,
            "type_dysmorphie": "",
            "yeux": [],
            "nez": [],
            "oreilles": [],
            "levres": None,
            "muqueuse_buccale": [],
            "langue": None,
            "amygdales": None,
            "fente_bec_lievre": None,
            "frein_langue": None,
            "cou_mobilite": None,
            "adenopathies_cervicales": None,
            "hematome_scm": None,
        },
        "palpation": {
            "ganglions_cervicaux": [],
            "masse_cervicale": None,
            "thyroide": None,
        },
        "exceptions": "",
        "conclusion": "",
    },
    "cutaneomuqueux": {
        "inspection": {
            "coloration": [],
            "hydratation": None,
            "turgor_cutane": None,
            "eruption_exantheme": [],
            "desquamation": None,
            "purpura": None,
            "petechies": None,
            "syndrome_hemorragique": None,
            "oedemes": None,
        },
        "palpation": {
            "temperature_cutanee": None,
            "texture": None,
        },
        "exceptions": "",
        "conclusion": "",
    },
    "genitaux": {
        "fille": {
            "petite_levre_clitoris": "",
            "grande_levre": "",
            "orifices_verifies": None,
            "secretion_vaginale_metrorragie": None,
        },
        "garcon": {
            "scrotum": "",
            "presence_testicules": None,
            "mar": None,
            "hydrocele_vaginale": None,
        },
        "exceptions": "",
        "conclusion": "",
    },
    "osteoarticulaire": {
        "ms": "",
        "mi": "",
        "rachis": "",
        "hanche_lch": None,
        "exceptions": "",
        "conclusion": "",
    },
}


# ============================================================
# SUIVI HOSPITALISATION - EXAMEN PHYSIQUE RÉPÉTÉ
# ============================================================

SIGNES_GENERAUX_SUIVI_CHOICES = [
    ("asthenie", "Asthénie"),
    ("fievre", "Fièvre"),
    ("paleur", "Pâleur"),
    ("cyanose", "Cyanose"),
    ("ictere", "Ictère"),
    ("oedemes", "Œdèmes"),
    ("sueurs", "Sueurs"),
    ("agitation", "Agitation"),
    ("lethargie", "Léthargie"),
    ("convulsions", "Convulsions"),
    ("deshydratation", "Déshydratation"),
    ("hypotonie", "Hypotonie"),
    ("hypertonie", "Hypertonie"),
    ("refus_alimentaire", "Refus alimentaire"),
    ("autre", "Autre"),
]

SIGNES_FONCTIONNELS_SUIVI_CHOICES = [
    ("dyspnee", "Dyspnée"),
    ("toux", "Toux"),
    ("douleur", "Douleur"),
    ("vomissements", "Vomissements"),
    ("diarrhee", "Diarrhée"),
    ("constipation", "Constipation"),
    ("oligurie", "Oligurie"),
    ("anurie", "Anurie"),
    ("polyurie", "Polyurie"),
    ("convulsions", "Convulsions"),
    ("refus_alimentaire", "Refus alimentaire"),
    ("somnolence", "Somnolence"),
    ("irritabilite", "Irritabilité"),
    ("autre", "Autre"),
]


# ============================================================
# SIGNES POUR RÉHYDRATATION / SUIVI
# ============================================================

SIGNES_GENERAUX_SUIVI_CHOICES = [
    ("asthenie", "Asthénie"),
    ("fievre", "Fièvre"),
    ("paleur", "Pâleur"),
    ("cyanose", "Cyanose"),
    ("ictere", "Ictère"),
    ("oedemes", "Œdèmes"),
    ("sueurs", "Sueurs"),
    ("agitation", "Agitation"),
    ("lethargie", "Léthargie"),
    ("convulsions", "Convulsions"),
    ("deshydratation", "Déshydratation"),
    ("hypotonie", "Hypotonie"),
    ("hypertonie", "Hypertonie"),
    ("refus_alimentaire", "Refus alimentaire"),
    ("autre", "Autre"),
]

SIGNES_FONCTIONNELS_SUIVI_CHOICES = [
    ("dyspnee", "Dyspnée"),
    ("toux", "Toux"),
    ("douleur", "Douleur"),
    ("vomissements", "Vomissements"),
    ("diarrhee", "Diarrhée"),
    ("constipation", "Constipation"),
    ("oligurie", "Oligurie"),
    ("anurie", "Anurie"),
    ("polyurie", "Polyurie"),
    ("convulsions", "Convulsions"),
    ("refus_alimentaire", "Refus alimentaire"),
    ("somnolence", "Somnolence"),
    ("irritabilite", "Irritabilité"),
    ("autre", "Autre"),
]


ETAT_YEUX_CHOICES = [
    ("enfonce", "Enfoncé"),
    ("cerne", "Cerné"),
    ("normal", "Normal"),
]

ETAT_MUQUEUSES_CHOICES = [
    ("seche", "Sèche"),
    ("peu_humide", "Peu humide"),
    ("humide", "Humide"),
]

PLI_CUTANE_REHYDRATATION_CHOICES = [
    ("persistant", "Persistant"),
    ("efface_lentement", "S'efface lentement"),
    ("efface_rapidement", "S'efface rapidement"),
    ("pas_pli", "Pas de pli cutané"),
]


# ============================================================
# FICHE DE RÉHYDRATATION
# ============================================================

REHYDRATATION_STATUT_CHOICES = [
    ("en_cours", "En cours"),
    ("terminee", "Terminée"),
]

ETAT_YEUX_CHOICES = [
    ("enfonce", "Enfoncé"),
    ("cerne", "Cerné"),
    ("normal", "Normal"),
]

ETAT_MUQUEUSES_CHOICES = [
    ("seche", "Sèche"),
    ("peu_humide", "Peu humide"),
    ("humide", "Humide"),
]

PLI_CUTANE_REHYDRATATION_CHOICES = [
    ("persistant", "Persistant"),
    ("efface_lentement", "S'efface lentement"),
    ("efface_rapidement", "S'efface rapidement"),
    ("pas_pli", "Pas de pli cutané"),
]

URINE_CHOICES = [
    ("oui", "Oui"),
    ("non", "Non"),
]

SELLES_REHYDRATATION_CHOICES = [
    ("absente", "Absente"),
    ("presente", "Présente"),
    ("diarrhee", "Diarrhée"),
    ("glaires", "Glaires"),
    ("sang", "Sang"),
]

VOMISSEMENTS_REHYDRATATION_CHOICES = [
    ("absent", "Absent"),
    ("present", "Présent"),
]


# ============================================================
# TRAITEMENTS AJUSTÉS ET TRACÉS
# ============================================================

TRAITEMENT_AJUSTEMENT_TYPE_CHOICES = [
    ("initial", "Initial"),
    ("ajustement", "Ajustement"),
    ("renouvellement", "Renouvellement"),
    ("suspension", "Suspension"),
    ("arret", "Arrêt"),
]

TYPE_LIGNE_TRAITEMENT_CHOICES = [
    ("medicament", "Médicament"),
    ("soin", "Soin"),
    ("autre", "Autre"),
]

VOIE_TRAITEMENT_CHOICES = [
    ("orale", "Orale"),
    ("iv_directe", "IV directe"),
    ("perfusion", "Perfusion"),
    ("im", "IM"),
    ("sc", "SC"),
    ("inhalation", "Inhalation"),
    ("rectale", "Rectale"),
    ("topique", "Topique"),
    ("ophtalmique", "Ophtalmique"),
    ("auriculaire", "Auriculaire"),
    ("nasale", "Nasale"),
    ("autre", "Autre"),
]

FREQUENCE_TRAITEMENT_CHOICES = [
    ("dose_unique", "Dose unique"),
    ("1_fois_jour", "1 fois/jour"),
    ("2_fois_jour", "2 fois/jour"),
    ("3_fois_jour", "3 fois/jour"),
    ("4_fois_jour", "4 fois/jour"),
    ("toutes_4_heures", "Toutes les 4 heures"),
    ("toutes_6_heures", "Toutes les 6 heures"),
    ("toutes_8_heures", "Toutes les 8 heures"),
    ("toutes_12_heures", "Toutes les 12 heures"),
    ("selon_besoin", "Selon besoin"),
    ("continu", "Continu"),
    ("autre", "Autre"),
]



