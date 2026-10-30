"""
ArecaGuard — Disease Advisory & Management Protocols (ICAR-CPCRI Standard)
==========================================================================
Ground-truth agronomic management guidelines sourced from ICAR-Central
Plantation Crops Research Institute (CPCRI), Kasaragod / Regional Station Vittal.

Provides actionable chemical, cultural, and fertilizer recommendations
tailored to specific arecanut palm diseases. Includes full bilingual support
(English and Kannada / ಕನ್ನಡ).
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
        "translations": {
            "kn": {
                "common_name": "ಎಲೆ ಚುಕ್ಕೆ ರೋಗ (Leaf Spot)",
                "disease_name": "ಎಲೆ ಚುಕ್ಕೆ ರೋಗ (Colletotrichum gloeosporioides)",
                "symptoms": "ಎಲೆಗಳ ಮೇಲೆ ಕಂದು ಅಥವಾ ಕಪ್ಪು ಬಣ್ಣದ ಚುಕ್ಕೆಗಳು ಮತ್ತು ಹಳದಿ ಬಣ್ಣದ ವೃತ್ತಾಕಾರದ ಅಂಚುಗಳು ಕಾಣಿಸಿಕೊಳ್ಳುವುದು.",
                "chemical": {
                    "title": "ರಾಸಾಯನಿಕ ಸಿಂಪಡಣೆ (Chemical Spray)",
                    "steps": [
                        "1% ಬೋರ್ಡೋ ಮಿಶ್ರಣವನ್ನು (1 ಕೆಜಿ ಮೈಲುತುತ್ತು + 1 ಕೆಜಿ ಸುಣ್ಣ / 100 ಲೀಟರ್ ನೀರು) ಎಲೆಗಳಿಗೆ ಸಿಂಪಡಿಸಿ.",
                        "ಮಳೆಗಾಲದಲ್ಲಿ 15 ದಿನಗಳ ಅಂತರದಲ್ಲಿ ಮ್ಯಾಂಕೋಜೆಬ್ 75% WP (2 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.",
                        "ತೀವ್ರ ಬಾಧೆಯಿದ್ದಾಗ ಕಾರ್ಬೆಂಡಾಜಿಮ್ 50% WP (1 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.",
                    ],
                },
                "cultural": {
                    "title": "ತೋಟದ ಸ್ವಚ್ಛತೆ (Cultural Sanitation)",
                    "steps": [
                        "ರೋಗಪೀಡಿತ ಒಣಗಿದ ಎಲೆಗಳನ್ನು ಕತ್ತರಿಸಿ ತೋಟದಿಂದ ಹೊರಹಾಕಿ ಸುಟ್ಟುಹಾಕಿ.",
                        "ಎಲೆಗಳ ಮೇಲೆ ಅತಿಯಾದ ತೇವಾಂಶ ಇರದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.",
                        "ಗಾಳಿ-ಬೆಳಕು ಚೆನ್ನಾಗಿ ಆಡುವಂತೆ ಸೂಕ್ತ ಅಂತರ (2.7 ಮೀ × 2.7 ಮೀ) ಕಾಪಾಡಿ.",
                    ],
                },
                "fertilizer": {
                    "title": "ಗೊಬ್ಬರ ನಿರ್ವಹಣೆ (Fertilizer Schedule)",
                    "steps": [
                        "ಶಿಫಾರಸು ಮಾಡಿದ NPK: 100 ಗ್ರಾಂ N : 40 ಗ್ರಾಂ P₂O₅ : 140 ಗ್ರಾಂ K₂O ವರ್ಷಕ್ಕೆ ನೀಡಿ.",
                        "ವಾರ್ಷಿಕ 12 ಕೆಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರವನ್ನು ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.",
                    ],
                },
            }
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
        "translations": {
            "kn": {
                "common_name": "ಹಳದಿ ಎಲೆ ರೋಗ (Yellow Leaf Disease)",
                "disease_name": "ಹಳದಿ ಎಲೆ ರೋಗ (Phytoplasma)",
                "symptoms": "ಕೆಳಭಾಗದ ಎಲೆಗಳ ತುದಿಯಿಂದ ಹಳದಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗುವುದು, ಎಲೆಗಳು ಒಣಗುವುದು, ಮರದ ಸುಳಿ ಕಿರಿದಾಗುವುದು ಮತ್ತು ಇಳುವರಿ ಗಣನೀಯವಾಗಿ ಕುಸಿಯುವುದು.",
                "chemical": {
                    "title": "ರಾಸಾಯನಿಕ ಹಾಗೂ ವೆಕ್ಟರ್ ನಿಯಂತ್ರಣ (Chemical Spray)",
                    "steps": [
                        "ರೋಗ ಹರಡುವ ಜಿಗಿಹುಳುಗಳನ್ನು ನಿಯಂತ್ರಿಸಲು ಇಮಿಡಾಕ್ಲೋಪ್ರಿಡ್ 17.8 SL (0.5 ಮಿ.ಲೀ/ಲೀ) ಸಿಂಪಡಿಸಿ.",
                        "ಆಕ್ಸಿಟೆಟ್ರಾಸೈಕ್ಲಿನ್ ಹೈಡ್ರೋಕ್ಲೋರೈಡ್ (500 ppm) ದ್ರಾವಣವನ್ನು ಬೇರಿನ ಮೂಲಕ ಉಣಿಸಿ (100 ಮಿ.ಲೀ/ಮರ).",
                    ],
                },
                "cultural": {
                    "title": "ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಮತ್ತು ನೈರ್ಮಲ್ಯ (Cultural Sanitation)",
                    "steps": [
                        "ತೀವ್ರವಾಗಿ ಸೋಂಕಿತ ಮತ್ತು ಒಣಗಿದ ಗರಿಗಳನ್ನು ಕತ್ತರಿಸಿ ನಾಶಪಡಿಸಿ.",
                        "ಸಾವಯವ ಗೊಬ್ಬರ ಮತ್ತು ಹಸಿರೆಲೆ ಗೊಬ್ಬರವನ್ನು ಹೆಚ್ಚಾಗಿ ಬಳಸಿ ಮಣ್ಣಿನ ತೇವಾಂಶ ಮತ್ತು ಫಲವತ್ತತೆ ಕಾಪಾಡಿ.",
                        "ತೋಟದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಉತ್ತಮ ಬಸಿಗಾಲುವೆಗಳನ್ನು ನಿರ್ಮಿಸಿ.",
                    ],
                },
                "fertilizer": {
                    "title": "ಸುಧಾರಿತ ಪೋಷಕಾಂಶ ವೇಳಾಪಟ್ಟಿ (Fertilizer Schedule)",
                    "steps": [
                        "ರೋಗಪೀಡಿತ ಮರಗಳಿಗೆ ಪೊಟ್ಯಾಶ್ ಪ್ರಮಾಣವನ್ನು 50% ಹೆಚ್ಚಿಸಿ (200 ಗ್ರಾಂ K₂O/ಮರ).",
                        "ಮೆಗ್ನೀಸಿಯಮ್ ಸಲ್ಫೇಟ್ (150 ಗ್ರಾಂ) ಮತ್ತು ಬೋರಾಕ್ಸ್ (50 ಗ್ರಾಂ) ಮರದ ಬುಡಕ್ಕೆ ನೀಡಿ.",
                        "ಪ್ರತಿ ಮರಕ್ಕೆ 15 ಕೆಜಿ ಎರೆಹುಳು ಗೊಬ್ಬರ ಅಥವಾ ಕಾಂಪೋಸ್ಟ್ ಒದಗಿಸಿ.",
                    ],
                },
            }
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
        "translations": {
            "kn": {
                "common_name": "ಕಾಂಡ ಸ್ರಾವ ರೋಗ / ಕಾಂಡ ಸೀಳುವಿಕೆ (Stem Bleeding)",
                "disease_name": "ಕಾಂಡ ಸ್ರಾವ ರೋಗ (Thielaviopsis paradoxa)",
                "symptoms": "ಕಾಂಡದ ಕೆಳಭಾಗದಲ್ಲಿ ಸೀಳುಗಳು ಉಂಟಾಗಿ, ಅಲ್ಲಿಂದ ಕಡು ಕೆಂಪು-ಕಂದು ಬಣ್ಣದ ದ್ರವ ಜಿನುಗುವುದು ಮತ್ತು ಕಾಂಡದ ಒಳಭಾಗ ಕೊಳೆಯುವುದು.",
                "chemical": {
                    "title": "ಗಾಯದ ಸಂಸ್ಕರಣೆ ಮತ್ತು ಲೇಪನ (Chemical Spray)",
                    "steps": [
                        "ಕಾಂಡದ ಸೋಂಕಿತ ಭಾಗವನ್ನು ಹರಿತವಾದ ಉಳಿಯಿಂದ ಕೆರೆದು, ಕಲ್ಲಿದ್ದಲು ಟಾರ್ ಅಥವಾ ಬೋರ್ಡೋ ಪೇಸ್ಟ್ ಲೇಪಿಸಿ.",
                        "ಕಾರ್ಬೆಂಡಾಜಿಮ್ 50% WP (2 ಗ್ರಾಂ/ಲೀ) ಅಥವಾ ಟ್ರೈಡೆಮಾರ್ಫ್ (5 ಮಿ.ಲೀ/ಲೀ) ದ್ರಾವಣದಿಂದ ಕಾಂಡಕ್ಕೆ ಸಿಂಪಡಿಸಿ.",
                        "ಕಾಂಡದ ಬುಡಕ್ಕೆ 0.2% ತಾಮ್ರದ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ದ್ರಾವಣ ಸುರಿಯಿರಿ.",
                    ],
                },
                "cultural": {
                    "title": "ಕಾಂಡ ಸಂರಕ್ಷಣೆ ಮತ್ತು ಸ್ವಚ್ಛತೆ (Cultural Sanitation)",
                    "steps": [
                        "ಕಳೆ ಕೀಳುವಾಗ ಅಥವಾ ಅಡಿಕೆ ಕೊಯ್ಯುವಾಗ ಕಾಂಡಕ್ಕೆ ಯಾವುದೇ ಯಾಂತ್ರಿಕ ಗಾಯವಾಗದಂತೆ ಎಚ್ಚರವಹಿಸಿ.",
                        "ಬೇಸಿಗೆಯಲ್ಲಿ ಬಿಸಿಲಿನ ತಾಪದಿಂದ ಕಾಂಡ ಬಿರಿಯದಂತೆ 1.5 ಮೀಟರ್ ಎತ್ತರದವರೆಗೆ ಸುಣ್ಣದ ಗಿಲಾವು (10% Lime slurry) ಹಚ್ಚಿ.",
                        "ಕೆರೆದ ರೋಗಪೀಡಿತ ತೊಗಟೆಯನ್ನು ತೋಟದಿಂದ ಹೊರತೆಗೆದು ಸುಟ್ಟುಹಾಕಿ.",
                    ],
                },
                "fertilizer": {
                    "title": "ಮಣ್ಣಿನ ಪೋಷಣೆ (Fertilizer Schedule)",
                    "steps": [
                        "ಬೇವು ಹಿಂಡಿ (5 ಕೆಜಿ/ಮರ) ಮತ್ತು ಟ್ರೈಕೋಡರ್ಮಾ ಹರ್ಜಿಯಾನಮ್ ಮಿಶ್ರಣವನ್ನು ಬುಡಕ್ಕೆ ಹಾಕಿ.",
                        "ಶಿಫಾರಸು ಮಾಡಿದ NPK ಗೊಬ್ಬರದೊಂದಿಗೆ ಸಾವಯವ ಗೊಬ್ಬರವನ್ನು ನಿಯಮಿತವಾಗಿ ನೀಡಿ.",
                    ],
                },
            }
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
        "translations": {
            "kn": {
                "common_name": "ಸುಳಿ ತಿಗಣೆ / ಮೊಗ್ಗು ಕೊರಕ (Bud Borer)",
                "disease_name": "ಸುಳಿ ತಿಗಣೆ ಮತ್ತು ಮೊಗ್ಗು ಕೊರಕ ಕೀಟಬಾಧೆ",
                "symptoms": "ಹೂಗೊಂಚಲು ಮತ್ತು ಎಳೆಯ ಸಿಂಗಾರಗಳಲ್ಲಿ ರಂಧ್ರಗಳು, ಜೇಡರ ಬಲೆಯಂತಹ ನೂಲು ಮತ್ತು ಮಲದ ಕಣಗಳು, ಸಿಂಗಾರ ಕಪ್ಪಾಗಿ ಉದುರುವುದು.",
                "chemical": {
                    "title": "ಸುಳಿ ಸಿಂಪಡಣೆ ಮತ್ತು ಕೀಟನಾಶಕ (Chemical Spray)",
                    "steps": [
                        "ಹೂಗೊಂಚಲಿಗೆ ಗುರಿಯಿಟ್ಟು ಕ್ಲೋರ್ಪೈರಿಫಾಸ್ 20% EC (2 ಮಿ.ಲೀ/ಲೀ) ಸಿಂಪಡಿಸಿ.",
                        "ಪರ್ಯಾಯವಾಗಿ, ಸಿಂಗಾರ ಹಂತದಲ್ಲಿ ಕ್ವಿನಾಲ್ಫಾಸ್ 25% EC (2 ಮಿ.ಲೀ/ಲೀ) ಸಿಂಪಡಿಸಿ.",
                        "ಪರಿಸರ ಸ್ನೇಹಿ ನಿಯಂತ್ರಣಕ್ಕಾಗಿ 2% ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ.",
                    ],
                },
                "cultural": {
                    "title": "ತೋಟದ ನೈರ್ಮಲ್ಯ (Cultural Sanitation)",
                    "steps": [
                        "ಉದುರಿದ ಕೀಟಬಾಧಿತ ಸಿಂಗಾರ, ಹೂವು ಮತ್ತು ಕೋಶಗಳನ್ನು ಆರಿಸಿ ಸುಟ್ಟುಹಾಕಿ.",
                        "ಪ್ರೌಢ ಪತಂಗಗಳ ನಿಗಾಕ್ಕಾಗಿ ಹೆಕ್ಟೇರಿಗೆ 5-8 ಮೋಹಕ ಬಲೆಗಳನ್ನು (Pheromone traps) ಅಳವಡಿಸಿ.",
                        "ಮರದ ಸುಳಿಯಲ್ಲಿರುವ ಒಣ ಹೊಂಬಾಳೆ ಮತ್ತು ಕಸಕಡ್ಡಿಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ.",
                    ],
                },
                "fertilizer": {
                    "title": "ಪೋಷಕಾಂಶ ವೇಳಾಪಟ್ಟಿ (Fertilizer Schedule)",
                    "steps": [
                        "ಪ್ರತಿ ಮರದ ಬುಡಕ್ಕೆ 2 ಕೆಜಿ ಬೇವಿನ ಹಿಂಡಿ ಸೇರಿಸಿ.",
                        "ಸಮತೋಲಿತ NPK ಗೊಬ್ಬರದೊಂದಿಗೆ 1% KNO₃ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ ಹೂಗೊಂಚಲನ್ನು ಬಲಪಡಿಸಿ.",
                    ],
                },
            }
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
        "translations": {
            "kn": {
                "common_name": "ಆರೋಗ್ಯಕರ ಗರಿಗಳು (Healthy Leaf)",
                "disease_name": "ಆರೋಗ್ಯಕರ ಅಡಿಕೆ ಗರಿ (ಯಾವುದೇ ರೋಗವಿಲ್ಲ)",
                "symptoms": "ಹಸಿರಾದ ಸಮೃದ್ಧ ಗರಿಗಳು, ಯಾವುದೇ ಚುಕ್ಕೆಗಳು, ಹಳದಿ ಅಥವಾ ಕೊಳೆತ ಲಕ್ಷಣಗಳಿಲ್ಲ.",
                "chemical": {
                    "title": "ಮುನ್ನೆಚ್ಚರಿಕಾ ರಕ್ಷಣೆ (Prophylactic Care)",
                    "steps": [
                        "ಪ್ರಸ್ತುತ ಯಾವುದೇ ರಾಸಾಯನಿಕ ಚಿಕಿತ್ಸೆ ಅಗತ್ಯವಿಲ್ಲ.",
                        "ಮುಂಗಾರು ಆರಂಭದಲ್ಲಿ ಮುನ್ನೆಚ್ಚರಿಕೆಯಾಗಿ 1% ಬೋರ್ಡೋ ಮಿಶ್ರಣ ಸಿಂಪಡಿಸಬಹುದು.",
                    ],
                },
                "cultural": {
                    "title": "ತೋಟದ ನಿರ್ವಹಣೆ (Cultural Maintenance)",
                    "steps": [
                        "ನಿಯಮಿತ ಕಳೆ ನಿರ್ವಹಣೆ ಮತ್ತು ಮಣ್ಣಿನ ಹೊದಿಕೆ (Mulching) ಮುಂದುವರಿಸಿ.",
                        "ಕೆಳಭಾಗದ ಒಣಗಿದ ಗರಿಗಳನ್ನು ಕತ್ತರಿಸಿ ಸುಳಿಯನ್ನು ಸ್ವಚ್ಛವಾಗಿಡಿ.",
                    ],
                },
                "fertilizer": {
                    "title": "ನಿಯಮಿತ ಪೋಷಕಾಂಶ ವೇಳಾಪಟ್ಟಿ (Fertilizer Schedule)",
                    "steps": [
                        "ಪ್ರತಿ ಮರಕ್ಕೆ ವಾರ್ಷಿಕ 100 ಗ್ರಾಂ N : 40 ಗ್ರಾಂ P₂O₅ : 140 ಗ್ರಾಂ K₂O ನೀಡಿ.",
                        "ವಾರ್ಷಿಕ 12 ಕೆಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರವನ್ನು ಮರದ ಬುಡಕ್ಕೆ ನೀಡಿ.",
                    ],
                },
            }
        },
    },
    # ── Koleroga / Fruit Rot ────────────────────────────────────────────────
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
        "translations": {
            "kn": {
                "common_name": "ಕೊಳೆ ರೋಗ (Mahali / Koleroga)",
                "disease_name": "ಮಹಾಲಿ / ಕೊಳೆ ರೋಗ (Phytophthora meadii)",
                "symptoms": "ಅಡಿಕೆ ಕಾಯಿಗಳ ಮೇಲೆ ನೀರಿನಿಂದ ಕೂಡಿದ ಕಪ್ಪು ಮಚ್ಚೆಗಳು, ಕಾಯಿಗಳ ನಡುವೆ ಬಿಳಿ ಬಣ್ಣದ ಶಿಲೀಂಧ್ರ ಬೆಳೆವಣಿಗೆ, ಕಾಯಿಗಳು ಅಕಾಲಿಕವಾಗಿ ಗೊನೆಯಿಂದ ಉದುರುವುದು.",
                "chemical": {
                    "title": "ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಣೆ (Chemical Spray)",
                    "steps": [
                        "ಮುಂಗಾರು ಆರಂಭವಾಗುವ ಮುನ್ನ 1% ಬೋರ್ಡೋ ಮಿಶ್ರಣವನ್ನು ಅಂಟು ಬೆರೆಸಿ ಗೊನೆಗಳಿಗೆ ಸಂಪೂರ್ಣವಾಗಿ ಸಿಂಪಡಿಸಿ.",
                        "ರೋಗದ ತೀವ್ರತೆಯಿದ್ದಾಗ ಮೆಟಲಾಕ್ಸಿಲ್ MZ 72% WP (2 ಗ್ರಾಂ/ಲೀ) ಅಥವಾ ಪೊಟ್ಯಾಸಿಯಮ್ ಫಾಸ್ಫೋನೇಟ್ (3 ಮಿ.ಲೀ/ಲೀ) ಸಿಂಪಡಿಸಿ.",
                        "ಮಳೆಗಾಲಕ್ಕೂ ಮುನ್ನ ಗೊನೆಗಳಿಗೆ 100-200 ಗೇಜ್ ಪಾಲಿಥೀನ್ ಹೊದಿಕೆ (ಕವರ್) ಕಟ್ಟುವುದು ಅತ್ಯಂತ ಪರಿಣಾಮಕಾರಿ.",
                    ],
                },
                "cultural": {
                    "title": "ತೋಟದ ನೈರ್ಮಲ್ಯ ಮತ್ತು ನಿರ್ವಹಣೆ (Cultural Sanitation)",
                    "steps": [
                        "ನೆಲಕ್ಕೆ ಬಿದ್ದ ಕೊಳೆತ ಕಾಯಿಗಳನ್ನು ತಕ್ಷಣ ಆರಿಸಿ ತೋಟದಿಂದ ಹೊರತೆಗೆದು ಸುಟ್ಟುಹಾಕಿ.",
                        "ಸಿಂಪಡಣೆಗೆ ಮುನ್ನ ಸುಳಿಯಲ್ಲಿರುವ ಒಣ ಎಲೆ ಕವಚಗಳು ಮತ್ತು ಕೊಳೆತ ಕಸವನ್ನು ತೆಗೆದುಹಾಕಿ.",
                    ],
                },
                "fertilizer": {
                    "title": "ಬಸಿಗಾಲುವೆ ಮತ್ತು ಪೋಷಕಾಂಶ (Fertilizer Schedule)",
                    "steps": [
                        "ತೋಟದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಆಳವಾದ ಬಸಿಗಾಲುವೆಗಳನ್ನು ನಿರ್ಮಿಸಿ.",
                        "ಪ್ರತಿ ಮರಕ್ಕೆ 12 ಕೆಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರದೊಂದಿಗೆ ಟ್ರೈಕೋಡರ್ಮಾ ಸೇರಿಸಿ ಬುಡಕ್ಕೆ ಹಾಕಿ.",
                    ],
                },
            }
        },
    },
    # ── Anabe Roga / Foot Rot / Basal Stem Rot ───────────────────────────────
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
        "translations": {
            "kn": {
                "common_name": "ಅಣಬೆ ರೋಗ / ಬುಡ ಕೊಳೆ ರೋಗ (Anabe Roga)",
                "disease_name": "ಅಣಬೆ ರೋಗ (Ganoderma lucidum)",
                "symptoms": "ಕೆಳಭಾಗದ ಗರಿಗಳು ಹಳದಿಯಾಗಿ ಕೆಳಗೆ ಜೋತುಬೀಳುವುದು, ಕಾಂಡದ ಬುಡದಲ್ಲಿ ಅಣಬೆಯಂತಹ ಶಿಲೀಂಧ್ರ ಬೆಳೆಯುವುದು, ಕಾಂಡದ ಒಳಭಾಗ ಕೊಳೆತು ಮರ ಒಣಗಿ ಸಾಯುವುದು.",
                "chemical": {
                    "title": "ಬೇರು ಉಣಿಸುವಿಕೆ ಮತ್ತು ಬುಡ ನೆನೆಸುವುದು (Chemical Spray)",
                    "steps": [
                        "ಟ್ರೈಡೆಮಾರ್ಫ್ (ಕ್ಯಾಲಿಕ್ಸಿನ್) 2 ಮಿ.ಲೀ ಅನ್ನು 100 ಮಿ.ಲೀ ನೀರಿನಲ್ಲಿ ಬೆರೆಸಿ ಪ್ರತಿ 3 ತಿಂಗಳಿಗೊಮ್ಮೆ ಬೇರಿನ ಮೂಲಕ ಉಣಿಸಿ.",
                        "ಮರದ ಬುಡದ 1 ಮೀಟರ್ ವ್ಯಾಪ್ತಿಯ ಮಣ್ಣಿಗೆ 0.1% ಹೆಕ್ಸಾಕೊನಜೋಲ್ (1 ಮಿ.ಲೀ/ಲೀ) ದ್ರಾವಣ ಸುರಿಯಿರಿ.",
                    ],
                },
                "cultural": {
                    "title": "ರೋಗ ನಿಯಂತ್ರಣ ಕಂದಕ (Cultural Sanitation)",
                    "steps": [
                        "ಶಿಲೀಂಧ್ರ ಬೇರುಗಳ ಮೂಲಕ ಇತರ ಮರಗಳಿಗೆ ಹರಡದಂತೆ ರೋಗಪೀಡಿತ ಮರದ ಸುತ್ತ 30 ಸೆಂ.ಮೀ ಅಗಲ, 60 ಸೆಂ.ಮೀ ಆಳದ ಪ್ರತ್ಯೇಕ ಕಂದಕ ತೋಡಿ.",
                        "ಸತ್ತ ರೋಗಪೀಡಿತ ಮರದ ಬುಡ ಹಾಗೂ ಅಣಬೆಗಳನ್ನು ತಕ್ಷಣ ಅಗೆದು ತೆಗೆದು ಸುಟ್ಟುಹಾಕಿ.",
                        "ಸುತ್ತಮುತ್ತಲಿನ ಆರೋಗ್ಯವಂತ ಮರಗಳಿಗೆ ಟ್ರೈಕೋಡರ್ಮಾ ಮಿಶ್ರಿತ ಬೇವಿನ ಹಿಂಡಿ (2-3 ಕೆಜಿ/ಮರ) ಹಾಕಿ.",
                    ],
                },
                "fertilizer": {
                    "title": "ಸುಣ್ಣ ಮತ್ತು ಮಣ್ಣಿನ ನಿರ್ವಹಣೆ (Fertilizer Schedule)",
                    "steps": [
                        "ಮಣ್ಣಿನ ಆಮ್ಲೀಯತೆ ತಗ್ಗಿಸಲು ಪ್ರತಿ ಮರಕ್ಕೆ ವಾರ್ಷಿಕ 500 ಗ್ರಾಂ ಕೃಷಿ ಸುಣ್ಣ ಹಾಕಿ.",
                    ],
                },
            }
        },
    },
    # ── Spindle Bug ──────────────────────────────────────────────────────────
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
        "translations": {
            "kn": {
                "common_name": "ಸುಳಿ ತಿಗಣೆ ಬಾಧೆ (Spindle Bug)",
                "disease_name": "ಸುಳಿ ತಿಗಣೆ (Carvalhoia arecae)",
                "symptoms": "ಎಳೆಯ ಸುಳಿಯ ಮೇಲೆ ಕಂದು ರೇಖಾತ್ಮಕ ಚುಕ್ಕೆಗಳು, ಎಲೆಗಳು ಸೀಳಾಗುವುದು, ಗರಿಗಳು ಸರಿಯಾಗಿ ಬಿರಿಯದೇ ಇರುವುದು.",
                "chemical": {
                    "title": "ಸುಳಿ ಸಿಂಪಡಣೆ (Chemical Spray)",
                    "steps": [
                        "ಸುಳಿಯ ಎಲೆಗಳ ಕಂಕುಳಿಗೆ ಕ್ಲೋರ್ಪೈರಿಫಾಸ್ 20% EC (2 ಮಿ.ಲೀ/ಲೀ) ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ.",
                        "ಪರ್ಯಾಯವಾಗಿ, ರಂಧ್ರವಿರುವ ಪ್ಲಾಸ್ಟಿಕ್ ಚೀಲದಲ್ಲಿ ಫೋರೇಟ್ 10G ಹರಳುಗಳನ್ನು ತುಂಬಿ ಸುಳಿಯ ಕಂಕುಳಲ್ಲಿ ಇಡಿ.",
                    ],
                },
                "cultural": {
                    "title": "ನಿಗಾ ಮತ್ತು ಸ್ವಚ್ಛತೆ (Cultural Sanitation)",
                    "steps": [
                        "ಹೊಸದಾಗಿ ಬಿರಿಯುವ ಸುಳಿಗಳನ್ನು ವಾರಕ್ಕೊಮ್ಮೆ ಪರೀಕ್ಷಿಸಿ ಕೀಟಬಾಧೆ ಪತ್ತೆಹಚ್ಚಿ.",
                        "ತೋಟದಲ್ಲಿ ಕಳೆಗಳನ್ನು ತೆಗೆದು ಕೀಟಗಳ ಆಶ್ರಯ ತಾಣಗಳನ್ನು ನಾಶಮಾಡಿ.",
                    ],
                },
                "fertilizer": {
                    "title": "ಪೋಷಕಾಂಶ (Fertilizer Schedule)",
                    "steps": [
                        "ಎಲೆಗಳ ಹೊರಪದರ ಗಟ್ಟಿಗೊಳ್ಳಲು ಶಿಫಾರಸು ಮಾಡಿದ ಪೊಟ್ಯಾಶ್ ಗೊಬ್ಬರವನ್ನು ತಪ್ಪದೇ ನೀಡಿ.",
                    ],
                },
            }
        },
    },
    # ── Healthy Nut Bunch ────────────────────────────────────────────────────
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
        "translations": {
            "kn": {
                "common_name": "ಆರೋಗ್ಯಕರ ಅಡಿಕೆ ಗೊನೆ (Healthy Nut Bunch)",
                "disease_name": "ಆರೋಗ್ಯಕರ ಅಡಿಕೆ ಗೊನೆ (ಯಾವುದೇ ರೋಗವಿಲ್ಲ)",
                "symptoms": "ಏಕರೂಪದ ಹಸಿರು ಬಣ್ಣದ ಕಾಯಿಗಳ ಬೆಳವಣಿಗೆ, ಯಾವುದೇ ಕಪ್ಪು ಚುಕ್ಕೆ, ಕೊಳೆತ ಅಥವಾ ಶಿಲೀಂಧ್ರದ ಲಕ್ಷಣಗಳಿಲ್ಲ.",
                "chemical": {
                    "title": "ಮುನ್ನೆಚ್ಚರಿಕಾ ರಕ್ಷಣೆ (Prophylactic Care)",
                    "steps": [
                        "ಆರೋಗ್ಯಕರ ಗೊನೆಗಳಿಗೆ ಯಾವುದೇ ಕೀಟನಾಶಕ ಸಿಂಪಡಣೆ ಅಗತ್ಯವಿಲ್ಲ.",
                        "ಮುಂಗಾರು ಮಳೆ ಆರಂಭವಾಗುವ ಮುನ್ನ ಮುನ್ನೆಚ್ಚರಿಕೆಯಾಗಿ 1% ಬೋರ್ಡೋ ಮಿಶ್ರಣ ಸಿಂಪಡಿಸಿ.",
                    ],
                },
                "cultural": {
                    "title": "ಗೊನೆ ನಿರ್ವಹಣೆ (Bunch Maintenance)",
                    "steps": [
                        "ಭಾರವಾದ ಗೊನೆಗಳು ಮುರಿಯದಂತೆ ಆಸರೆ ಕಟ್ಟಿ ಅಥವಾ ತೂಗು ಕಟ್ಟಿ.",
                        "ಮಲೆನಾಡು ಹಾಗೂ ಅಧಿಕ ಮಳೆಯಾಗುವ ಪ್ರದೇಶಗಳಲ್ಲಿ ಮಳೆಗಾಲದಲ್ಲಿ ಗೊನೆಗಳಿಗೆ ಪಾಲಿಥೀನ್ ಕವರ್ ಕಟ್ಟಿ.",
                    ],
                },
                "fertilizer": {
                    "title": "ಅಧಿಕ ಇಳುವರಿಗಾಗಿ ಪೋಷಕಾಂಶ (Fertilizer Schedule)",
                    "steps": [
                        "ಶಿಫಾರಸು ಮಾಡಿದ NPK: 100 ಗ್ರಾಂ N : 40 ಗ್ರಾಂ P₂O₅ : 140 ಗ್ರಾಂ K₂O ವಾರ್ಷಿಕ ನೀಡಿ.",
                        "ಪ್ರತಿ ಮರಕ್ಕೆ 12 ಕೆಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಮತ್ತು 25 ಗ್ರಾಂ ಬೋರಾಕ್ಸ್ ಮೈಕ್ರೋನ್ಯೂಟ್ರಿಯೆಂಟ್ ನೀಡಿ.",
                    ],
                },
            }
        },
    },
    # ── Healthy Trunk / Palm Foot ─────────────────────────────────────────────
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
        "translations": {
            "kn": {
                "common_name": "ಆರೋಗ್ಯಕರ ಕಾಂಡ / ಬುಡ (Healthy Trunk)",
                "disease_name": "ಆರೋಗ್ಯಕರ ಕಾಂಡ (ಯಾವುದೇ ರೋಗವಿಲ್ಲ)",
                "symptoms": "ಗಟ್ಟಿಯಾದ ನಯವಾದ ತೊಗಟೆ, ಯಾವುದೇ ರಸ ಜಿನುಗುವಿಕೆ, ಸೀಳು ಅಥವಾ ಅಣಬೆ ಬೆಳೆವಣಿಗೆಗಳಿಲ್ಲ.",
                "chemical": {
                    "title": "ಕಾಂಡದ ಮುನ್ನೆಚ್ಚರಿಕೆ (Prophylactic Care)",
                    "steps": [
                        "ಬಿಸಿಲಿನ ತಾಪ ಮತ್ತು ಹುಳುಗಳ ಬಾಧೆ ತಡೆಯಲು ವರ್ಷಕ್ಕೊಮ್ಮೆ ಕಾಂಡದ 1.5 ಮೀಟರ್ ಎತ್ತರದವರೆಗೆ ಸುಣ್ಣದ ಲೇಪನ ಮಾಡಿ.",
                        "ಆರೋಗ್ಯಕರ ಕಾಂಡಕ್ಕೆ ಯಾವುದೇ ಶಿಲೀಂಧ್ರನಾಶಕದ ಅಗತ್ಯವಿಲ್ಲ.",
                    ],
                },
                "cultural": {
                    "title": "ಕಾಂಡ ಸಂರಕ್ಷಣೆ (Trunk Maintenance)",
                    "steps": [
                        "ಅಡಿಕೆ ಕೊಯ್ಯುವಾಗ ಕಾಂಡಕ್ಕೆ ಕಬ್ಬಿಣದ ಕೊಂಡಿಗಳಿಂದ ಗಾಯವಾಗದಂತೆ ಎಚ್ಚರವಹಿಸಿ.",
                        "ಮರದ ಬುಡದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಸ್ವಚ್ಛವಾದ ಬಸಿಗಾಲುವೆ ಕಾಪಾಡಿ.",
                        "ಬುಡಕ್ಕೆ ಅಂಟಿರುವ ಪಾಚಿ, ಪರಾವಲಂಬಿ ಸಸ್ಯಗಳನ್ನು ತೆಗೆದು ಸ್ವಚ್ಛವಾಗಿಡಿ.",
                    ],
                },
                "fertilizer": {
                    "title": "ಬುಡದ ಪೋಷಕಾಂಶ ನಿರ್ವಹಣೆ (Fertilizer Schedule)",
                    "steps": [
                        "ಬುಡದಿಂದ 1 ಮೀಟರ್ ದೂರದಲ್ಲಿ ವೃತ್ತಾಕಾರದ ಪಾತಿಯಲ್ಲಿ 12 ಕೆಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಹಾಕಿ.",
                        "ವಾರ್ಷಿಕ NPK ಸಮತೋಲಿತ ಪ್ರಮಾಣದಲ್ಲಿ ಒದಗಿಸಿ.",
                    ],
                },
            }
        },
    },
    # ── Non-Arecanut / Invalid Object (OOD Rejection) ────────────────────────
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
        "translations": {
            "kn": {
                "common_name": "ಅಡಿಕೆಯೇತರ ಚಿತ್ರ / ಅಮಾನ್ಯ ವಿಷಯ (Non-Arecanut Image)",
                "disease_name": "ಅಡಿಕೆ ಮರದ ಚಿತ್ರವಲ್ಲ (ಅಮಾನ್ಯ ವಿಷಯ)",
                "symptoms": "ಅಪ್‌ಲೋಡ್ ಮಾಡಲಾದ ಚಿತ್ರದಲ್ಲಿ ಅಡಿಕೆ ಕಾಯಿ, ಎಲೆ, ಗರಿ ಅಥವಾ ಕಾಂಡದ ಭಾಗಗಳು ಪತ್ತೆಯಾಗಿಲ್ಲ.",
                "chemical": {
                    "title": "ಯಾವುದೇ ಚಿಕಿತ್ಸೆ ಅನ್ವಯಿಸುವುದಿಲ್ಲ",
                    "steps": [
                        "ಅಡಿಕೆಯೇತರ ಚಿತ್ರಗಳಿಗೆ ಯಾವುದೇ ಕೃಷಿ ರಾಸಾಯನಿಕ ಸಿಂಪಡಣೆ ಅನ್ವಯಿಸುವುದಿಲ್ಲ.",
                    ],
                },
                "cultural": {
                    "title": "ಛಾಯಾಚಿತ್ರ ಸೆರೆಹಿಡಿಯುವ ಮಾರ್ಗದರ್ಶನ",
                    "steps": [
                        "ದಯವಿಟ್ಟು ಅಡಿಕೆ ಮರದ ಕಾಯಿಗಳ ಗೊನೆ, ಎಲೆ ಅಥವಾ ಕಾಂಡದ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಸೆರೆಹಿಡಿಯಿರಿ.",
                        "ಮನೆಯ ವಸ್ತುಗಳು, ಮುಖಗಳು, ವಾಹನಗಳು ಅಥವಾ ಇತರೆ ಗಿಡಮರಗಳ ಫೋಟೋಗಳನ್ನು ತಪ್ಪಿಸಿ.",
                        "ಸಾಕಷ್ಟು ನೈಸರ್ಗಿಕ ಬೆಳಕಿನಲ್ಲಿ ಸ್ಪಷ್ಟವಾಗಿ ಫೋಕಸ್ ಮಾಡಿ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
                    ],
                },
                "fertilizer": {
                    "title": "ಯಾವುದೇ ಗೊಬ್ಬರ ಅನ್ವಯಿಸುವುದಿಲ್ಲ",
                    "steps": [
                        "ಗೊಬ್ಬರದ ವೇಳಾಪಟ್ಟಿಯು ಕೇವಲ ಅಡಿಕೆ ತೋಟದ ಮರಗಳಿಗೆ ಮಾತ್ರ ಅನ್ವಯಿಸುತ್ತದೆ.",
                    ],
                },
            }
        },
    },
}

# ── Dynamic Canonical Aliases ────────────────────────────────────────────────
_RECOMMENDATIONS["non_areca"] = _RECOMMENDATIONS["non_areca"]
_RECOMMENDATIONS["invalid"] = _RECOMMENDATIONS["non_areca"]
_RECOMMENDATIONS["out_of_distribution"] = _RECOMMENDATIONS["non_areca"]
_RECOMMENDATIONS["bud_borer"] = _RECOMMENDATIONS["Bud borer"]
_RECOMMENDATIONS["stem_bleeding"] = _RECOMMENDATIONS["stem cracking"]
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
    Includes English and Kannada (translations.kn) protocols.
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

    # Format text summaries for backward compatibility
    res = {
        **data,
        "chemical_treatment": "\n".join(data["chemical"]["steps"]),
        "cultural_measures": "\n".join(data["cultural"]["steps"]),
        "fertilizer_plan": "\n".join(data["fertilizer"]["steps"]),
    }

    # ICAR-CPCRI Weather & Spray Application Protocol (Monsoon Rain Protection)
    res["weather_advisory"] = {
        "title": "Weather & Spray Application Advisory",
        "warning": "Do not spray 1% Bordeaux mixture if rainfall is expected within 24 hours (copper washes off into plantation soil, wasting treatment). During monsoon breaks, mix with sticker/adjuvant (rosin soap @ 100g / 100L) or use systemic fungicide (Metalaxyl-Mancozeb 2g/L).",
        "translations": {
            "kn": {
                "title": "ಹವಾಮಾನ ಮತ್ತು ಸಿಂಪಡಣೆ ಎಚ್ಚರಿಕೆ (Weather Advisory)",
                "warning": "ಮುಂದಿನ 24 ಗಂಟೆಗಳಲ್ಲಿ ಮಳೆಯಾಗುವ ಸಾಧ್ಯತೆಯಿದ್ದರೆ 1% ಬೋರ್ಡೋ ಮಿಶ್ರಣ ಸಿಂಪಡಿಸಬೇಡಿ (ಮಳೆಗೆ ತೊಳೆದು ವ್ಯರ್ಥವಾಗುತ್ತದೆ). ಮಳೆಗಾಲದ ಬಿಡುವಿನಲ್ಲಿ ಸಿಂಪಡಿಸುವಾಗ ಅಂಟು ದ್ರಾವಣವನ್ನು (ರೋಸಿನ್ ಸೋಪ್ 100 ಗ್ರಾಂ/100 ಲೀ) ಕಡ್ಡಾಯವಾಗಿ ಬೆರೆಸಿ ಅಥವಾ ಮೆಟಲಾಕ್ಸಿಲ್-ಮ್ಯಾಂಕೋಜೆಬ್ ಬಳಸಿ.",
            }
        }
    }

    # Format Kannada text summaries if translations exist
    if "translations" in data and "kn" in data["translations"]:
        kn_data = data["translations"]["kn"]
        if "chemical" in kn_data and "steps" in kn_data["chemical"]:
            kn_data["chemical_treatment"] = "\n".join(kn_data["chemical"]["steps"])
        if "cultural" in kn_data and "steps" in kn_data["cultural"]:
            kn_data["cultural_measures"] = "\n".join(kn_data["cultural"]["steps"])
        if "fertilizer" in kn_data and "steps" in kn_data["fertilizer"]:
            kn_data["fertilizer_plan"] = "\n".join(kn_data["fertilizer"]["steps"])
        res["translations"] = data["translations"]

    return res
