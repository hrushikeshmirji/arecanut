import { useState, useRef, useEffect, useMemo } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import {
  ArrowLeft,
  Upload,
  Camera,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Sparkles,
  Download,
  RefreshCw,
  ShieldAlert,
  Layers,
  Eye,
  XCircle,
  Volume2,
  VolumeX,
  Calculator,
  MapPin,
  Droplets,
  Cpu,
  FlaskConical,
  Activity,
  FileText,
  ShieldCheck,
  Sprout,
  Clock,
} from "lucide-react"
import { useScanHistory, ScanItem } from "../contexts/ScanHistoryContext"
import { useNotifications } from "../contexts/NotificationContext"
import { usePlantation } from "../contexts/PlantationContext"
import { useLanguage } from "../contexts/LanguageContext"
import { useWeather } from "../contexts/WeatherContext"
import { submitAnalysis, getJobStatus, cancelJob, fetchSpecimens } from "../services/detectionService"
import { ModelInferenceResponse, FieldSpecimenItem } from "../types/api"
import LiveCameraModal from "../components/LiveCameraModal"
import XaiSplitViewer from "../components/XaiSplitViewer"
import TreatmentCalculatorModal from "../components/TreatmentCalculatorModal"
import MarkTreatmentModal from "../components/MarkTreatmentModal"
import { speakText, stopSpeech } from "../utils/textToSpeech"
import { resolveSpecimenImageUrl, SPECIMEN_METADATA_I18N, handleImageError } from "../utils/imageFallback"
import { useTheme } from "../contexts/ThemeProvider"
import type { CSSProperties } from "react"
import arecaPhoto from "../images/image.png"

const PLANTATION_BLOCKS = [
  { id: "block-a1", name: "Block A-1 (North Valley)", trees: 450, zone: "High Humidity Valley" },
  { id: "block-a2", name: "Block A-2 (North Slope)", trees: 520, zone: "Terraced Slope" },
  { id: "block-b1", name: "Block B-1 (Central Basin)", trees: 610, zone: "Well-Drained Basin" },
  { id: "block-b2", name: "Block B-2 (East Ridge)", trees: 380, zone: "Elevated Ridge" },
  { id: "block-c1", name: "Block C-1 (River Bank)", trees: 490, zone: "Riparian Belt" },
  { id: "block-d1", name: "Block D-1 (West Nursery)", trees: 310, zone: "Young Palms" },
]

interface BatchItem {
  id: string
  name: string
  previewUrl: string
  fileOrSpec: File | string
  specimenId?: string
  result?: ModelInferenceResponse
  status: "pending" | "scanning" | "done" | "error"
}

export default function Detection() {
  const { addScan, markTreated } = useScanHistory()
  const { addNotification } = useNotifications()
  const { markBlockTreated, blocks: contextBlocks } = usePlantation()
  const { language, t } = useLanguage()
  const { theme } = useTheme()
  const { weatherState } = useWeather()
  const location = useLocation()
  const navigate = useNavigate()

  // Dynamic plantation blocks synced with database & local storage
  const activeBlocks = useMemo(() => {
    if (contextBlocks && contextBlocks.length > 0) {
      return contextBlocks.map((b) => ({
        id: b.id,
        name: (b as any).name || b.id,
        trees: b.trees,
        zone: b.status || "Plantation Plot",
      }))
    }
    return PLANTATION_BLOCKS
  }, [contextBlocks])

  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentStage, setCurrentStage] = useState<string>("STAGE_1_CNN_GATEKEEPER")
  const [activeJobId, setActiveJobId] = useState<string | null>(null)
  const [diagnosis, setDiagnosis] = useState<ModelInferenceResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [cameraModalOpen, setCameraModalOpen] = useState(false)
  const [isDragging, setIsDragging] = useState(false)

  // Block Tagging & Dosage Calculator State
  const [selectedBlockId, setSelectedBlockId] = useState<string>("block-a1")
  const [palmCountToSpray, setPalmCountToSpray] = useState<number>(450)
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false)
  const [treatmentModalOpen, setTreatmentModalOpen] = useState(false)
  const [treatmentModalMode, setTreatmentModalMode] = useState<"pesticides" | "fertilizers">("pesticides")
  const [currentScanItem, setCurrentScanItem] = useState<ScanItem | null>(null)
  const [markTreatmentModalOpen, setMarkTreatmentModalOpen] = useState(false)
  const [treatmentSuccessBanner, setTreatmentSuccessBanner] = useState<string | null>(null)
  const [systemDark, setSystemDark] = useState(() => window.matchMedia("(prefers-color-scheme: dark)").matches)
  const isDark = theme === "dark" || (theme === "system" && systemDark)
  const detectionPalette = {
    "--color-background": isDark ? "#0A1104" : "#F4F3EE",
    "--color-foreground": isDark ? "#DCDCE1" : "#0A1104",
    "--color-surface": isDark ? "#141B11" : "#FCFCF9",
    "--color-card": isDark ? "#141B11" : "#FCFCF9",
    "--color-card-hover": isDark ? "#20291B" : "#E8E9E1",
    "--color-primary": isDark ? "#88A928" : "#2D4C0D",
    "--color-primary-foreground": isDark ? "#0A1104" : "#FFFFFF",
    "--color-secondary": isDark ? "#252920" : "#D3C2B9",
    "--color-accent": "#88A928",
    "--color-muted": isDark ? "#1B2318" : "#E8E9E1",
    "--color-muted-foreground": isDark ? "#A0A2A9" : "#525046",
    "--color-border": isDark ? "#303A2B" : "#D2D3CB",
    "--color-input": isDark ? "#303A2B" : "#D2D3CB",
    "--color-ring": "#88A928",
  } as CSSProperties

  // Specimen Gallery & Batch Filmstrip State
  const [specimens, setSpecimens] = useState<FieldSpecimenItem[]>([])
  const [batchQueue, setBatchQueue] = useState<BatchItem[]>([])
  const [activeBatchId, setActiveBatchId] = useState<string | null>(null)
  const ownedPreviewUrlsRef = useRef<Set<string>>(new Set())

  const fileInputRef = useRef<HTMLInputElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  const activeJobIdRef = useRef<string | null>(null)
  const lastInferenceRef = useRef<{ fileOrUrl: File | string; blockId?: string; specimenId?: string } | null>(null)

  useEffect(() => {
    if (theme !== "system") return
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    const handleChange = (event: MediaQueryListEvent) => setSystemDark(event.matches)
    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [theme])

  // Load verified field specimens on mount
  useEffect(() => {
    fetchSpecimens()
      .then((items) => setSpecimens(items))
      .catch(() => undefined)
  }, [])

  // Sync palm count when block selection changes
  useEffect(() => {
    const found = activeBlocks.find((b) => b.id === selectedBlockId)
    if (found) setPalmCountToSpray(found.trees)
  }, [selectedBlockId, activeBlocks])

  // Keep local previews alive while they're in use, then release them on reset/unmount.
  useEffect(() => () => {
    ownedPreviewUrlsRef.current.forEach((url) => URL.revokeObjectURL(url))
    ownedPreviewUrlsRef.current.clear()
  }, [])

  useEffect(() => {
    const state = location.state as { imageUrl?: string; selectedBlockId?: string } | null
    if (state?.selectedBlockId) {
      setSelectedBlockId(state.selectedBlockId)
    }
    if (state?.imageUrl) {
      setSelectedImage(state.imageUrl)
      runRealInference(state.imageUrl, state?.selectedBlockId || selectedBlockId)
    }
    return () => {
      stopSpeech()
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      if (activeJobIdRef.current) {
        cancelJob(activeJobIdRef.current).catch(() => undefined)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state])

  const runRealInference = async (
    fileOrUrl: File | string,
    blockIdOverride?: string,
    specimenIdOverride?: string
  ) => {
    lastInferenceRef.current = { fileOrUrl, blockId: blockIdOverride, specimenId: specimenIdOverride }
    if (activeJobIdRef.current) {
      cancelJob(activeJobIdRef.current).catch(() => undefined)
      activeJobIdRef.current = null
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    const currentAbort = new AbortController()
    abortControllerRef.current = currentAbort

    stopSpeech()
    setIsSpeaking(false)
    setIsAnalyzing(true)
    setProgress(15)
    setActiveJobId(null)
    setCurrentStage("STAGE_1_CNN_GATEKEEPER")
    setDiagnosis(null)
    setErrorMessage(null)
    setCurrentScanItem(null)
    setTreatmentSuccessBanner(null)

    const targetBlock = blockIdOverride || selectedBlockId

    try {
      const submitRes = await submitAnalysis(fileOrUrl, {
        signal: currentAbort.signal,
        blockId: targetBlock,
        specimenId: specimenIdOverride,
      })
      if (currentAbort.signal.aborted) return

      setActiveJobId(submitRes.job_id)
      activeJobIdRef.current = submitRes.job_id
      setProgress(30)

      let isCompleted = false
      let pollAttempts = 0

      while (!isCompleted && pollAttempts < 80) {
        await new Promise((r) => setTimeout(r, 450))
        if (currentAbort.signal.aborted) return

        pollAttempts++
        const statusRes = await getJobStatus(submitRes.job_id, { signal: currentAbort.signal })
        if (currentAbort.signal.aborted) return

        setProgress(statusRes.progressPercent)
        if (statusRes.currentStage) {
          setCurrentStage(statusRes.currentStage)
        }

        if (statusRes.status === "done" && statusRes.result) {
          isCompleted = true
          const res = statusRes.result
          setDiagnosis(res)
          setIsAnalyzing(false)
          setActiveJobId(null)
          activeJobIdRef.current = null

          // Never save mock or demo inferences to persistent scan history
          const isDemo = res.id.startsWith("demo-") || import.meta.env.VITE_DEMO_MODE === "true"
          if (res.disease !== "Not an Arecanut image" && res.stage !== "Gatekeeper Uncertain" && !isDemo) {
            const blockObj = PLANTATION_BLOCKS.find((b) => b.id === targetBlock)
            const created = addScan({
              title: `${res.disease} Inspection`,
              disease: res.disease,
              confidence: res.confidence,
              stage: res.stage,
              severity: res.severity,
              location: res.blockName || blockObj?.name || "Block A-1 (North Valley)",
              temp: weatherState.status === "POPULATED" ? `${weatherState.data.temperature}°C` : "24°C",
              weatherCondition: weatherState.status === "POPULATED" ? weatherState.data.condition : "Humid",
              recommendedActions: res.treatments.slice(0, 2),
              imageUrl: `/uploads/${res.id}.jpg`,
            })
            setCurrentScanItem(created)
          }
        } else if (statusRes.status === "failed") {
          throw new Error(statusRes.error || "Diagnosis pipeline failed")
        }
      }

      if (!isCompleted) {
        throw new Error("Analysis timed out waiting for neural worker")
      }
    } catch (err) {
      if (currentAbort.signal.aborted) return
      const msg = err instanceof Error ? err.message : "Failed to complete image diagnosis"
      setDiagnosis(null)
      setErrorMessage(msg)
      setIsAnalyzing(false)
      setActiveJobId(null)
      activeJobIdRef.current = null
    }
  }

  const handleCancelJob = async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    if (activeJobId) {
      await cancelJob(activeJobId)
    }
    setIsAnalyzing(false)
    setActiveJobId(null)
    activeJobIdRef.current = null
    setProgress(0)
    setErrorMessage("Analysis cancelled by user.")
  }

  const handleConfirmDirectTreatment = (details: {
    treatmentType: "chemical" | "organic"
    chemicalUsed: string
    notes?: string
    blockId?: string
    followUpDate: string
  }) => {
    const targetBlock = details.blockId || selectedBlockId
    if (currentScanItem) {
      markTreated(currentScanItem.id, details)
      setCurrentScanItem((prev) =>
        prev
          ? {
              ...prev,
              treatment: {
                isTreated: true,
                treatedAt: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
                treatmentType: details.treatmentType,
                chemicalUsed: details.chemicalUsed,
                dosageNotes: details.notes,
                followUpDate: details.followUpDate,
                status: "recovering",
              },
            }
          : null
      )
    }
    markBlockTreated(targetBlock, {
      treatmentType: details.treatmentType,
      chemicalUsed: details.chemicalUsed,
      followUpDate: details.followUpDate,
    })
    addNotification({
      type: "info",
      title: `Treatment Logged: ${diagnosis?.disease || "Arecanut"}`,
      msg: `Applied ${details.chemicalUsed} at ${targetBlock}. 14-day follow-up inspection scheduled for ${details.followUpDate}.`,
      blockId: targetBlock,
    })
    setTreatmentSuccessBanner(
      `Treatment confirmed! ${details.chemicalUsed} logged for ${targetBlock}. 14-day re-inspection alert scheduled for ${details.followUpDate}.`
    )
    setMarkTreatmentModalOpen(false)
    setTimeout(() => setTreatmentSuccessBanner(null), 6000)
  }

  const validateAndLoadFiles = (fileList: FileList) => {
    const validTypes = ["image/jpeg", "image/png", "image/webp", "image/bmp"]
    const maxBytes = 10 * 1024 * 1024
    const files = Array.from(fileList)
    if (files.length === 0) return

    if (files.length > 8) {
      setErrorMessage("Choose up to 8 photos at a time.")
      return
    }
    const validFiles = files.filter((f) => {
      const extensionIsImage = /\.(jpe?g|png|webp|bmp)$/i.test(f.name)
      return (validTypes.includes(f.type) || extensionIsImage) && f.size > 0 && f.size <= maxBytes
    })
    if (validFiles.length !== files.length) {
      setErrorMessage(
        t("detect.val_invalid_format", "Some files are unsupported or over 10MB. Choose JPEG, PNG, WebP, or BMP photos under 10MB each.")
      )
      return
    }

    const newBatchItems: BatchItem[] = validFiles.slice(0, 8).map((f, idx) => {
      const previewUrl = URL.createObjectURL(f)
      ownedPreviewUrlsRef.current.add(previewUrl)
      return {
        id: `batch-${Date.now()}-${idx}`,
        name: f.name,
        previewUrl,
        fileOrSpec: f,
        status: idx === 0 ? "scanning" : "pending",
      }
    })

    const nextBatchQueue = [...newBatchItems, ...batchQueue].slice(0, 8)
    const retainedUrls = new Set(nextBatchQueue.map((item) => item.previewUrl))
    batchQueue.forEach((item) => {
      if (item.previewUrl.startsWith("blob:") && !retainedUrls.has(item.previewUrl)) {
        URL.revokeObjectURL(item.previewUrl)
        ownedPreviewUrlsRef.current.delete(item.previewUrl)
      }
    })
    setBatchQueue(nextBatchQueue)
    const first = newBatchItems[0]
    setActiveBatchId(first.id)
    setSelectedImage(first.previewUrl)
    runRealInference(first.fileOrSpec, selectedBlockId)
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndLoadFiles(e.target.files)
    }
    e.target.value = ""
  }

  const handleReset = () => {
    stopSpeech()
    setIsSpeaking(false)
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    if (activeJobIdRef.current) {
      cancelJob(activeJobIdRef.current).catch(() => undefined)
    }
    setSelectedImage(null)
    ownedPreviewUrlsRef.current.forEach((url) => URL.revokeObjectURL(url))
    ownedPreviewUrlsRef.current.clear()
    setDiagnosis(null)
    setErrorMessage(null)
    setIsAnalyzing(false)
    setActiveJobId(null)
    activeJobIdRef.current = null
    setProgress(0)
    setBatchQueue([])
    setActiveBatchId(null)
    setTreatmentSuccessBanner(null)
  }

  const handleSelectSpecimen = (spec: FieldSpecimenItem) => {
    const imageUrl = resolveSpecimenImageUrl(spec.id, spec.previewUrl)
    setSelectedImage(imageUrl)
    runRealInference(`specimen:${spec.id}`, selectedBlockId, spec.id)
  }

  // Voice Audio Briefing (EN / KN / HI)
  const handleToggleVoiceBriefing = () => {
    if (!diagnosis) return
    if (isSpeaking) {
      stopSpeech()
      setIsSpeaking(false)
      return
    }
    const morph = diagnosis.tissueMorphometrics
    const speechScript =
      diagnosis.disease === "Not an Arecanut image"
        ? `Gatekeeper alert. With ${diagnosis.confidence}% confidence, this image is not an Areca catechu specimen. ${diagnosis.description}`
        : `ArecaVision Diagnostic Report for ${diagnosis.blockName || "selected block"}. Detected condition: ${
            diagnosis.disease
          } with ${diagnosis.confidence}% confidence and ${diagnosis.severity} severity. ${
            morph ? `Healthy tissue is ${morph.healthyPct}%, lesion coverage is ${morph.lesionCoveragePct}%. ` : ""
          }Recommended action: ${diagnosis.treatments[0] || "Follow standard management."} Organic protocol: ${
            diagnosis.organicControl[0] || "Apply neem cake."
          }`

    setIsSpeaking(true)
    speakText(speechScript, language, () => setIsSpeaking(false))
  }

  // Consult AI Agronomist about this scan
  const handleConsultAiAgronomist = () => {
    if (!diagnosis) return
    const weatherNote =
      weatherState.status === "POPULATED"
        ? `Current weather in ${weatherState.data.city}: ${weatherState.data.temperature}°C, ${weatherState.data.humidity}% humidity, ${weatherState.data.riskLevel} fungal risk.`
        : ""
    const prompt = `I just scanned an arecanut specimen in ${
      diagnosis.blockName || "Block A-1"
    } (${palmCountToSpray} palms). Diagnosis: ${diagnosis.disease} (${diagnosis.confidence}% confidence, ${
      diagnosis.severity
    } severity, Lesion coverage: ${
      diagnosis.tissueMorphometrics?.lesionCoveragePct ?? 18
    }%). ${weatherNote} Please give me an immediate step-by-step spray schedule and organic + chemical dosage plan.`
    navigate("/assistant", { state: { initialPrompt: prompt } })
  }

  // Interactive Spray & Nutrition Dosage Calculations (ICAR-CPCRI Standards)
  const dosagePlan = useMemo(() => {
    const palms = Math.max(1, palmCountToSpray)
    const sprayLiters = Math.round(palms * 1.5)
    const d = diagnosis?.disease?.toLowerCase() || ""

    let planType = "fungicide"
    let title = "1% Neutral Bordeaux Mixture"
    let primaryLabel = "CuSO₄"
    let primaryVal = ((sprayLiters * 10) / 1000).toFixed(2) + " kg"
    let secondaryLabel = "Quicklime CaO"
    let secondaryVal = ((sprayLiters * 10) / 1000).toFixed(2) + " kg"
    let organicLabel = "Organic Neem (5ml/L)"
    let organicVal = ((sprayLiters * 5) / 1000).toFixed(2) + " L"
    let bioLabel = "Trichoderma Bio-Mix"
    let bioVal = ((palms * 50) / 1000).toFixed(1) + " kg"

    if (d.includes("crack") || d.includes("split")) {
      planType = "nutrition"
      title = "Boron & Potash Nutrient Correction"
      primaryLabel = "Borax (25g/palm)"
      primaryVal = ((palms * 25) / 1000).toFixed(2) + " kg"
      secondaryLabel = "MOP Potash (200g/palm)"
      secondaryVal = ((palms * 200) / 1000).toFixed(2) + " kg"
      organicLabel = "Wood Ash / Compost"
      organicVal = (palms * 2.0).toFixed(0) + " kg"
      bioLabel = "Solubor Foliar (1g/L)"
      bioVal = ((sprayLiters * 1) / 1000).toFixed(2) + " kg"
    } else if (d.includes("bud") || d.includes("borer") || d.includes("caterpillar")) {
      planType = "pesticide"
      title = "Crown Insecticide & Bio-Pesticide"
      primaryLabel = "Chlorpyrifos (2ml/L)"
      primaryVal = ((sprayLiters * 2) / 1000).toFixed(2) + " L"
      secondaryLabel = "Cartap 50 SP"
      secondaryVal = ((sprayLiters * 1.5) / 1000).toFixed(2) + " kg"
      organicLabel = "Neem Oil 10,000 ppm"
      organicVal = ((sprayLiters * 5) / 1000).toFixed(2) + " L"
      bioLabel = "Beauveria bassiana"
      bioVal = ((sprayLiters * 10) / 1000).toFixed(1) + " kg"
    } else if (d.includes("yellow") || d.includes("phytoplasma")) {
      planType = "complex"
      title = "Vector Control + Micronutrient Boost"
      primaryLabel = "Imidacloprid (0.5ml/L)"
      primaryVal = ((sprayLiters * 0.5) / 1000).toFixed(2) + " L"
      secondaryLabel = "MgSO₄ (100g/palm)"
      secondaryVal = ((palms * 100) / 1000).toFixed(1) + " kg"
      organicLabel = "ZnSO₄ (50g/palm)"
      organicVal = ((palms * 50) / 1000).toFixed(1) + " kg"
      bioLabel = "AMF Mycorrhiza"
      bioVal = ((palms * 100) / 1000).toFixed(1) + " kg"
    } else if (d.includes("anthracnose") || d.includes("spot") || d.includes("blight")) {
      planType = "fungicide"
      title = "Mancozeb 75 WP / Hexaconazole"
      primaryLabel = "Mancozeb (2g/L)"
      primaryVal = ((sprayLiters * 2) / 1000).toFixed(2) + " kg"
      secondaryLabel = "Copper Oxychloride"
      secondaryVal = ((sprayLiters * 2.5) / 1000).toFixed(2) + " kg"
      organicLabel = "Organic Neem (5ml/L)"
      organicVal = ((sprayLiters * 5) / 1000).toFixed(2) + " L"
      bioLabel = "Pseudomonas fluorescens"
      bioVal = ((sprayLiters * 10) / 1000).toFixed(1) + " kg"
    } else if (d.includes("healthy")) {
      planType = "fertilizer"
      title = "Annual Routine NPK Maintenance"
      primaryLabel = "Urea (220g/palm)"
      primaryVal = ((palms * 220) / 1000).toFixed(1) + " kg"
      secondaryLabel = "Rock Phosphate"
      secondaryVal = ((palms * 200) / 1000).toFixed(1) + " kg"
      organicLabel = "MOP Potash (235g)"
      organicVal = ((palms * 235) / 1000).toFixed(1) + " kg"
      bioLabel = "Farmyard Manure (FYM)"
      bioVal = (((palms * 12) / 1000)).toFixed(1) + " Tons"
    }

    const rosinStickerMl = Math.round(sprayLiters * 0.5)
    const highHumidityOrRain =
      weatherState.status === "POPULATED" &&
      (weatherState.data.humidity >= 82 || weatherState.data.rainfall > 0.5)

    return {
      sprayLiters,
      planType,
      title,
      primaryLabel,
      primaryVal,
      secondaryLabel,
      secondaryVal,
      organicLabel,
      organicVal,
      bioLabel,
      bioVal,
      rosinStickerMl,
      highHumidityOrRain,
    }
  }, [palmCountToSpray, diagnosis?.disease, weatherState])

  const handleDownloadSummary = () => {
    if (!diagnosis) return
    const isSynthetic = diagnosis.id.startsWith("demo-") || import.meta.env.VITE_DEMO_MODE === "true"
    const reportText = [
      "==========================================================",
      "   ARECAVISION AI 2.0 — AI SCREENING SUMMARY    ",
      "==========================================================",
      "AI-assisted screening only. Confirm findings and treatment decisions with a qualified local agronomist.",
      ...(isSynthetic ? ["DEMO RESULT — simulated data, not a real crop assessment."] : []),
      `Scan ID          : ${diagnosis.id}`,
      `Timestamp        : ${new Date(diagnosis.processedAt).toLocaleString()}`,
      `Plantation Block : ${diagnosis.blockName || selectedBlockId} (${palmCountToSpray} Palms)`,
      `AI Screening Result: ${diagnosis.disease}`,
      `Model Confidence   : ${diagnosis.confidence}%`,
      `Observed Severity  : ${diagnosis.severity}`,
      "",
      "--- NEURAL ENSEMBLE & STAGE TELEMETRY ---",
      `Stage 1 (EfficientNet-B0 Gatekeeper): ${diagnosis.modelBreakdown.cnn}% (${diagnosis.stageTimingsMs?.gatekeeperMs ?? 38} ms)`,
      `Stage 2 (YOLOv8 + LAB Saliency ROI) : ${diagnosis.modelBreakdown.yolo}% (${diagnosis.stageTimingsMs?.yoloMs ?? 94} ms)`,
      `Stage 3 (Multi-Crop ViT-B/16 TTA)   : ${diagnosis.modelBreakdown.vit}% (${diagnosis.stageTimingsMs?.vitTtaMs ?? 245} ms)`,
      `Stage 4 (12-Head Attention Rollout) : ${diagnosis.stageTimingsMs?.xaiRolloutMs ?? 24} ms`,
      `Total Pipeline Execution Latency    : ${diagnosis.stageTimingsMs?.totalMs ?? 401} ms`,
      "",
      "--- TISSUE MORPHOMETRICS (LAB COLORIMETRY) ---",
      `Healthy Photosynthetic Tissue : ${diagnosis.tissueMorphometrics?.healthyPct ?? 75}%`,
      `Chlorotic Stress Halo         : ${diagnosis.tissueMorphometrics?.chloroticPct ?? 12}%`,
      `Necrotic Lesion Core          : ${diagnosis.tissueMorphometrics?.necroticPct ?? 13}%`,
      `Total Lesion Coverage         : ${diagnosis.tissueMorphometrics?.lesionCoveragePct ?? 25}%`,
      "",
      "--- CALCULATED BLOCK DOSAGE (" + palmCountToSpray + " PALMS) ---",
      `Protocol Focus                  : ${dosagePlan.title}`,
      `Total Spray Fluid Volume        : ${dosagePlan.sprayLiters} Liters`,
      `Primary Input (${dosagePlan.primaryLabel}) : ${dosagePlan.primaryVal}`,
      `Secondary Input (${dosagePlan.secondaryLabel}) : ${dosagePlan.secondaryVal}`,
      `Organic / Cultural Component    : ${dosagePlan.organicVal} (${dosagePlan.organicLabel})`,
      `Biological Agent                : ${dosagePlan.bioVal} (${dosagePlan.bioLabel})`,
      "",
      "--- RECOMMENDED CHEMICAL & CULTURAL TREATMENTS ---",
      ...diagnosis.treatments.map((item, i) => `${i + 1}. ${item}`),
      "",
      "--- ORGANIC & BIOLOGICAL CONTROL ---",
      ...diagnosis.organicControl.map((item, i) => `${i + 1}. ${item}`),
      "==========================================================",
    ].join("\n")

    const blob = new Blob([reportText], { type: "text/plain;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = `ArecaVision_Screening_Summary_${diagnosis.disease}_${diagnosis.id}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const pipelineStages = [
    {
      key: "STAGE_1_CNN_GATEKEEPER",
      step: "01",
      title: "EfficientNet-B0 Gate",
      subtitle: "Botanical OOD Verification",
      ms: diagnosis?.stageTimingsMs?.gatekeeperMs,
      score: diagnosis ? `${diagnosis.modelBreakdown.cnn}%` : undefined,
    },
    {
      key: "STAGE_2_YOLO_LESION_ROI",
      step: "02",
      title: "YOLOv8 Candidate Detection",
      subtitle: "Candidate Region Localization (Experimental)",
      ms: diagnosis?.stageTimingsMs?.yoloMs,
      score: diagnosis ? `${diagnosis.yoloBoxes.length} Detections` : undefined,
    },
    {
      key: "STAGE_3_VIT_MULTICROP_TTA",
      step: "03",
      title: "Multi-Crop ViT-B/16 TTA",
      subtitle: "5-Crop Entropy Fusion",
      ms: diagnosis?.stageTimingsMs?.vitTtaMs,
      score: diagnosis ? `${diagnosis.modelBreakdown.vit}%` : undefined,
    },
    {
      key: "STAGE_4_XAI_ATTENTION_ROLLOUT",
      step: "04",
      title: "12-Head Rollout + Twin Sync",
      subtitle: "XAI Heatmap & SQLite Sync",
      ms: diagnosis?.stageTimingsMs?.xaiRolloutMs,
      score: diagnosis?.stageTimingsMs ? `${diagnosis.stageTimingsMs.totalMs}ms total` : undefined,
    },
  ]

  const hasActiveSession = Boolean(selectedImage || isAnalyzing || diagnosis)

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-4 text-foreground sm:p-6" style={detectionPalette}>
      {/* PERSISTENT DEMO DATA BANNER (Only when VITE_DEMO_MODE=true or demo diagnosis) */}
      {(import.meta.env.VITE_DEMO_MODE === "true" || diagnosis?.id?.startsWith("demo-")) && (
        <div className="bg-amber-500/15 border-2 border-amber-500/40 text-amber-900 dark:text-amber-100 p-3.5 rounded-2xl font-bold text-xs flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-2.5">
            <AlertTriangle size={18} className="text-amber-600 dark:text-amber-400 shrink-0" />
            <div>
              <span>DEMO DATA, NOT A REAL DIAGNOSIS</span>
              <p className="text-[11px] font-normal opacity-90">Simulated demonstration mode is active. Results are preset mock profiles and not actual model inferences.</p>
            </div>
          </div>
          <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-amber-500/20 shrink-0">Demo Mode</span>
        </div>
      )}

      {/* ============================================================
      STATE A: INITIAL STATE — SINGLE FULL-WIDTH SCAN BOX & VERIFIED SPECIMENS
      ============================================================ */}
      {!hasActiveSession ? (
        <div className="space-y-8 animate-in fade-in duration-200">
          {/* Mission Header */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 bg-card border border-border rounded-2xl p-6 shadow-xs">
            <div>
              <h1 className="text-xl sm:text-2xl font-extrabold text-foreground">
                {t("detect.title", "Arecanut Disease Diagnostics")}
              </h1>
              <p className="text-xs sm:text-sm text-muted-foreground mt-1">
                {t(
                  "detect.subtitle",
                  "Upload or scan palm leaves, nuts, or trunk photos to detect diseases and get ICAR-CPCRI management guides."
                )}
              </p>
            </div>

            {/* Target Plantation Block Selector */}
            <div className="flex items-center gap-2.5 shrink-0">
              <div className="flex items-center gap-2 bg-muted/40 border border-border rounded-xl px-3.5 py-2">
                <MapPin size={15} className="text-primary shrink-0" />
                <div className="text-xs">
                  <span className="text-muted-foreground font-medium mr-1.5">{t("detect.target_gis_block", "Target GIS Block:")}</span>
                  <select
                    value={selectedBlockId}
                    onChange={(e) => setSelectedBlockId(e.target.value)}
                    className="bg-transparent font-bold text-foreground outline-none cursor-pointer"
                  >
                    {activeBlocks.map((b) => (
                      <option key={b.id} value={b.id} className="bg-card text-foreground">
                        {b.name} ({b.trees} Palms)
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Full-Width Prominent Scan & Upload Hero Box */}
          <div
            onClick={(event) => {
              if (event.target !== fileInputRef.current) fileInputRef.current?.click()
            }}
            onDragOver={(e) => {
              e.preventDefault()
              e.stopPropagation()
              setIsDragging(true)
            }}
            onDragEnter={(e) => {
              e.preventDefault()
              e.stopPropagation()
              setIsDragging(true)
            }}
            onDragLeave={(e) => {
              e.preventDefault()
              e.stopPropagation()
              setIsDragging(false)
            }}
            onDrop={(e) => {
              e.preventDefault()
              e.stopPropagation()
              setIsDragging(false)
              if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                validateAndLoadFiles(e.dataTransfer.files)
              }
            }}
            className={`relative isolate overflow-hidden bg-card rounded-2xl border-2 border-dashed p-8 sm:p-12 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[380px] group shadow-xs ${
              isDragging
                ? "border-primary bg-primary/10 ring-4 ring-primary/20 scale-[1.01]"
                : "border-primary/40 hover:border-primary hover:bg-muted/10"
            }`}
          >
            <img src={arecaPhoto} alt="" aria-hidden="true" className="pointer-events-none absolute inset-0 z-0 h-full w-full object-cover object-center opacity-[0.10]" />
            <div className="pointer-events-none absolute inset-0 z-0 bg-gradient-to-br from-card/95 via-card/85 to-primary/10" />
            <div className="relative z-10 flex w-full flex-col items-center">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/jpeg,image/png,image/webp,image/bmp"
              className="hidden"
              onChange={handleFileUpload}
            />

            <div className="w-20 h-20 rounded-3xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-5 group-hover:scale-110 transition-transform shadow-md">
              <Upload size={38} />
            </div>

            <h2 className="text-lg sm:text-xl font-extrabold text-foreground">
              {isDragging
                ? t("detect.upload_box_title", "Drop Single or Multiple Specimens to Analyze!")
                : t("detect.upload_box_title", "Drop Areca Leaf, Nut, or Trunk Photo(s) Here")}
            </h2>
            <p className="text-xs sm:text-sm text-muted-foreground mt-2 max-w-lg">
              {t("detect.upload_box_desc", "Take or upload a clear photo of the affected plant parts. Supports up to 8 JPEG, PNG, WebP, or BMP photos (10MB each).")}
            </p>

            <div className="flex flex-wrap items-center justify-center gap-3 mt-6">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  fileInputRef.current?.click()
                }}
                className="btn-primary text-xs sm:text-sm px-5 py-2.5 shadow-sm"
              >
                <Upload size={16} /> {t("detect.browse", "Browse Files (Single / Batch)")}
              </button>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  setCameraModalOpen(true)
                }}
                className="btn-secondary text-xs sm:text-sm px-5 py-2.5 shadow-sm"
              >
                <Camera size={16} /> {t("detect.take_photo", "Take Photo with Camera")}
              </button>
            </div>

            {errorMessage && (
              <div role="alert" className="mt-4 w-full max-w-xl rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-left text-xs text-danger">
                {errorMessage}
              </div>
            )}

            {/* Farmer Photo Guidelines */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-2xl mt-8 pt-6 border-t border-border/60 text-left">
              <div className="flex items-start gap-2.5 p-2 rounded-xl bg-muted/30">
                <span className="text-base shrink-0">☀️</span>
                <div className="text-[11px] leading-tight">
                  <strong className="text-foreground block mb-0.5">{t("detect.guideline_daylight_title", "Natural Daylight")}</strong>
                  <span className="text-muted-foreground">{t("detect.guideline_daylight_desc", "Capture in clear daylight without harsh shadows.")}</span>
                </div>
              </div>
              <div className="flex items-start gap-2.5 p-2 rounded-xl bg-muted/30">
                <span className="text-base shrink-0">🔍</span>
                <div className="text-[11px] leading-tight">
                  <strong className="text-foreground block mb-0.5">{t("detect.guideline_focus_title", "Close-Up Focus")}</strong>
                  <span className="text-muted-foreground">{t("detect.guideline_focus_desc", "Focus closely on spots, lesions, or trunk cracks.")}</span>
                </div>
              </div>
              <div className="flex items-start gap-2.5 p-2 rounded-xl bg-muted/30">
                <span className="text-base shrink-0">🌴</span>
                <div className="text-[11px] leading-tight">
                  <strong className="text-foreground block mb-0.5">{t("detect.guideline_organ_title", "Any Plant Part")}</strong>
                  <span className="text-muted-foreground">{t("detect.guideline_organ_desc", "Analyzes leaves, crowns, nut bunches, & trunk bark.")}</span>
                </div>
              </div>
            </div>
            </div>
          </div>

          {/* 1-Click Verified Field Specimen Gallery */}
          <div className="bg-card border border-border rounded-2xl p-5 sm:p-6 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3.5">
              <div className="flex items-center gap-2">
                <FlaskConical size={16} className="text-primary" />
                <h3 className="text-xs sm:text-sm font-bold text-foreground">
                  {t("detect.specimens_gallery_title", "1-Click Verified Field Specimen Gallery")}
                </h3>
              </div>
              <span className="text-xs text-muted-foreground">
                {t("detect.specimens_gallery_subtitle", "Click any verified field sample below to run instant diagnostic analysis")}
              </span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-4 gap-3">
              {specimens.length === 0 && (
                <p className="col-span-full rounded-xl border border-dashed border-border px-4 py-6 text-center text-xs text-muted-foreground">
                  Sample photos are unavailable right now. You can still upload a photo or use your camera above.
                </p>
              )}
              {specimens.map((spec) => {
                const meta = SPECIMEN_METADATA_I18N[spec.id]
                const curLang = (language as "en" | "kn" | "hi") || "en"
                const itemTitle = meta?.title[curLang] || spec.title
                const itemSub = meta?.sublabel[curLang] || ""
                const itemOrgan = meta?.organ[curLang] || meta?.organ.en || ""
                const itemSeverity = meta?.severity[curLang] || spec.severity
                const imgUrl = resolveSpecimenImageUrl(spec.id, spec.previewUrl)

                return (
                  <button
                    key={spec.id}
                    type="button"
                    disabled={isAnalyzing}
                    onClick={() => handleSelectSpecimen(spec)}
                    className="group flex items-center gap-3 p-2.5 rounded-xl border border-border hover:border-primary bg-muted/20 hover:bg-primary/5 text-left transition-all disabled:opacity-50 cursor-pointer shadow-2xs"
                  >
                    <img
                      src={imgUrl}
                      alt={itemTitle}
                      onError={handleImageError}
                      className="w-12 h-12 rounded-xl object-cover shrink-0 border border-border group-hover:scale-105 transition-transform"
                    />
                    <div className="min-w-0 flex-1">
                      <div className="text-xs font-bold text-foreground truncate group-hover:text-primary">
                        {itemTitle}
                      </div>
                      {itemSub && (
                        <div className="text-[10px] text-muted-foreground truncate font-medium">
                          {itemSub}
                        </div>
                      )}
                      <div className="flex items-center gap-1.5 mt-1">
                        <span
                          className={`inline-block px-1.5 py-0.2 rounded text-[9px] font-bold ${
                            spec.severity === "Severe" || spec.severity === "Critical"
                              ? "bg-danger/15 text-danger"
                              : spec.severity === "Healthy"
                              ? "bg-primary/15 text-primary"
                              : spec.severity === "Gatekeeper" || spec.severity === "Non-Arecanut"
                              ? "bg-muted text-muted-foreground"
                              : "bg-warning/15 text-warning"
                          }`}
                        >
                          {itemSeverity}
                        </span>
                        {itemOrgan && (
                          <span className="text-[9px] text-muted-foreground truncate">
                            • {itemOrgan}
                          </span>
                        )}
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      ) : (
        /* ============================================================
        STATE B: ACTIVE DIAGNOSTIC WORKSPACE (Image Selected / Analyzing / Results)
        ============================================================ */
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Active Session Top Navigation Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-card border border-border rounded-2xl p-4 shadow-xs">
            <div className="flex items-center gap-3">
              <button
                onClick={handleReset}
                className="btn-secondary text-xs flex items-center gap-2 py-2 px-3 shadow-2xs cursor-pointer font-bold"
              >
                <ArrowLeft size={14} />
                <span>{t("detect.scan_another", "Scan Another Photo")}</span>
              </button>
              <div>
                <h2 className="text-sm sm:text-base font-extrabold text-foreground">
                  {isAnalyzing
                    ? t("detect.analyzing_specimen", "Analyzing Specimen...")
                    : diagnosis
                    ? t("detect.workspace_title", "Diagnostic Inspection Workspace")
                    : t("detect.specimen_inspection", "Specimen Inspection")}
                </h2>
                <p className="text-[11px] text-muted-foreground">
                  {diagnosis
                    ? `${t("detect.diagnosis_ready", "Diagnosis ready")} • ${diagnosis.disease}`
                    : isAnalyzing
                    ? t("detect.running_neural_analysis", "Neural ensemble processing in progress")
                    : t("detect.active_specimen_loaded", "Active specimen loaded")}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2.5">
              <div className="flex items-center gap-2 bg-muted/40 border border-border rounded-xl px-3 py-1.5 text-xs">
                <MapPin size={14} className="text-primary shrink-0" />
                <div>
                  <span className="text-muted-foreground mr-1.5">Block:</span>
                  <select
                    value={selectedBlockId}
                    onChange={(e) => setSelectedBlockId(e.target.value)}
                    className="bg-transparent font-bold text-foreground outline-none cursor-pointer"
                  >
                    {activeBlocks.map((b) => (
                      <option key={b.id} value={b.id} className="bg-card text-foreground">
                        {b.name} ({b.trees} Palms)
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* 4-Stage Neural Telemetry Bar */}
          {(isAnalyzing || (diagnosis && diagnosis.disease !== "Not an Arecanut image" && diagnosis.severity !== "Non-Arecanut")) && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {pipelineStages.map((st, idx) => {
                const stageOrder = pipelineStages.findIndex((s) => s.key === currentStage)
                const isDone = Boolean(diagnosis) || (isAnalyzing && idx < stageOrder)
                const isCurrent = isAnalyzing && idx === stageOrder

                return (
                  <div
                    key={st.key}
                    className={`rounded-xl border p-3 transition-all flex items-center justify-between ${
                      isCurrent
                        ? "bg-primary/10 border-primary ring-2 ring-primary/20"
                        : isDone
                        ? "bg-card border-primary/40"
                        : "bg-card/50 border-border opacity-60"
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div
                        className={`w-7 h-7 rounded-lg text-xs font-mono font-extrabold flex items-center justify-center shrink-0 ${
                          isCurrent
                            ? "bg-primary text-primary-foreground animate-pulse"
                            : isDone
                            ? "bg-primary/20 text-primary"
                            : "bg-muted text-muted-foreground"
                        }`}
                      >
                        {isDone ? "✓" : st.step}
                      </div>
                      <div className="min-w-0">
                        <div className="text-xs font-bold text-foreground truncate">{st.title}</div>
                        <div className="text-[10px] text-muted-foreground truncate">{st.subtitle}</div>
                      </div>
                    </div>
                    <div className="text-right shrink-0 ml-2">
                      {st.ms !== undefined && (
                        <div className="text-[11px] font-mono font-extrabold text-primary">{st.ms} ms</div>
                      )}
                      {st.score && <div className="text-[10px] font-mono text-muted-foreground">{st.score}</div>}
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {/* 2-Column Responsive Diagnostic Workspace */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* LEFT COLUMN: XAI VIEWER, BATCH FILMSTRIP, MORPHOMETRICS */}
            <div className="lg:col-span-6 space-y-4">
              <div className="bg-card rounded-2xl border border-border p-4 space-y-4 shadow-sm">
                {/* Interactive XAI Split Viewer */}
                <XaiSplitViewer
                  originalUrl={selectedImage || "/placeholder.jpg"}
                  attentionMapUrl={diagnosis?.attentionMapUrl}
                  yoloBoxes={diagnosis?.yoloBoxes || []}
                  diseaseLabel={diagnosis?.disease}
                  confidence={diagnosis?.confidence}
                />

                {/* Progress Bar during Active Inference */}
                {isAnalyzing && (
                  <div className="space-y-2 p-3 rounded-xl bg-primary/5 border border-primary/20">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-primary flex items-center gap-2">
                        <Cpu size={14} className="animate-spin" />
                        <span>
                          {currentStage.includes("STAGE_1")
                            ? t("detect.status_verifying", "Verifying leaf and palm specimen...")
                            : currentStage.includes("STAGE_2")
                            ? t("detect.status_spotting", "Spotting affected lesion zones...")
                            : currentStage.includes("STAGE_3")
                            ? t("detect.status_diagnosing", "Diagnosing disease and infection severity...")
                            : t("detect.status_generating", "Generating visual explanation and treatment plan...")}
                        </span>
                      </span>
                      <div className="flex items-center gap-3">
                        <span className="font-mono font-bold text-primary">{progress}%</span>
                        <button
                          onClick={handleCancelJob}
                          className="text-[11px] font-semibold text-danger hover:underline flex items-center gap-1"
                        >
                          <XCircle size={12} /> Cancel
                        </button>
                      </div>
                    </div>
                    <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Batch Triage Filmstrip Queue (if multiple images) */}
                {batchQueue.length > 1 && (
                  <div className="pt-2 border-t border-border">
                    <div className="text-[11px] font-bold text-muted-foreground mb-2">
                      Batch Field Triage Queue ({batchQueue.length} Specimens)
                    </div>
                    <div className="flex items-center gap-2 overflow-x-auto pb-1">
                      {batchQueue.map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => {
                            setActiveBatchId(item.id)
                            setSelectedImage(item.previewUrl)
                            runRealInference(item.fileOrSpec, selectedBlockId)
                          }}
                          className={`relative w-14 h-14 rounded-xl overflow-hidden border-2 shrink-0 transition-all ${
                            activeBatchId === item.id ? "border-primary scale-105 shadow-md" : "border-border opacity-70"
                          }`}
                        >
                          <img src={item.previewUrl} alt={item.name} className="w-full h-full object-cover" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Tri-Band LAB Colorimetry Tissue Morphometrics & Differential Spectrum */}
              {diagnosis && diagnosis.disease !== "Not an Arecanut image" && (
                <div className="bg-card rounded-2xl border border-border p-4 space-y-4 shadow-sm">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Activity size={15} className="text-primary" />
                      <h3 className="text-xs font-extrabold uppercase tracking-wider text-foreground">
                        OpenCV LAB Colorimetry Tissue Morphometrics
                      </h3>
                    </div>
                    <span className="text-xs font-mono font-bold text-danger">
                      {t("detect.lesion_area", "Lesion Area")}: {diagnosis.tissueMorphometrics?.lesionCoveragePct ?? 18.4}%
                    </span>
                  </div>

                  {/* Tri-Band Stacked Visual Bar */}
                  <div className="space-y-1.5">
                    <div className="h-3.5 w-full rounded-full overflow-hidden flex bg-muted border border-border">
                      <div
                        style={{ width: `${diagnosis.tissueMorphometrics?.healthyPct ?? 72}%` }}
                        className="bg-emerald-500 h-full transition-all"
                        title="Healthy Photosynthetic Tissue"
                      />
                      <div
                        style={{ width: `${diagnosis.tissueMorphometrics?.chloroticPct ?? 14}%` }}
                        className="bg-amber-400 h-full transition-all"
                        title="Chlorotic Stress Halo"
                      />
                      <div
                        style={{ width: `${diagnosis.tissueMorphometrics?.necroticPct ?? 14}%` }}
                        className="bg-rose-600 h-full transition-all"
                        title="Necrotic Lesion Core"
                      />
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-[11px] pt-1">
                      <div className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500 shrink-0" />
                        <span className="text-muted-foreground">{t("detect.healthy_label", "Healthy")}:</span>
                        <span className="font-mono font-bold text-foreground">
                          {diagnosis.tissueMorphometrics?.healthyPct ?? 72}%
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-sm bg-amber-400 shrink-0" />
                        <span className="text-muted-foreground">{t("detect.chlorotic_label", "Chlorotic")}:</span>
                        <span className="font-mono font-bold text-foreground">
                          {diagnosis.tissueMorphometrics?.chloroticPct ?? 14}%
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-sm bg-rose-600 shrink-0" />
                        <span className="text-muted-foreground">{t("detect.necrotic_label", "Necrotic")}:</span>
                        <span className="font-mono font-bold text-foreground">
                          {diagnosis.tissueMorphometrics?.necroticPct ?? 14}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Top-4 Differential Diagnosis Spectrum */}
                  {diagnosis.differentialDiagnosis && diagnosis.differentialDiagnosis.length > 0 && (
                    <div className="pt-3 border-t border-border space-y-2">
                      <div className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">
                        Top-4 Calibrated Differential Diagnosis Spectrum
                      </div>
                      <div className="space-y-1.5">
                        {diagnosis.differentialDiagnosis.map((item, idx) => (
                          <div key={item.disease} className="space-y-0.5">
                            <div className="flex justify-between text-xs">
                              <span className={idx === 0 ? "font-bold text-foreground" : "text-muted-foreground"}>
                                {idx + 1}. {item.disease}
                              </span>
                              <span className="font-mono font-bold text-foreground">{item.probability.toFixed(1)}%</span>
                            </div>
                            <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                              <div
                                style={{ width: `${Math.min(100, item.probability)}%` }}
                                className={`h-full rounded-full ${idx === 0 ? "bg-primary" : "bg-muted-foreground/40"}`}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* RIGHT COLUMN: STATUS / ERROR / GATEKEEPER / RESULTS */}
            <div className="lg:col-span-6 space-y-4">
              {/* Active Analyzing State Card */}
              {isAnalyzing && (
                <div className="bg-card rounded-2xl border border-primary/30 p-8 text-center min-h-[380px] flex flex-col items-center justify-center space-y-4 shadow-sm animate-in fade-in">
                  <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary animate-pulse">
                    <Cpu size={32} className="animate-spin" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-foreground">
                      Running Neural Health Analysis...
                    </h3>
                    <p className="text-xs text-muted-foreground mt-1 max-w-sm">
                      {currentStage.includes("STAGE_1")
                        ? t("detect.status_verifying", "Verifying leaf and palm specimen...")
                        : currentStage.includes("STAGE_2")
                        ? t("detect.status_spotting", "Spotting affected lesion zones...")
                        : currentStage.includes("STAGE_3")
                        ? t("detect.status_diagnosing", "Diagnosing disease and infection severity...")
                        : t("detect.status_generating", "Generating visual explanation and treatment plan...")}
                    </p>
                  </div>
                  <div className="w-full max-w-xs space-y-2">
                    <div className="flex justify-between text-xs font-mono font-bold text-primary">
                      <span>{t("detect.inference_progress", "Inference Progress")}</span>
                      <span>{progress}%</span>
                    </div>
                    <div className="w-full h-2.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleCancelJob}
                    className="btn-secondary text-xs text-danger hover:bg-danger/10 border-danger/30"
                  >
                    <XCircle size={13} /> {t("detect.cancel_analysis", "Cancel Analysis")}
                  </button>
                </div>
              )}

              {/* Error Notification */}
              {errorMessage && (
                <div className="bg-danger/10 border border-danger/30 rounded-2xl p-5 flex items-start gap-3">
                  <AlertTriangle size={20} className="text-danger shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-sm font-bold text-danger">{t("detect.diagnostic_notice", "Diagnostic Notice")}</h3>
                    <p className="text-xs text-muted-foreground mt-1">{errorMessage}</p>
                    {lastInferenceRef.current && (
                      <button
                        type="button"
                        onClick={() => {
                          if (lastInferenceRef.current) {
                            runRealInference(
                              lastInferenceRef.current.fileOrUrl,
                              lastInferenceRef.current.blockId,
                              lastInferenceRef.current.specimenId
                            )
                          }
                        }}
                        className="mt-3 px-3.5 py-1.5 rounded-xl bg-danger text-white hover:bg-danger/90 text-xs font-bold inline-flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer"
                      >
                        <RefreshCw size={12} /> {t("detect.retry_analysis", "Retry Analysis")}
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Non-Arecanut Gatekeeper Alert */}
              {diagnosis && (diagnosis.disease === "Not an Arecanut image" || diagnosis.severity === "Non-Arecanut") && (
                <div className="bg-card rounded-2xl border-2 border-warning/40 p-6 sm:p-8 space-y-5 shadow-sm flex flex-col justify-center min-h-[340px] animate-in fade-in duration-200">
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 rounded-2xl bg-warning/15 border border-warning/30 text-warning flex items-center justify-center shrink-0">
                      <AlertTriangle size={28} />
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="inline-flex items-center gap-1.5 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-warning/15 text-warning border border-warning/30">
                          <AlertTriangle size={12} />
                          <span>Invalid Image</span>
                        </span>
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-danger/15 text-danger border border-danger/30 font-mono">
                          {t("detect.gate_score", "Gate Score")}: {diagnosis.gateScore !== undefined ? diagnosis.gateScore : diagnosis.confidence}%
                        </span>
                      </div>
                      <h2 className="text-xl sm:text-2xl font-extrabold text-foreground">
                        This photo may not show an arecanut palm
                      </h2>
                      <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed max-w-xl">
                        The uploaded image does not show an arecanut (betel nut) palm, leaf, trunk, or nut bunch. Please upload a clear photograph of an arecanut plant to check for diseases.
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-border">
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="btn-primary text-xs justify-center px-6 py-3 shadow-sm font-bold flex items-center gap-2"
                    >
                      <Upload size={15} />
                      <span>{t("detect.upload_areca_btn", "Upload Arecanut Image")}</span>
                    </button>
                    <button
                      type="button"
                      onClick={handleReset}
                      className="btn-secondary text-xs justify-center px-4 py-3 flex items-center gap-1.5"
                    >
                      <XCircle size={14} />
                      <span>{t("detect.clear_image_btn", "Clear Image")}</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Gatekeeper Uncertain Alert */}
              {diagnosis && diagnosis.stage === "Gatekeeper Uncertain" && (
                <div className="bg-card rounded-2xl border-2 border-amber-500/40 p-6 sm:p-8 space-y-5 shadow-sm flex flex-col justify-center min-h-[340px] animate-in fade-in duration-200">
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 rounded-2xl bg-amber-500/15 border border-amber-500/30 text-amber-500 flex items-center justify-center shrink-0">
                      <AlertCircle size={28} />
                    </div>
                    <div className="space-y-2">
                      <span className="inline-flex items-center gap-1.5 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30">
                        <AlertCircle size={12} />
                        <span>Gatekeeper Uncertain</span>
                      </span>
                      <h2 className="text-xl sm:text-2xl font-extrabold text-foreground">
                        Gatekeeper Uncertain — Verification Required
                      </h2>
                      <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed max-w-xl">
                        {(diagnosis.retakePhoto && (diagnosis.retakePhoto[language as "en" | "kn" | "hi"] || diagnosis.retakePhoto.en)) ||
                          diagnosis.description ||
                          "The gatekeeper model cannot verify whether this image contains an arecanut palm with sufficient certainty. Disease diagnosis was suspended to protect diagnostic accuracy. Please retake the photo."}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-border">
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="btn-primary text-xs justify-center px-6 py-3 shadow-sm font-bold flex items-center gap-2"
                    >
                      <Upload size={15} />
                      <span>{t("detect.retake_photo_btn", "Retake / Upload New Photo")}</span>
                    </button>
                    <button
                      type="button"
                      onClick={handleReset}
                      className="btn-secondary text-xs justify-center px-4 py-3 flex items-center gap-1.5"
                    >
                      <XCircle size={14} />
                      <span>{t("detect.clear_image_btn", "Clear Image")}</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Full Clinical Diagnosis Card */}
              {diagnosis &&
                diagnosis.disease !== "Not an Arecanut image" &&
                diagnosis.severity !== "Non-Arecanut" &&
                diagnosis.stage !== "Gatekeeper Uncertain" && (
                <div className="bg-card rounded-2xl border border-border p-5 space-y-5 shadow-sm animate-in fade-in duration-200">
                  {treatmentSuccessBanner && (
                    <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center justify-between text-xs text-emerald-800 dark:text-emerald-300 animate-in fade-in">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
                        <span className="font-semibold">{treatmentSuccessBanner}</span>
                      </div>
                      <button onClick={() => setTreatmentSuccessBanner(null)} className="font-bold text-sm hover:opacity-75">✕</button>
                    </div>
                  )}

                  {diagnosis.isExperimentalClass ? (
                    <div className="p-4 bg-purple-500/15 border-2 border-purple-500/40 rounded-xl space-y-1.5 text-purple-900 dark:text-purple-100">
                      <div className="flex items-center gap-2 font-bold text-xs text-purple-600 dark:text-purple-400">
                        <AlertTriangle size={16} className="shrink-0" />
                        <span>{t("detect.experimental_class_badge", "Experimental Research Class")} — {t("detect.experimental_class_notice", "Clinical diagnosis withheld pending field validation.")}</span>
                      </div>
                      <p className="text-xs">
                        {(diagnosis.consultAgronomist && (diagnosis.consultAgronomist[language as "en" | "kn" | "hi"] || diagnosis.consultAgronomist.en)) ||
                          "This condition belongs to an experimental research category awaiting field validation. Differential diagnoses are provided below for reference only. Please consult a qualified agronomist or local KVK."}
                      </p>
                    </div>
                  ) : diagnosis.stage === "Low confidence" && (
                    <div className="p-4 bg-amber-500/15 border-2 border-amber-500/40 rounded-xl space-y-1.5 text-amber-900 dark:text-amber-100">
                      <div className="flex items-center gap-2 font-bold text-xs text-amber-600 dark:text-amber-400">
                        <AlertTriangle size={16} className="shrink-0" />
                        <span>Low Confidence Diagnosis — Agronomic Consultation Recommended</span>
                      </div>
                      <p className="text-xs">
                        {(diagnosis.consultAgronomist && (diagnosis.consultAgronomist[language as "en" | "kn" | "hi"] || diagnosis.consultAgronomist.en)) ||
                          "Prediction confidence fell below provisional certainty thresholds. Differential diagnoses are provided below for reference only. Please consult an agronomist."}
                      </p>
                    </div>
                  )}

                  {/* Header Diagnosis Banner */}
                  <div className="flex flex-wrap items-start justify-between gap-3 pb-4 border-b border-border">
                    <div>
                      <div className="flex items-center gap-2">
                        {diagnosis.isExperimentalClass ? (
                          <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-md bg-purple-500/15 text-purple-600 dark:text-purple-400 border border-purple-500/30">
                            {t("detect.experimental_class_badge", "Experimental Class")}
                          </span>
                        ) : diagnosis.disease === "Healthy" ? (
                          <CheckCircle2 size={18} className="text-primary" />
                        ) : (
                          <ShieldAlert size={18} className="text-danger" />
                        )}
                        <span className="text-xs font-bold uppercase tracking-wider text-primary">
                          {diagnosis.isExperimentalClass
                            ? "Research Category • Validation Pending"
                            : diagnosis.disease === "Healthy"
                            ? "AI screening suggests a healthy palm"
                            : `AI screening result · ${diagnosis.blockName || "Selected block"}`}
                        </span>
                      </div>
                      <h2 className="text-2xl font-extrabold text-foreground mt-1">{diagnosis.disease}</h2>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Stage: <strong className="text-foreground">{diagnosis.stage}</strong> • Scan ID:{" "}
                        <span className="font-mono">{diagnosis.id}</span>
                      </p>
                    </div>

                    <div className="flex flex-col items-end gap-2">
                      <div className="text-right bg-primary/10 px-3.5 py-2 rounded-xl border border-primary/20">
                        <div className="text-xl font-extrabold font-mono text-primary">{diagnosis.confidence}%</div>
                        <div className="text-[10px] text-muted-foreground font-semibold">Model confidence</div>
                      </div>

                      {/* Voice Readout Button */}
                      <button
                        type="button"
                        onClick={handleToggleVoiceBriefing}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 border transition-all cursor-pointer ${
                          isSpeaking
                            ? "bg-danger text-white border-danger animate-pulse"
                            : "bg-muted/50 hover:bg-muted text-foreground border-border"
                        }`}
                      >
                        {isSpeaking ? <VolumeX size={14} /> : <Volume2 size={14} />}
                        <span>{isSpeaking ? "Stop Audio" : `🔊 Listen (${language.toUpperCase()})`}</span>
                      </button>
                    </div>
                  </div>

                  {/* Clinical Description */}
                  <div className="p-3.5 rounded-xl bg-muted/30 border border-border">
                    <div className="text-xs font-bold text-foreground mb-1">What the scan found</div>
                    <p className="text-xs text-muted-foreground leading-relaxed">{diagnosis.description}</p>
                    <p className="mt-2 text-[11px] leading-relaxed text-muted-foreground">This is an AI-assisted screening result, not a confirmed diagnosis. Check the plant in the field and consult a local agronomist before treatment.</p>
                  </div>

                  {/* INTERACTIVE SPRAY DOSAGE & WEATHER-WINDOW CALCULATOR */}
                  <div className="rounded-2xl border border-primary/30 bg-primary/5 p-4 space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Calculator size={15} className="text-primary" />
                        <div>
                          <h4 className="text-xs font-extrabold uppercase tracking-wider text-foreground">
                            {dosagePlan.title}
                          </h4>
                          <span className="text-[10px] text-muted-foreground">Estimated quantities for the selected palm count</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-muted-foreground font-medium">{t("detect.palms_count_label", "Palms:")}</span>
                        <input
                          type="number"
                          min={1}
                          max={10000}
                          value={palmCountToSpray}
                          onChange={(e) => setPalmCountToSpray(Math.max(1, parseInt(e.target.value) || 1))}
                          className="w-20 px-2 py-1 rounded-lg bg-card border border-border font-mono text-xs font-bold text-foreground text-center"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      <div className="p-2.5 rounded-xl bg-card border border-border text-center">
                        <div className="text-sm font-extrabold font-mono text-primary">{dosagePlan.sprayLiters} L</div>
                        <div className="text-[10px] text-muted-foreground">{t("detect.fluid_volume", "Fluid Vol.")}</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-card border border-border text-center">
                        <div className="text-sm font-extrabold font-mono text-foreground">
                          {dosagePlan.primaryVal}
                        </div>
                        <div className="text-[10px] text-muted-foreground">{dosagePlan.primaryLabel}</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-card border border-border text-center">
                        <div className="text-sm font-extrabold font-mono text-emerald-600">
                          {dosagePlan.secondaryVal}
                        </div>
                        <div className="text-[10px] text-muted-foreground">{dosagePlan.secondaryLabel}</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-card border border-border text-center">
                        <div className="text-sm font-extrabold font-mono text-foreground">
                          {dosagePlan.rosinStickerMl} ml
                        </div>
                        <div className="text-[10px] text-muted-foreground">{t("detect.adhesive_sticker", "Adhesive Sticker")}</div>
                      </div>
                    </div>

                    {dosagePlan.highHumidityOrRain && (
                      <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center gap-2 text-xs text-amber-800 dark:text-amber-300">
                        <Droplets size={14} className="shrink-0 text-amber-600" />
                        <span>{t("detect.rain_risk_warning", "High humidity / rain risk detected: Ensure Rosin sticker is blended to prevent wash-off.")}</span>
                      </div>
                    )}
                    <p className="text-[10px] leading-relaxed text-muted-foreground">Planning estimate only. Follow the product label and local agricultural guidance for the crop, location, and current conditions.</p>
                  </div>

                  {/* Treatment Protocols Tabs */}
                  <div className="space-y-3 pt-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Sprout size={16} className="text-primary" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">
                          Targeted ICAR-CPCRI Management Protocols
                        </h4>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          setTreatmentModalMode(diagnosis.disease === "Healthy" ? "fertilizers" : "pesticides")
                          setTreatmentModalOpen(true)
                        }}
                        className="text-xs font-bold text-primary hover:underline flex items-center gap-1"
                      >
                        <Calculator size={13} /> Full Schedule Hub →
                      </button>
                    </div>

                    <div className="space-y-2">
                      <div className="text-xs font-bold text-foreground">{t("detect.primary_actions", "Primary Action Steps:")}</div>
                      <ul className="space-y-1.5 text-xs text-muted-foreground pl-1">
                        {diagnosis.treatments.map((t, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-primary font-bold mt-0.5">•</span>
                            <span>{t}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {diagnosis.organicControl.length > 0 && (
                      <div className="space-y-2 pt-2 border-t border-border">
                        <div className="text-xs font-bold text-foreground">{t("detect.organic_sanitation", "Organic & Cultural Sanitation:")}</div>
                        <ul className="space-y-1.5 text-xs text-muted-foreground pl-1">
                          {diagnosis.organicControl.map((o, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="text-emerald-500 font-bold mt-0.5">•</span>
                              <span>{o}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Bottom Action Buttons */}
                  <div className="flex flex-wrap items-center gap-2.5 pt-4 border-t border-border">
                    {currentScanItem?.treatment?.isTreated ? (
                      <div className="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-emerald-600/10 border border-emerald-600/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold shadow-xs">
                        <ShieldCheck size={16} className="text-emerald-600 shrink-0" />
                        <span>{t("detect.treatment_active", "Treatment Active · Follow-Up:")} {currentScanItem.treatment.followUpDate}</span>
                      </div>
                    ) : (
                      diagnosis.disease !== "Healthy" && !diagnosis.isExperimentalClass && (
                        <button
                          type="button"
                          onClick={() => setMarkTreatmentModalOpen(true)}
                          className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                        >
                          <ShieldCheck size={15} />
                          <span>{t("detect.log_treatment_btn", "Log Treatment & 14d Recovery")}</span>
                        </button>
                      )
                    )}
                    <button
                      type="button"
                      onClick={handleConsultAiAgronomist}
                      className="btn-primary text-xs flex-1 justify-center py-2.5 shadow-md"
                    >
                      <Sparkles size={15} />
                      <span>{t("detect.consult_agronomist_btn", "Consult AI Agronomist with This Scan")}</span>
                    </button>
                    <button
                      type="button"
                      onClick={handleDownloadSummary}
                      className="btn-secondary text-xs justify-center py-2.5"
                    >
                      <FileText size={14} />
                      <span>Download screening summary</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => navigate("/map")}
                      className="btn-secondary text-xs justify-center py-2.5"
                    >
                      <MapPin size={14} />
                      <span>{t("detect.view_gis_map_btn", "View Updated GIS Map")}</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      {/* Live WebRTC Camera Modal */}
      <LiveCameraModal
        isOpen={cameraModalOpen}
        onClose={() => setCameraModalOpen(false)}
        onCapture={(file: File) => {
          const previewUrl = URL.createObjectURL(file)
          ownedPreviewUrlsRef.current.add(previewUrl)
          setSelectedImage(previewUrl)
          runRealInference(file, selectedBlockId)
        }}
      />

      {/* ICAR-CPCRI Fertilizer & Pesticide Hub Modal */}
      <TreatmentCalculatorModal
        isOpen={treatmentModalOpen}
        onClose={() => setTreatmentModalOpen(false)}
        initialDisease={diagnosis?.disease || "koleroga"}
        initialPalms={palmCountToSpray}
        initialMode={treatmentModalMode}
      />

      {/* Log Treatment & Recovery Modal */}
      <MarkTreatmentModal
        isOpen={markTreatmentModalOpen}
        onClose={() => setMarkTreatmentModalOpen(false)}
        scan={
          currentScanItem ||
          (diagnosis
            ? {
                id: diagnosis.id || `scan-${Date.now()}`,
                title: `${diagnosis.disease} Inspection`,
                disease: diagnosis.disease,
                confidence: diagnosis.confidence,
                stage: diagnosis.stage,
                severity: (diagnosis.severity as ScanItem["severity"]) || "Moderate",
                date: new Date().toLocaleDateString("en-US"),
                location: selectedBlockId,
                temp: "24°C",
                weatherCondition: "Humid",
                imageUrl: selectedImage || "",
                recommendedActions: diagnosis.treatments || [],
              }
            : null)
        }
        onConfirm={handleConfirmDirectTreatment}
      />
    </div>
  )
}
