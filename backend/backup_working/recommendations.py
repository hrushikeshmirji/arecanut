"""
ICAR-CPCRI Management Recommendations for Arecanut Diseases
============================================================
Maps each disease class to evidence-based management practices
sourced from ICAR–Central Plantation Crops Research Institute guidelines.
"""

from typing import Dict, Any

# ── Disease recommendation database ──────────────────────────────────────────
_RECOMMENDATIONS: Dict[str, Dict[str, Any]] = {
    "Leaf_Spot": {
        "common_name": "Anthracnose / Leaf Spot",
        "disease_name": "Anthracnose / Leaf Spot (Colletotrichum gloeosporioides)",
        "pathogen": "Colletotrichum gloeosporioides",
        "symptoms": "Brown to dark necrotic spots with chlorotic yellow halos on leaf surface.",
        "severity_level": "moderate",
        "chemical": {
            "title": "Chemical Spray",
            "steps": [
                "Foliar spray with 1% Bordeaux mixture (1 kg CuSO₄ + 1 kg lime in 100 L water).",
                "Alternatively, spray Mancozeb 75% WP @ 2 g/L at 15-day intervals during monsoon.",
                "Use Carbendazim 50% WP @ 1 g/L as a systemic option in severe outbreaks.",
            ],
        },
        "cultural": {
            "title": "Cultural Sanitation",
            "steps": [
                "Prune and burn all necrotic / severely infected fronds.",
                "Avoid overhead irrigation to reduce foliar wetness duration.",
                "Maintain adequate spacing (2.7 m × 2.7 m) for air circulation.",
                "Remove weed hosts from the plantation floor.",
            ],
        },
        "fertilizer": {
            "title": "Fertilizer Schedule",
            "steps": [
                "Apply balanced NPK — 100 g N : 40 g P₂O₅ : 140 g K₂O per palm per year.",
                "Split into two doses: first at onset of monsoon, second at retreating monsoon.",
                "Apply 12 kg FYM or compost per palm annually to improve soil health.",
            ],
        },
    },
    "yellow leaf": {
        "common_name": "Yellow Leaf Disease (YLD)",
        "disease_name": "Yellow Leaf Disease (Phytoplasma)",
        "pathogen": "Phytoplasma (Candidatus Phytoplasma)",
        "symptoms": "Progressive yellowing of fronds starting from lower whorl, necrosis, crown tapering.",
        "severity_level": "severe",
        "chemical": {
            "title": "Chemical Spray",
            "steps": [
                "Root feeding with Oxytetracycline HCl (500 ppm) — 100 mL per palm, thrice a year.",
                "Inject Tetracycline HCl through trunk at 45° angle in severe cases.",
                "Spray Imidacloprid 17.8 SL @ 0.5 mL/L to control leafhopper vectors.",
            ],
        },
        "cultural": {
            "title": "Cultural Sanitation",
            "steps": [
                "Improve soil drainage; construct shallow trenches between rows.",
                "Remove and destroy severely diseased palms acting as inoculum sources.",
                "Intercrop with leguminous cover crops to improve soil nitrogen.",
                "Avoid waterlogging — ensure proper bund management.",
            ],
        },
        "fertilizer": {
            "title": "Fertilizer Schedule",
            "steps": [
                "Apply MgSO₄ (Magnesium sulphate) @ 150 g per palm per year.",
                "Apply ZnSO₄ (Zinc sulphate) @ 25 g per palm per year.",
                "Supplement with Borax @ 50 g per palm to correct micro-nutrient deficiency.",
                "Apply 100 g N : 40 g P₂O₅ : 140 g K₂O per palm with organic manure.",
            ],
        },
    },
    "stem cracking": {
        "common_name": "Stem Bleeding / Stem Cracking",
        "disease_name": "Stem Bleeding / Stem Cracking (Thielaviopsis paradoxa)",
        "pathogen": "Thielaviopsis paradoxa (Ceratocystis paradoxa)",
        "symptoms": "Exudation of dark reddish-brown liquid through cracks in the trunk, rotting internal tissues.",
        "severity_level": "severe",
        "chemical": {
            "title": "Chemical Spray",
            "steps": [
                "Chisel out all damaged / discoloured bark tissue until healthy tissue is exposed.",
                "Swab the chiselled area with Coal Tar or Carbendazim paste (5% w/v).",
                "Apply Tridemorph 80% EC @ 5 mL/L as a trunk drench around the lesion margin.",
            ],
        },
        "cultural": {
            "title": "Cultural Sanitation",
            "steps": [
                "Whitewash the trunk with 10% lime slurry up to 1.5 m height annually.",
                "Avoid mechanical injuries during harvest — use trained climbers or mechanical harvesters.",
                "Ensure good drainage around the palm base; avoid soil heaping against the trunk.",
                "Destroy all chiselled diseased bark by burning.",
            ],
        },
        "fertilizer": {
            "title": "Fertilizer Schedule",
            "steps": [
                "Apply Neem cake @ 5 kg per palm to suppress soil-borne pathogens.",
                "Balanced NPK — 100 g N : 40 g P₂O₅ : 140 g K₂O per palm per year.",
                "Apply Trichoderma-enriched FYM @ 10 kg per palm in the basin.",
            ],
        },
    },
    "Bud borer": {
        "common_name": "Inflorescence / Bud Borer",
        "disease_name": "Inflorescence / Bud Borer (Tirathaba mundella)",
        "pathogen": "Tirathaba mundella / Batrachedra arenosella (Lepidoptera)",
        "symptoms": "Boring holes into flower buds and buttons, silk webbing with frass, button shedding.",
        "severity_level": "moderate",
        "chemical": {
            "title": "Chemical Spray",
            "steps": [
                "Crown spray with Chlorpyrifos 20% EC @ 2 mL/L directed at the inflorescence.",
                "Alternatively, spray Quinalphos 25% EC @ 2 mL/L during button stage.",
                "Apply Neem oil 2% emulsion as an eco-friendly deterrent between chemical sprays.",
            ],
        },
        "cultural": {
            "title": "Cultural Sanitation",
            "steps": [
                "Collect and destroy all infested buttons, fallen flowers and cocoons.",
                "Install pheromone traps (5–8 per hectare) for adult moth monitoring.",
                "Maintain plantation hygiene — remove dried spathes and debris from crowns.",
                "Encourage natural predators (Trichogramma parasitoid releases).",
            ],
        },
        "fertilizer": {
            "title": "Fertilizer Schedule",
            "steps": [
                "Apply balanced NPK — 100 g N : 40 g P₂O₅ : 140 g K₂O per palm per year.",
                "Apply Neem cake @ 2 kg per palm basin as a soil amendment.",
                "Foliar spray of KNO₃ @ 1% to strengthen reproductive structures.",
            ],
        },
    },
    "healthy leaf": {
        "common_name": "Healthy Foliage",
        "disease_name": "Healthy Foliage (No Disease Detected)",
        "pathogen": "None — No pathogen detected",
        "symptoms": "Uniform deep green color, vigorous frond development, absence of necrotic lesions or chlorosis.",
        "severity_level": "healthy",
        "chemical": {
            "title": "Chemical Spray",
            "steps": [
                "No chemical treatment required at this time.",
                "Prophylactic Bordeaux mixture (1%) spray during onset of monsoon is recommended.",
            ],
        },
        "cultural": {
            "title": "Cultural Sanitation",
            "steps": [
                "Continue standard plantation maintenance — regular weeding and mulching.",
                "Prune lower dried fronds to maintain crown hygiene.",
                "Monitor palms fortnightly for early disease / pest symptoms.",
            ],
        },
        "fertilizer": {
            "title": "Fertilizer Schedule",
            "steps": [
                "Maintain recommended dose: 100 g N : 40 g P₂O₅ : 140 g K₂O per palm per year.",
                "Apply 12 kg FYM or compost per palm annually.",
                "Lime application @ 1 kg per palm if soil pH < 5.5.",
            ],
        },
    },
    # ── NEW: Koleroga / Fruit Rot ────────────────────────────────────────────
    "fruit_rot": {
        "common_name": "Fruit Rot / Koleroga / Mahali",
        "disease_name": "Fruit Rot / Koleroga (Phytophthora meadii)",
        "pathogen": "Phytophthora meadii (Fungal oomycete)",
        "symptoms": "Water-soaked lesions on immature nuts, white fungal threads between nuts, "
                    "bunch rotting and shedding of nuts in strings during monsoon.",
        "severity_level": "critical",
        "chemical": {
            "title": "Preventive & Curative Sprays",
            "steps": [
                "Prophylactic pre-monsoon spray with 1% Bordeaux mixture on bunches (add resin adhesive/sticker).",
                "During active outbreak, crown-spray Metalaxyl MZ 72% WP @ 2 g/L or Fosetyl-Al @ 2 g/L.",
                "Tying polythene covers (100–200 gauge) over bunches before the onset of monsoon prevents infection.",
            ],
        },
        "cultural": {
            "title": "Sanitation & Disposal",
            "steps": [
                "Immediately collect and destroy fallen rotted nuts to prevent spore buildup in the soil.",
                "Clear dead leaf sheaths and webbed debris from the crown before spraying.",
            ],
        },
        "fertilizer": {
            "title": "Soil Management",
            "steps": [
                "Improve drainage trenches to avoid waterlogging at the palm root zone.",
            ],
        },
    },
    # ── NEW: Anabe Roga / Foot Rot / Basal Stem Rot ─────────────────────────
    "foot_rot": {
        "common_name": "Foot Rot / Anabe Roga / Basal Stem Rot",
        "disease_name": "Foot Rot / Anabe Roga (Ganoderma lucidum)",
        "pathogen": "Ganoderma lucidum (Basidiomycete fungus)",
        "symptoms": "Yellowing and drooping of outer fronds, bracket-shaped fungal conks at stem base, "
                    "internal reddish-brown discolouration of trunk tissues, eventual palm death.",
        "severity_level": "critical",
        "chemical": {
            "title": "Root Feeding & Drenching",
            "steps": [
                "Root feeding with Tridemorph (Calixin) 2 mL in 100 mL water per palm at quarterly intervals.",
                "Drench the root basin (1 meter radius) with 0.1% Hexaconazole (1 mL/L) or Carbendazim (2 g/L).",
            ],
        },
        "cultural": {
            "title": "Containment & Bio-Control",
            "steps": [
                "Dig an isolation trench (30 cm wide, 60 cm deep) around infected palms to halt underground mycelial spread.",
                "Uproot and burn dead infected stumps and bracket conks immediately.",
                "Apply Trichoderma harzianum / viride enriched neem cake (2–3 kg/palm) to surrounding palms.",
            ],
        },
        "fertilizer": {
            "title": "Basin Health",
            "steps": [
                "Apply 500 g agricultural lime per palm annually to reduce soil acidity.",
            ],
        },
    },
    # ── NEW: Spindle Bug ─────────────────────────────────────────────────────
    "spindle_bug": {
        "common_name": "Spindle Bug Damage",
        "disease_name": "Spindle Bug Damage (Carvalhoia arecae)",
        "pathogen": "Carvalhoia arecae (Mirid bug pest)",
        "symptoms": "Brown linear puncture marks on spindle leaves, leaf shredding and crinkling of "
                    "emerging fronds, reduced photosynthetic area.",
        "severity_level": "moderate",
        "chemical": {
            "title": "Axil Spraying / Granules",
            "steps": [
                "Spray the innermost leaf axils and unfurling spindle with Chlorpyrifos 20% EC @ 2 mL/L.",
                "Alternatively, place Phorate 10G or Cartap Hydrochloride granules in perforated sachets inside the spindle axil.",
            ],
        },
        "cultural": {
            "title": "Physical Monitoring",
            "steps": [
                "Inspect newly opened fronds for brown linear puncture marks and leaf shredding.",
                "Maintain weed-free interspaces to minimize alternate host plants.",
            ],
        },
        "fertilizer": {
            "title": "Crown Health",
            "steps": [
                "Ensure adequate potash application to strengthen leaf cuticle resistance.",
            ],
        },
    },
    # ── NEW: Healthy Nut Bunch ───────────────────────────────────────────────
    "healthy_nut": {
        "common_name": "Healthy Arecanut Bunch",
        "disease_name": "Healthy Nut Bunch (No Disease Detected)",
        "pathogen": "None — No pathogen detected",
        "symptoms": "Uniform healthy green nut development, intact calyx, absence of water-soaked lesions or rotting.",
        "severity_level": "healthy",
        "chemical": {
            "title": "Prophylactic Care",
            "steps": [
                "No curative spray needed for healthy bunches.",
                "Apply prophylactic 1% Bordeaux mixture on bunches before the onset of monsoon.",
            ],
        },
        "cultural": {
            "title": "Bunch Maintenance",
            "steps": [
                "Ensure proper bunch tying or propping to prevent stalk snapping under heavy yield.",
                "Tie polythene hoods (100–200 gauge) over bunches during monsoon if in high-rainfall zones.",
            ],
        },
        "fertilizer": {
            "title": "Nutrition for High Yield",
            "steps": [
                "Apply balanced NPK: 100 g N : 40 g P₂O₅ : 140 g K₂O per palm per year.",
                "Supplement with 12 kg FYM/compost and micronutrients (Borax @ 25 g/palm).",
            ],
        },
    },
    # ── NEW: Healthy Trunk / Palm Foot ────────────────────────────────────────
    "healthy_trunk": {
        "common_name": "Healthy Trunk / Base",
        "disease_name": "Healthy Trunk (No Disease Detected)",
        "pathogen": "None — No pathogen detected",
        "symptoms": "Intact uniform bark, absence of weeping lesions, fissures, or fungal conks.",
        "severity_level": "healthy",
        "chemical": {
            "title": "Prophylactic Trunk Care",
            "steps": [
                "Annual whitewashing of trunk up to 1.5 m with 10% lime slurry to prevent sun-scald and borer entry.",
                "No chemical fungicide application required for healthy palm trunks.",
            ],
        },
        "cultural": {
            "title": "Trunk Maintenance & Protection",
            "steps": [
                "Avoid mechanical cuts or climber iron step injuries during harvesting.",
                "Ensure free basin drainage to avoid stagnant water contact with the palm foot.",
                "Remove parasitic plants, moss, or weeds adhering to the trunk base.",
            ],
        },
        "fertilizer": {
            "title": "Basin Nutrition",
            "steps": [
                "Apply 12 kg FYM/compost in a wide circular basin 1 meter away from the trunk base.",
                "Maintain standard balanced NPK: 100 g N : 40 g P₂O₅ : 140 g K₂O per palm per year.",
            ],
        },
    },
    # ── NEW: Non-Arecanut / Invalid Object (OOD Rejection) ───────────────────
    "non_areca": {
        "common_name": "Non-Arecanut Image / Invalid Subject",
        "disease_name": "Non-Arecanut Image Detected",
        "pathogen": "N/A — Out-of-Distribution Image",
        "symptoms": "The uploaded photo does not contain recognized arecanut tissues (nut bunches, leaves, fronds, or trunk/stem).",
        "severity_level": "unknown",
        "chemical": {
            "title": "No Treatment Required",
            "steps": [
                "No agricultural chemical spray is applicable to non-arecanut subjects.",
            ],
        },
        "cultural": {
            "title": "Photo Capture Guidance",
            "steps": [
                "Please capture a focused, clear photo of the arecanut palm, nut bunch, leaf, or trunk.",
                "Avoid capturing unrelated background objects, human faces, everyday household items, or other plant species.",
                "Ensure sufficient daylight illumination without extreme glare or darkness.",
            ],
        },
        "fertilizer": {
            "title": "No Fertilizer Applicable",
            "steps": [
                "Fertilizer scheduling is only applicable for arecanut plantation palms.",
            ],
        },
    },
}

# ── Dynamic Canonical Aliases ────────────────────────────────────────────────
_RECOMMENDATIONS["non_areca"] = _RECOMMENDATIONS["non_areca"]
_RECOMMENDATIONS["invalid"] = _RECOMMENDATIONS["non_areca"]
_RECOMMENDATIONS["out_of_distribution"] = _RECOMMENDATIONS["non_areca"]
_RECOMMENDATIONS["bud_borer"] = _RECOMMENDATIONS["Bud borer"]
_RECOMMENDATIONS["stem_bleeding"] = _RECOMMENDATIONS["stem cracking"]  # Base stem protocol
_RECOMMENDATIONS["stem_cracking"] = _RECOMMENDATIONS["stem cracking"]
_RECOMMENDATIONS["mahali_koleroga"] = _RECOMMENDATIONS["fruit_rot"]
_RECOMMENDATIONS["koleroga"] = _RECOMMENDATIONS["fruit_rot"]
_RECOMMENDATIONS["male koleroga"] = _RECOMMENDATIONS["fruit_rot"]
_RECOMMENDATIONS["yellow_leaf"] = _RECOMMENDATIONS["yellow leaf"]
_RECOMMENDATIONS["yellow_leaf_disease"] = _RECOMMENDATIONS["yellow leaf"]
_RECOMMENDATIONS["healthy_leaf"] = _RECOMMENDATIONS["healthy leaf"]
_RECOMMENDATIONS["healthy_nut"] = _RECOMMENDATIONS["healthy_nut"]
_RECOMMENDATIONS["healthy_trunk"] = _RECOMMENDATIONS["healthy_trunk"]
_RECOMMENDATIONS["healthy_foot"] = _RECOMMENDATIONS["healthy_trunk"]
_RECOMMENDATIONS["anabe_roga"] = _RECOMMENDATIONS["foot_rot"]
_RECOMMENDATIONS["basal_stem_rot"] = _RECOMMENDATIONS["foot_rot"]


def get_recommendation(disease_name: str) -> Dict[str, Any]:
    """
    Retrieve ICAR-CPCRI management recommendations for a given disease class.
    """
    data = None
    if disease_name in _RECOMMENDATIONS:
        data = _RECOMMENDATIONS[disease_name]
    else:
        for key, value in _RECOMMENDATIONS.items():
            if key.lower() == disease_name.lower():
                data = value
                break

    if data is None:
        data = {
            "common_name": disease_name,
            "disease_name": disease_name,
            "pathogen": "Unknown",
            "symptoms": "Unclassified symptoms.",
            "severity_level": "unknown",
            "chemical": {
                "title": "Chemical Spray",
                "steps": ["Consult a local ICAR-CPCRI extension officer for specific recommendations."],
            },
            "cultural": {
                "title": "Cultural Sanitation",
                "steps": ["Maintain standard plantation hygiene practices."],
            },
            "fertilizer": {
                "title": "Fertilizer Schedule",
                "steps": ["Follow recommended NPK dose: 100:40:140 g per palm per year."],
            },
        }

    return {
        **data,
        "chemical_treatment": "\n".join(data["chemical"]["steps"]),
        "cultural_measures": "\n".join(data["cultural"]["steps"]),
        "fertilizer_plan": "\n".join(data["fertilizer"]["steps"]),
    }
