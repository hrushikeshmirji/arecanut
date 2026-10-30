import React, { useState, useEffect, useMemo } from "react"
import {
  X,
  ShieldCheck,
  Calendar,
  Sprout,
  CheckCircle2,
  Clock,
  Droplets,
  AlertCircle,
  FileText,
  User,
  Layers,
} from "lucide-react"
import { ScanItem } from "../contexts/ScanHistoryContext"

export interface MarkTreatmentModalProps {
  isOpen: boolean
  onClose: () => void
  scan: ScanItem | null
  onConfirm: (details: {
    treatmentType: "chemical" | "organic"
    chemicalUsed: string
    notes?: string
    blockId?: string
    followUpDate: string
  }) => void
}

const DEFAULT_RECOMMENDATIONS: Record<string, { chemical: string; organic: string }> = {
  koleroga: {
    chemical: "1% Bordeaux Mixture + Rosin-Soda Sticker",
    organic: "Trichoderma viride + Cold-Pressed Neem Oil (5ml/L)",
  },
  "fruit rot": {
    chemical: "1% Bordeaux Mixture + Rosin-Soda Sticker",
    organic: "Trichoderma viride + Cold-Pressed Neem Oil (5ml/L)",
  },
  anthracnose: {
    chemical: "Mancozeb 75% WP (2g/L) / Copper Oxychloride (2.5g/L)",
    organic: "Pseudomonas fluorescens (10g/L) + NSKE 5%",
  },
  "bud borer": {
    chemical: "Chlorpyrifos 20 EC (2ml/L) / Cartap 50 SP",
    organic: "Beauveria bassiana (10g/L) + Neem cake crown dusting",
  },
  "nut cracking": {
    chemical: "Borax (25g/palm) + MOP Potash (200g/palm) + Solubor foliar",
    organic: "Wood ash (2kg) + Vermicompost + Dry leaf mulching",
  },
  "yellow leaf": {
    chemical: "Imidacloprid 17.8 SL (0.5ml/L) + ZnSO₄ + MgSO₄ + Borax",
    organic: "AMF Mycorrhiza (100g/palm) + Neem oil vector spray",
  },
  "sooty mold": {
    chemical: "Dimethoate 30 EC (1.7ml/L) followed by 2% Boiled Starch",
    organic: "Fish Oil Rosin Soap (FORS 20g/L) wash",
  },
  "stem bleeding": {
    chemical: "Bark excision + Calixin 5% paste + Coal tar seal",
    organic: "Trichoderma viride in fermented cow dung slurry",
  },
  "leaf spot": {
    chemical: "Hexaconazole 5 SC (1ml/L) / Saaf (2g/L)",
    organic: "Pseudomonas fluorescens (10g/L) foliar spray",
  },
}

function getRecommendationForDisease(disease: string) {
  const d = disease.toLowerCase()
  for (const [key, val] of Object.entries(DEFAULT_RECOMMENDATIONS)) {
    if (d.includes(key)) return val
  }
  return {
    chemical: "ICAR-CPCRI Standard Agronomic Treatment",
    organic: "Certified Bio-Fungicide & Neem Formulation",
  }
}

export default function MarkTreatmentModal({
  isOpen,
  onClose,
  scan,
  onConfirm,
}: MarkTreatmentModalProps) {
  const [treatmentType, setTreatmentType] = useState<"chemical" | "organic">("chemical")
  const [chemicalUsed, setChemicalUsed] = useState("")
  const [notes, setNotes] = useState("")
  const [applicator, setApplicator] = useState("Manual Climber / Sprayer")

  const rec = useMemo(() => {
    return scan ? getRecommendationForDisease(scan.disease) : { chemical: "", organic: "" }
  }, [scan])

  useEffect(() => {
    if (scan) {
      setChemicalUsed(treatmentType === "chemical" ? rec.chemical : rec.organic)
    }
  }, [scan, treatmentType, rec])

  if (!isOpen || !scan) return null

  // 14 days follow-up calculation
  const now = new Date()
  const followUpDateObj = new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000)
  const followUpFormatted = followUpDateObj.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })
  const todayFormatted = now.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onConfirm({
      treatmentType,
      chemicalUsed: chemicalUsed || (treatmentType === "chemical" ? rec.chemical : rec.organic),
      notes: notes ? `${notes} (Applicator: ${applicator})` : `Applicator: ${applicator}`,
      blockId: scan.location,
      followUpDate: followUpFormatted,
    })
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/60 backdrop-blur-sm overflow-y-auto animate-in fade-in duration-150">
      <div className="relative w-full max-w-lg bg-card border border-border rounded-2xl shadow-2xl overflow-hidden my-auto">
        {/* Header */}
        <div className="px-6 py-4 border-b border-border bg-muted/20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/25 flex items-center justify-center text-primary">
              <ShieldCheck size={20} />
            </div>
            <div>
              <h3 className="font-bold text-sm sm:text-base text-foreground">
                Log Treatment & Recovery Schedule
              </h3>
              <p className="text-xs text-muted-foreground">
                ICAR-CPCRI 14-Day Re-Inspection Protocol
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
          {/* Target Specimen Summary Box */}
          <div className="p-3.5 rounded-xl bg-muted/30 border border-border flex items-center justify-between gap-3">
            <div>
              <div className="text-[11px] text-muted-foreground font-semibold uppercase tracking-wider">
                Diagnosed Target
              </div>
              <div className="font-bold text-foreground text-sm mt-0.5">{scan.disease}</div>
              <div className="text-[11px] text-muted-foreground">
                Location: <strong className="text-foreground">{scan.location}</strong> · Scanned on {scan.date}
              </div>
            </div>
            <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20 shrink-0">
              {scan.severity}
            </span>
          </div>

          {/* Treatment Formulation Type */}
          <div>
            <label className="block text-xs font-bold text-foreground mb-1.5">
              Applied Treatment Formulation
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setTreatmentType("chemical")}
                className={`py-2 px-3 rounded-xl border text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                  treatmentType === "chemical"
                    ? "bg-primary text-primary-foreground border-primary"
                    : "bg-background text-muted-foreground border-border hover:bg-muted/40"
                }`}
              >
                <ShieldCheck size={14} />
                <span>Chemical Fungicide / Spray</span>
              </button>
              <button
                type="button"
                onClick={() => setTreatmentType("organic")}
                className={`py-2 px-3 rounded-xl border text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                  treatmentType === "organic"
                    ? "bg-emerald-700 text-white border-emerald-700"
                    : "bg-background text-muted-foreground border-border hover:bg-muted/40"
                }`}
              >
                <Sprout size={14} />
                <span>Certified Bio-Organic</span>
              </button>
            </div>
          </div>

          {/* Chemical/Bio Active Name */}
          <div>
            <label className="block text-xs font-bold text-foreground mb-1">
              Active Chemical / Bio-Formulation Used:
            </label>
            <input
              type="text"
              required
              value={chemicalUsed}
              onChange={(e) => setChemicalUsed(e.target.value)}
              placeholder="e.g. 1% Bordeaux Mixture + Rosin sticker"
              className="w-full px-3 py-2 rounded-xl bg-background border border-border text-foreground font-semibold text-xs focus:ring-2 focus:ring-primary/40 focus:outline-none"
            />
          </div>

          {/* 14-Day Calendar Follow-up Banner */}
          <div className="p-3.5 rounded-xl border border-primary/30 bg-primary/5 space-y-2">
            <div className="flex items-center gap-2 font-bold text-primary text-xs">
              <Calendar size={15} />
              <span>14-Day Epidemiological Recovery Window</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px] pt-1">
              <div className="p-2 rounded-lg bg-card border border-border">
                <span className="text-muted-foreground block text-[10px]">Treatment Logged Date:</span>
                <span className="font-bold text-foreground">{todayFormatted}</span>
              </div>
              <div className="p-2 rounded-lg bg-card border border-primary/40 text-primary">
                <span className="text-muted-foreground block text-[10px]">Next Re-Inspection Due:</span>
                <span className="font-extrabold font-mono text-xs">{followUpFormatted}</span>
              </div>
            </div>
            <p className="text-[11px] text-muted-foreground leading-relaxed pt-1">
              An automated high-priority reminder will be placed in your notification feed on{" "}
              <strong>{followUpFormatted}</strong> to verify lesion arrest and remission.
            </p>
          </div>

          {/* Applicator Details */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-muted-foreground mb-1">
                Applicator / Climber:
              </label>
              <input
                type="text"
                value={applicator}
                onChange={(e) => setApplicator(e.target.value)}
                placeholder="Name or team"
                className="w-full px-3 py-1.5 rounded-lg bg-background border border-border text-foreground text-xs focus:ring-1 focus:ring-primary/40 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-muted-foreground mb-1">
                Field Observation Notes:
              </label>
              <input
                type="text"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g. 100% canopy drenched"
                className="w-full px-3 py-1.5 rounded-lg bg-background border border-border text-foreground text-xs focus:ring-1 focus:ring-primary/40 focus:outline-none"
              />
            </div>
          </div>

          {/* GIS Sync Notice */}
          <div className="text-[11px] text-muted-foreground flex items-center gap-1.5 bg-muted/20 p-2 rounded-lg border border-border">
            <CheckCircle2 size={13} className="text-emerald-600 shrink-0" />
            <span>
              GIS Block <strong>{scan.location}</strong> will be upgraded to <strong>"Under Recovery"</strong>.
            </span>
          </div>

          {/* Footer Buttons */}
          <div className="pt-2 flex items-center justify-end gap-2 border-t border-border">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-2 rounded-xl border border-border bg-card text-foreground font-semibold hover:bg-muted/40 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-primary text-primary-foreground font-bold hover:opacity-90 flex items-center gap-1.5 shadow-sm transition-opacity"
            >
              <CheckCircle2 size={14} />
              <span>Confirm & Schedule Follow-Up</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
