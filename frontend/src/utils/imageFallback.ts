export const FALLBACK_IMAGE_DATA_URI =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300' viewBox='0 0 400 300'%3E%3Crect width='400' height='300' fill='%231e293b'/%3E%3Cpath d='M200,60 C250,120 280,200 200,260 C120,200 150,120 200,60 Z' fill='%2310b981' opacity='0.7'/%3E%3Ctext x='200' y='280' font-family='sans-serif' font-size='14' fill='%2394a3b8' text-anchor='middle'%3EArecaVision AI%3C/text%3E%3C/svg%3E"

export const DISEASE_LOCAL_SAMPLE_MAP: Record<string, string> = {
  koleroga: "/samples/sample_koleroga.jpg",
  "fruit rot": "/samples/sample_koleroga.jpg",
  mahali: "/samples/sample_koleroga.jpg",
  anthracnose: "/samples/sample_anthracnose.jpg",
  "leaf spot": "/samples/sample_leaf_spot.jpg",
  leafspotcomplex: "/samples/sample_leaf_spot.jpg",
  "yellow leaf": "/samples/sample_yellow_leaf.jpg",
  "stem bleeding": "/samples/sample_stem_bleeding.jpg",
  "stem cracking": "/samples/sample_stem_cracking.jpg",
  "bud borer": "/samples/sample_bud_borer.jpg",
  "nut cracking": "/samples/sample_nut_cracking.jpg",
  "sooty mold": "/samples/sample_sooty_mold.jpg",
  phytoplasma: "/samples/sample_phytoplasma.jpg",
  "root wilt": "/samples/sample_phytoplasma.jpg",
  healthy: "/samples/sample_healthy.jpg",
}

export function getSampleImageForDisease(disease?: string, currentUrl?: string): string {
  if (currentUrl?.trim()) {
    if (currentUrl.startsWith("/samples/")) return currentUrl
    if (/^https?:\/\//i.test(currentUrl)) return currentUrl
    if (currentUrl.startsWith("/uploads/")) {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"
      return new URL(currentUrl, apiBaseUrl).toString()
    }
  }
  const query = (disease || "").toLowerCase()
  for (const [key, path] of Object.entries(DISEASE_LOCAL_SAMPLE_MAP)) {
    if (query.includes(key)) {
      return path
    }
  }
  return "/samples/sample_leaf_spot.jpg"
}

export function handleImageError(e: React.SyntheticEvent<HTMLImageElement>): void {
  const target = e.currentTarget
  if (target.src !== FALLBACK_IMAGE_DATA_URI) {
    target.src = FALLBACK_IMAGE_DATA_URI
  }
}

export interface SpecimenLocalizationItem {
  title: Record<"en" | "kn" | "hi", string>
  sublabel: Record<"en" | "kn" | "hi", string>
  organ: Record<"en" | "kn" | "hi", string>
  severity: Record<"en" | "kn" | "hi", string>
  fallbackImage: string
}

export const SPECIMEN_METADATA_I18N: Record<string, SpecimenLocalizationItem> = {
  fruit_rot: {
    title: {
      en: "Fruit Rot (Koleroga)",
      kn: "ಕೊಳೆರೋಗ (ಮಹಾಲಿ)",
      hi: "फल सड़न (कोलेरोगा)",
    },
    sublabel: {
      en: "Phytophthora meadii fungal infection",
      kn: "ಫೈಟೊಪ್ಥೊರಾ ಶಿಲೀಂಧ್ರ ಸೋಂಕು",
      hi: "फाइटोफ्थोरा कवक संक्रमण",
    },
    organ: {
      en: "Nut Cluster",
      kn: "ಕಾಯಿ ಗೊಂಚಲು",
      hi: "फल गुच्छा",
    },
    severity: {
      en: "Critical",
      kn: "ತೀವ್ರ",
      hi: "गंभीर",
    },
    fallbackImage: "/samples/sample_koleroga.jpg",
  },
  bud_borer: {
    title: {
      en: "Bud Borer Infestation",
      kn: "ಸುಳಿ ಕೊಳೆ ರೋಗ",
      hi: "कली छेदक कीट",
    },
    sublabel: {
      en: "Crown spindle caterpillar boring",
      kn: "ಮರದ ಸುಳಿಯ ಹುಳು ಹಾನಿ",
      hi: "शीर्ष कली कीट क्षति",
    },
    organ: {
      en: "Crown Spindle",
      kn: "ಮರದ ಸುಳಿ",
      hi: "शीर्ष कली",
    },
    severity: {
      en: "Critical",
      kn: "ತೀವ್ರ",
      hi: "गंभीर",
    },
    fallbackImage: "/samples/sample_bud_borer.jpg",
  },
  yellow_leaf: {
    title: {
      en: "Yellow Leaf Disease",
      kn: "ಹಳದಿ ಎಲೆ ರೋಗ",
      hi: "पीली पत्ती रोग",
    },
    sublabel: {
      en: "Phytoplasma chlorosis complex",
      kn: "ಫೈಟೋಪ್ಲಾಸ್ಮಾ ಹಳದಿ ರೋಗ",
      hi: "फाइटोप्लाज्मा क्लोरोसिस",
    },
    organ: {
      en: "Fronds / Leaf",
      kn: "ಗರಿ / ಎಲೆಗಳು",
      hi: "पत्ते / शाखा",
    },
    severity: {
      en: "Severe",
      kn: "ಹೆಚ್ಚು",
      hi: "गंभीर",
    },
    fallbackImage: "/samples/sample_yellow_leaf.jpg",
  },
  stem_bleeding: {
    title: {
      en: "Stem Bleeding Disease",
      kn: "ಕಾಂಡ ಸೋರುವಿಕೆ ರೋಗ",
      hi: "तना स्राव रोग",
    },
    sublabel: {
      en: "Thielaviopsis paradoxa dark exudate",
      kn: "ಕಾಂಡದಿಂದ ಕಂದು ದ್ರವ ಸೋರುವಿಕೆ",
      hi: "तने से गहरा रिसाव",
    },
    organ: {
      en: "Trunk Bark",
      kn: "ಕಾಂಡದ ತೊಗಟೆ",
      hi: "तने की छाल",
    },
    severity: {
      en: "Severe",
      kn: "ಹೆಚ್ಚು",
      hi: "गंभीर",
    },
    fallbackImage: "/samples/sample_stem_bleeding.jpg",
  },
  stem_cracking: {
    title: {
      en: "Stem Cracking Disorder",
      kn: "ಕಾಂಡ ಬಿರುಕು ತೊಂದರೆ",
      hi: "तना विदारण / दरार",
    },
    sublabel: {
      en: "Physiological moisture expansion",
      kn: "ತೇವಾಂಶ ವ್ಯತ್ಯಾಸದಿಂದ ಉಂಟಾದ ಬಿರುಕು",
      hi: "नमी असंतुलन से दरार",
    },
    organ: {
      en: "Basal Trunk",
      kn: "ಕೆಳ ಕಾಂಡದ ಭಾಗ",
      hi: "निचला तना",
    },
    severity: {
      en: "Moderate",
      kn: "ಮಧ್ಯಮ",
      hi: "मध्यम",
    },
    fallbackImage: "/samples/sample_stem_cracking.jpg",
  },
  healthy_nut: {
    title: {
      en: "Healthy Areca Nut",
      kn: "ಆರೋಗ್ಯಕರ ಅಡಿಕೆ ಕಾಯಿ",
      hi: "स्वस्थ सुपारी फल",
    },
    sublabel: {
      en: "Uniform green development",
      kn: "ಸಂಪೂರ್ಣ ಆರೋಗ್ಯಕರ ಕಾಯಿ ಗೊಂಚಲು",
      hi: "उत्कृष्ट स्वास्थ्य और विकास",
    },
    organ: {
      en: "Healthy Nut Bunch",
      kn: "ಆರೋಗ್ಯಕರ ಕಾಯಿ ಗೊಂಚಲು",
      hi: "स्वस्थ फल गुच्छा",
    },
    severity: {
      en: "Healthy",
      kn: "ಆರೋಗ್ಯಕರ",
      hi: "स्वस्थ",
    },
    fallbackImage: "/samples/sample_healthy.jpg",
  },
  healthy_leaf: {
    title: {
      en: "Healthy Palm Canopy",
      kn: "ಆರೋಗ್ಯಕರ ಅಡಿಕೆ ಗರಿ",
      hi: "स्वस्थ ताड़ की छतरी",
    },
    sublabel: {
      en: "Deep green photosynthetic vigor",
      kn: "ಹಸಿರಾದ ಗರಿಗಳು ಮತ್ತು ಉತ್ತಮ ಬೆಳವಣಿಗೆ",
      hi: "हरी-भरी पत्तियाँ एवं विकास",
    },
    organ: {
      en: "Healthy Canopy",
      kn: "ಹಸಿರು ಗರಿಗಳು",
      hi: "हरी छतरी",
    },
    severity: {
      en: "Healthy",
      kn: "ಆರೋಗ್ಯಕರ",
      hi: "स्वस्थ",
    },
    fallbackImage: "/samples/sample_healthy.jpg",
  },
  non_areca: {
    title: {
      en: "Non-Arecanut Gatekeeper",
      kn: "ಅಡಿಕೆಯೇತರ ಸಸ್ಯ (ಪರೀಕ್ಷೆ)",
      hi: "गैर-सुपारी पौधा (गेटकीपर)",
    },
    sublabel: {
      en: "Botanical OOD verification test",
      kn: "ಅಡಿಕೆಯೇತರ ಸಸ್ಯದ ಪರಿಶೀಲನೆ",
      hi: "वानस्पतिक सत्यापन परीक्षण",
    },
    organ: {
      en: "Gatekeeper Test",
      kn: "ಗೇಟ್‌ಕೀಪರ್ ಪರೀಕ್ಷೆ",
      hi: "गेटकीपर परीक्षण",
    },
    severity: {
      en: "Gatekeeper",
      kn: "ಪರೀಕ್ಷೆ",
      hi: "परीक्षण",
    },
    fallbackImage: "/samples/sample_anthracnose.jpg",
  },
}

// Backwards-compatible shim
export const SPECIMEN_METADATA: Record<string, { kannada: string; organ: string; fallbackImage: string }> = Object.fromEntries(
  Object.entries(SPECIMEN_METADATA_I18N).map(([k, v]) => [
    k,
    { kannada: v.title.kn, organ: v.organ.en, fallbackImage: v.fallbackImage },
  ])
)

export function resolveSpecimenImageUrl(specimenId: string, previewUrl?: string): string {
  if (previewUrl && (previewUrl.startsWith("http://") || previewUrl.startsWith("https://") || previewUrl.startsWith("blob:") || previewUrl.startsWith("data:"))) {
    return previewUrl
  }

  if (previewUrl && previewUrl.startsWith("/api/")) {
    const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"
    const backendOrigin = apiBase.replace(/\/api\/v1\/?$/, "")
    return `${backendOrigin}${previewUrl}`
  }

  const meta = SPECIMEN_METADATA_I18N[specimenId]
  if (meta) {
    return meta.fallbackImage
  }

  return previewUrl || "/samples/sample_leaf_spot.jpg"
}


export function formatDiseaseName(raw?: string): string {
  if (!raw) return 'Healthy Palm'
  const lower = raw.toLowerCase()
  if (lower.includes('koleroga') || lower.includes('fruit_rot') || lower.includes('fruit rot') || lower.includes('mahali')) {
    return 'Fruit Rot (Koleroga)'
  }
  if (lower.includes('yellow_leaf') || lower.includes('yellow leaf') || lower.includes('phytoplasma')) {
    return 'Yellow Leaf Disease'
  }
  if (lower.includes('anthracnose')) {
    return 'Anthracnose'
  }
  if (lower.includes('bud_borer') || lower.includes('bud borer')) {
    return 'Bud Borer Infestation'
  }
  if (lower.includes('stem_bleeding') || lower.includes('stem bleeding')) {
    return 'Stem Bleeding Disease'
  }
  if (lower.includes('stem_cracking') || lower.includes('stem cracking')) {
    return 'Stem Cracking Disorder'
  }
  if (lower.includes('nut_cracking') || lower.includes('nut cracking')) {
    return 'Nut Cracking'
  }
  if (lower.includes('sooty_mold') || lower.includes('sooty mold')) {
    return 'Sooty Mold'
  }
  if (lower.includes('healthy')) {
    return 'Healthy Palm'
  }
  const clean = raw.trim().toLowerCase().replace(/[\s-]+/g, '_')
  
  if (SPECIMEN_METADATA_I18N[clean]) {
    return SPECIMEN_METADATA_I18N[clean].title.en
  }

  const friendlyMap: Record<string, string> = {
    fruit_rot: 'Fruit Rot / Koleroga',
    koleroga: 'Fruit Rot / Koleroga',
    mahali: 'Fruit Rot / Koleroga',
    anthracnose: 'Anthracnose',
    yellow_leaf: 'Yellow Leaf Disease',
    nut_cracking: 'Nut Cracking',
    sooty_mold: 'Sooty Mold',
    bud_borer: 'Bud Borer Infestation',
    stem_bleeding: 'Stem Bleeding',
    leaf_spot: 'Leaf Spot Complex',
    healthy: 'Healthy Palm',
  }

  if (friendlyMap[clean]) return friendlyMap[clean]

  return clean
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}
