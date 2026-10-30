import { useState } from "react"
import { Link, useSearchParams } from "react-router-dom"
import {
  ScanLine,
  Search,
  Calendar,
  Trash2,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  Filter,
  Plus,
  CloudSun,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  ShieldCheck,
  Clock,
  Calculator,
  Sprout,
  Download,
  Printer,
  FileText,
  Table,
  LayoutGrid,
  MapPin,
  Eye,
  Sparkles,
} from "lucide-react"
import { useScanHistory, ScanItem } from "../contexts/ScanHistoryContext"
import { useNotifications } from "../contexts/NotificationContext"
import { usePlantation } from "../contexts/PlantationContext"
import { useLanguage } from "../contexts/LanguageContext"
import { useFocusTrap } from "../hooks/useFocusTrap"
import { useArecaPalette } from "../hooks/useArecaPalette"
import { handleImageError } from "../utils/imageFallback"
import MarkTreatmentModal from "../components/MarkTreatmentModal"
import TreatmentCalculatorModal from "../components/TreatmentCalculatorModal"
import {
  generateReportApi,
  generateSingleScanReport,
  triggerBlobDownload,
} from "../services/reportService"

interface ScanHistoryProps {
  defaultView?: "scans" | "reports"
}

function formatScanDate(value: string): string {
  const parts = /^(\d{4}-\d{2}-\d{2})[ T](\d{2}):(\d{2})$/.exec(value)
  if (!parts) return value

  const hour = Number(parts[2])
  const hour12 = hour % 12 || 12
  const meridiem = hour < 12 ? "AM" : "PM"
  return `${parts[1]} ${hour12}:${parts[3]} ${meridiem}`
}

export default function ScanHistory({ defaultView = "scans" }: ScanHistoryProps) {
  const { scans, deleteScan, clearHistory, markTreated } = useScanHistory()
  const { addNotification } = useNotifications()
  const { blocks, totalTrees, totalAcres, healthyTrees, diseasedTrees, overallHealthScore, markBlockTreated } = usePlantation()
  const { t } = useLanguage()
  const pagePalette = useArecaPalette()
  const [searchParams, setSearchParams] = useSearchParams()

  const [searchTerm, setSearchTerm] = useState("")
  const [selectedDiseaseFilter, setSelectedDiseaseFilter] = useState("All")
  const [selectedBlockFilter, setSelectedBlockFilter] = useState("All")
  const [treatmentStatusFilter, setTreatmentStatusFilter] = useState<"all" | "treated" | "pending">("all")
  const [displayMode, setDisplayMode] = useState<"grid" | "table">(defaultView === "reports" ? "table" : "grid")
  const [currentPage, setCurrentPage] = useState(1)
  const [showClearModal, setShowClearModal] = useState(false)
  const [scanToDelete, setScanToDelete] = useState<string | null>(null)
  const [scanToTreat, setScanToTreat] = useState<ScanItem | null>(null)
  const [selectedScanDetail, setSelectedScanDetail] = useState<ScanItem | null>(null)
  const [calcModalOpen, setCalcModalOpen] = useState(false)
  const [calcModalDisease, setCalcModalDisease] = useState("koleroga")
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null)
  const [exporting, setExporting] = useState(false)

  const clearModalRef = useFocusTrap<HTMLDivElement>({
    isOpen: showClearModal,
    onClose: () => setShowClearModal(false),
  })

  const deleteModalRef = useFocusTrap<HTMLDivElement>({
    isOpen: scanToDelete !== null,
    onClose: () => setScanToDelete(null),
  })

  const handleConfirmTreatment = (details: {
    treatmentType: "chemical" | "organic"
    chemicalUsed: string
    notes?: string
    blockId?: string
    followUpDate: string
  }) => {
    if (!scanToTreat) return
    markTreated(scanToTreat.id, details)
    markBlockTreated(details.blockId || scanToTreat.location, {
      treatmentType: details.treatmentType,
      chemicalUsed: details.chemicalUsed,
      followUpDate: details.followUpDate,
    })
    addNotification({
      type: "info",
      title: `Treatment Logged: ${scanToTreat.disease}`,
      msg: `Applied ${details.chemicalUsed} at ${scanToTreat.location}. 14-day follow-up inspection scheduled for ${details.followUpDate}.`,
      blockId: scanToTreat.location,
    })
    setFeedbackMessage(
      `Treatment logged for ${scanToTreat.disease}! 14-day follow-up re-inspection scheduled for ${details.followUpDate}.`
    )
    setTimeout(() => setFeedbackMessage(null), 5000)
    setScanToTreat(null)
  }

  // Export Entire Filtered Set to CSV
  const handleExportCSV = async () => {
    try {
      setExporting(true)
      const blob = await generateReportApi(
        {
          type: "detailed",
          timeframe: new Date().toLocaleDateString("en-US", { month: "long", year: "numeric" }),
          format: "csv",
        },
        {
          scans: filteredScans,
          blocks,
          totalAcres,
          totalTrees,
          healthyTrees,
          diseasedTrees,
          overallHealthScore,
        }
      )
      triggerBlobDownload(blob)
      setFeedbackMessage("Exported field diagnostic logs to CSV.")
      setTimeout(() => setFeedbackMessage(null), 4000)
    } catch (err) {
      console.error("Export error:", err)
    } finally {
      setExporting(false)
    }
  }

  // Print Single Scan Field Audit Slip
  const handlePrintSlip = (scan: ScanItem) => {
    const reportBlob = generateSingleScanReport(scan, "pdf")
    triggerBlobDownload(reportBlob)
  }

  // Print Full Audit View
  const handlePrintAuditReport = () => {
    window.print()
  }

  const itemsPerPage = 6

  const filteredScans = scans.filter((scan) => {
    const matchesSearch =
      scan.disease.toLowerCase().includes(searchTerm.toLowerCase()) ||
      scan.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
      scan.title.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesDisease =
      selectedDiseaseFilter === "All" ||
      scan.disease.toLowerCase().includes(selectedDiseaseFilter.toLowerCase())
    const matchesBlock =
      selectedBlockFilter === "All" ||
      scan.location.toLowerCase().includes(selectedBlockFilter.toLowerCase())
    const isTreated = !!scan.treatment?.isTreated
    const matchesTreatment =
      treatmentStatusFilter === "all" ||
      (treatmentStatusFilter === "treated" && isTreated) ||
      (treatmentStatusFilter === "pending" && !isTreated && scan.disease !== "Healthy" && scan.disease !== "Non-Arecanut")
    return matchesSearch && matchesDisease && matchesBlock && matchesTreatment
  })

  const totalPages = Math.max(1, Math.ceil(filteredScans.length / itemsPerPage))
  const paginatedScans = filteredScans.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-5 text-foreground sm:p-6 lg:p-8" style={pagePalette}>
      {/* Header */}
      <div className="flex flex-col gap-4 border-b border-border/80 pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">{t("scans.title", "Field Logs & Agronomic Reports")}</h1>
            <span className="text-[10px] font-bold px-2 py-0.5 bg-primary/10 text-primary border border-primary/20 rounded-full flex items-center gap-1">
              <Sparkles size={11} />
              Unified Records
            </span>
          </div>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            {t("scans.subtitle", "Audit history, treatment tracking, and ICAR-CPCRI compliance export")}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {scans.length > 0 && (
            <>
              <button
                onClick={handleExportCSV}
                disabled={exporting}
                className="btn-secondary text-xs flex items-center gap-1.5 shadow-xs"
                title="Export filtered records as CSV spreadsheet"
              >
                <Download size={14} />
                <span>{exporting ? "Exporting..." : "Export CSV"}</span>
              </button>

              <button
                onClick={handlePrintAuditReport}
                className="btn-secondary text-xs flex items-center gap-1.5 shadow-xs"
                title="Print formal plantation audit certificate"
              >
                <Printer size={14} />
                <span>Print Audit Slip</span>
              </button>

              <button
                onClick={() => setShowClearModal(true)}
                className="px-2.5 py-1.5 rounded-xl text-xs font-semibold text-danger bg-danger/10 hover:bg-danger/20 transition-colors flex items-center gap-1"
                title="Clear local cached records"
              >
                <Trash2 size={13} />
              </button>
            </>
          )}

          <Link to="/detection" className="btn-primary text-xs flex items-center gap-1.5 shadow-xs">
            <Plus size={14} />
            <span>{t("scans.new_scan", "New Scan")}</span>
          </Link>
        </div>
      </div>

      {feedbackMessage && (
        <div className="p-3 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-between text-xs text-primary animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <CheckCircle2 size={16} />
            <span className="font-semibold">{feedbackMessage}</span>
          </div>
          <button onClick={() => setFeedbackMessage(null)} className="text-primary hover:opacity-80 text-sm font-bold">
            ✕
          </button>
        </div>
      )}

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <div className="p-5 rounded-2xl bg-card border border-border shadow-xs text-center sm:text-left sm:p-6">
          <div className="text-[11px] font-bold text-muted-foreground uppercase">Total Scans</div>
          <div className="text-2xl font-extrabold text-foreground mt-0.5">{scans.length}</div>
          <div className="text-[10px] text-muted-foreground mt-0.5">Audited palms</div>
        </div>

        <div className="p-5 rounded-2xl bg-card border border-border shadow-xs text-center sm:text-left sm:p-6">
          <div className="text-[11px] font-bold text-muted-foreground uppercase">Healthy Index</div>
          <div className="text-2xl font-extrabold text-primary mt-0.5">{overallHealthScore || 92}%</div>
          <div className="text-[10px] text-muted-foreground mt-0.5">Optimal vigor</div>
        </div>

        <div className="p-5 rounded-2xl bg-card border border-border shadow-xs text-center sm:text-left sm:p-6">
          <div className="text-[11px] font-bold text-muted-foreground uppercase">Active Infections</div>
          <div className="text-2xl font-extrabold text-danger mt-0.5">
            {scans.filter(s => s.severity === "Critical" || s.severity === "Severe").length}
          </div>
          <div className="text-[10px] text-muted-foreground mt-0.5">Critical &amp; Severe</div>
        </div>

        <div className="p-5 rounded-2xl bg-card border border-border shadow-xs text-center sm:text-left sm:p-6">
          <div className="text-[11px] font-bold text-muted-foreground uppercase">Treated Palms</div>
          <div className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">
            {scans.filter(s => s.treatment?.isTreated).length}
          </div>
          <div className="text-[10px] text-muted-foreground mt-0.5">In recovery cycle</div>
        </div>
      </div>

      {/* ===== EMPTY STATE ===== */}
      {scans.length === 0 ? (
        <div className="bg-card rounded-2xl border border-border p-12 text-center flex flex-col items-center justify-center min-h-[360px]">
          <div className="w-16 h-16 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-4 shadow-sm">
            <ScanLine size={32} />
          </div>

          <h2 className="text-lg font-bold text-foreground mb-1">
            {t("scans.empty_title", "No diagnostic scan records found.")}
          </h2>

          <p className="text-xs text-muted-foreground max-w-sm mb-6 leading-relaxed">
            {t("scans.empty_desc", "Analyze your first palm to start building your audit logs and tracking plantation recovery trends.")}
          </p>

          <Link to="/detection" className="btn-primary text-xs px-5 py-2.5 shadow-sm flex items-center gap-2">
            <ScanLine size={15} />
            <span>{t("scans.analyze_btn", "Analyze Palm Specimen")}</span>
          </Link>
        </div>
      ) : (
        /* ===== POPULATED STATE ===== */
        <div className="space-y-5">
          {/* Controls Bar */}
          <div className="flex flex-col lg:flex-row items-center justify-between gap-3 bg-card p-4 rounded-xl border border-border">
            <div className="flex items-center gap-2 bg-muted/50 border border-border rounded-xl px-3 py-2 w-full lg:w-72">
              <Search size={15} className="text-muted-foreground shrink-0" />
              <input
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder={t("scans.search_placeholder", "Search scans by ID, disease, or block...")}
                className="bg-transparent border-none outline-none text-xs text-foreground placeholder-muted-foreground flex-1"
              />
            </div>

            <div className="flex flex-wrap items-center gap-2.5 w-full lg:w-auto justify-end">
              <Filter size={14} className="text-muted-foreground shrink-0" />
              
              {/* Block Filter */}
              <select
                value={selectedBlockFilter}
                onChange={(e) => setSelectedBlockFilter(e.target.value)}
                className="bg-card border border-border rounded-xl px-2.5 py-1.5 text-xs font-semibold text-foreground outline-none cursor-pointer"
              >
                <option value="All" className="bg-card text-foreground">All Plantation Blocks</option>
                {blocks.map((b) => (
                  <option key={b.id} value={b.name || b.id} className="bg-card text-foreground">{b.name || b.id}</option>
                ))}
              </select>

              {/* Disease Filter */}
              <select
                value={selectedDiseaseFilter}
                onChange={(e) => setSelectedDiseaseFilter(e.target.value)}
                className="bg-card border border-border rounded-xl px-2.5 py-1.5 text-xs font-semibold text-foreground outline-none cursor-pointer"
              >
                <option value="All" className="bg-card text-foreground">{t("scans.filter_all", "All Diagnoses")}</option>
                <option value="Anthracnose" className="bg-card text-foreground">{t("disease.anthracnose", "Anthracnose")}</option>
                <option value="Koleroga" className="bg-card text-foreground">{t("scans.filter_koleroga", "Koleroga / Fruit Rot")}</option>
                <option value="Nut Cracking" className="bg-card text-foreground">{t("disease.nut_cracking", "Nut Cracking")}</option>
                <option value="Bud Borer" className="bg-card text-foreground">Bud Borer</option>
                <option value="Yellow Leaf" className="bg-card text-foreground">Yellow Leaf</option>
                <option value="Stem Bleeding" className="bg-card text-foreground">Stem Bleeding</option>
                <option value="Healthy" className="bg-card text-foreground">Healthy Palms</option>
              </select>

              {/* Treatment Status Filter */}
              <select
                value={treatmentStatusFilter}
                onChange={(e) => setTreatmentStatusFilter(e.target.value as any)}
                className="bg-card border border-border rounded-xl px-2.5 py-1.5 text-xs font-semibold text-foreground outline-none cursor-pointer"
              >
                <option value="all" className="bg-card text-foreground">All Treatments</option>
                <option value="treated" className="bg-card text-foreground">Treated &amp; In Recovery</option>
                <option value="pending" className="bg-card text-foreground">Action Required (Pending)</option>
              </select>

              {/* View Mode Toggle */}
              <div className="flex items-center gap-1 bg-muted p-1 rounded-xl">
                <button
                  onClick={() => setDisplayMode("grid")}
                  className={`p-1 rounded-lg transition-colors ${displayMode === "grid" ? "bg-card text-foreground shadow-xs" : "text-muted-foreground"}`}
                  title="Card Grid View"
                >
                  <LayoutGrid size={15} />
                </button>
                <button
                  onClick={() => setDisplayMode("table")}
                  className={`p-1 rounded-lg transition-colors ${displayMode === "table" ? "bg-card text-foreground shadow-xs" : "text-muted-foreground"}`}
                  title="Audit Table View"
                >
                  <Table size={15} />
                </button>
              </div>
            </div>
          </div>

          {/* Grid View or Filter-Mismatch Empty State */}
          {filteredScans.length === 0 ? (
            <div className="bg-card rounded-2xl border border-border p-12 text-center flex flex-col items-center justify-center min-h-[260px]">
              <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center text-muted-foreground mb-3">
                <Search size={20} />
              </div>
              <h3 className="text-sm font-bold text-foreground mb-1">
                {t("scans.no_matching_title", "No scans match your search or filter criteria")}
              </h3>
              <p className="text-xs text-muted-foreground max-w-sm mb-4 leading-relaxed">
                {t("scans.no_matching_desc", "Try adjusting your search query or resetting block/disease filters.")}
              </p>
              <button
                onClick={() => {
                  setSearchTerm("")
                  setSelectedDiseaseFilter("All")
                  setSelectedBlockFilter("All")
                  setTreatmentStatusFilter("all")
                }}
                className="btn-secondary text-xs px-3.5 py-1.5 flex items-center gap-1.5"
              >
                <RefreshCw size={12} />
                <span>{t("scans.reset_filters", "Reset All Filters")}</span>
              </button>
            </div>
          ) : displayMode === "table" ? (
            /* ===== TABLE VIEW (FORMAL AUDIT) ===== */
            <div className="bg-card rounded-xl border border-border overflow-hidden shadow-xs">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-muted/40 border-b border-border text-[11px] font-bold text-muted-foreground uppercase tracking-wider">
                    <tr>
                      <th className="px-4 py-3">Scan ID</th>
                      <th className="px-4 py-3">Date</th>
                      <th className="px-4 py-3">Plantation Block</th>
                      <th className="px-4 py-3">Diagnosed Condition</th>
                      <th className="px-4 py-3">Confidence</th>
                      <th className="px-4 py-3">Severity</th>
                      <th className="px-4 py-3">Treatment Lifecycle</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {paginatedScans.map((item) => (
                      <tr key={item.id} className="hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3 font-mono font-bold text-foreground">{item.id}</td>
                        <td className="px-4 py-3 text-muted-foreground whitespace-nowrap">{formatScanDate(item.date)}</td>
                        <td className="px-4 py-3 font-medium text-foreground">{item.location}</td>
                        <td className="px-4 py-3 font-bold text-primary">{item.disease}</td>
                        <td className="px-4 py-3 font-semibold text-foreground">{item.confidence}%</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full border ${
                            item.severity === "Critical" || item.severity === "Severe"
                              ? "bg-danger/10 text-danger border-danger/20"
                              : item.severity === "Moderate"
                              ? "bg-warning/10 text-warning border-warning/20"
                              : "bg-success/10 text-success border-success/20"
                          }`}>
                            {item.severity}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {item.treatment?.isTreated ? (
                            <span className="text-emerald-700 dark:text-emerald-300 font-semibold flex items-center gap-1">
                              <CheckCircle2 size={13} className="text-emerald-600" />
                              Treated ({item.treatment.chemicalUsed.split(" ")[0]})
                            </span>
                          ) : item.disease !== "Healthy" && item.disease !== "Non-Arecanut" ? (
                            <button
                              onClick={() => setScanToTreat(item)}
                              className="text-[10px] font-bold text-amber-700 dark:text-amber-400 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/25 px-2 py-0.5 rounded-lg transition-colors"
                            >
                              Log Treatment
                            </button>
                          ) : (
                            <span className="text-muted-foreground">Optimal Vigor</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handlePrintSlip(item)}
                              className="p-1 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted"
                              title="Print Field Audit Slip"
                            >
                              <Printer size={14} />
                            </button>
                            <Link
                              to="/detection"
                              state={{ imageUrl: item.imageUrl }}
                              className="p-1 rounded-lg text-primary hover:bg-primary/10"
                              title="Re-analyze Specimen"
                            >
                              <ExternalLink size={14} />
                            </Link>
                            <button
                              onClick={() => setScanToDelete(item.id)}
                              className="p-1 rounded-lg text-muted-foreground hover:text-danger hover:bg-danger/10"
                              title="Delete Record"
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            /* ===== CARD GRID VIEW ===== */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {paginatedScans.map((item) => (
                <div key={item.id} className="bg-card rounded-2xl border border-border overflow-hidden shadow-xs card-hover flex flex-col justify-between">
                  <div className="p-4 space-y-3">
                    <div className="relative aspect-[16/10] rounded-xl overflow-hidden bg-muted border border-border">
                      <img
                        src={item.imageUrl}
                        alt={item.title}
                        onError={handleImageError}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute top-2 right-2 px-2 py-1 rounded-full text-[10px] font-extrabold bg-black/60 text-white backdrop-blur-md">
                        {item.confidence}% {t("scans.confidence_suffix", "Confidence")}
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <h3 className="font-bold text-foreground text-sm">{item.title}</h3>
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full border ${
                        item.severity === "Critical" || item.severity === "Severe" || item.severity === "High"
                          ? "bg-danger/10 text-danger border-danger/20"
                          : item.severity === "Moderate"
                          ? "bg-warning/10 text-warning border-warning/20"
                          : item.severity === "Healthy"
                          ? "bg-success/10 text-success border-success/20"
                          : "bg-primary/10 text-primary border-primary/20"
                      }`}>
                        {item.severity}
                      </span>
                    </div>

                    <div className="text-xs text-primary font-bold">{item.disease}</div>

                    {/* Treatment Lifecycle Status Banner */}
                    {item.treatment?.isTreated ? (
                      <div className="p-2.5 rounded-xl bg-emerald-600/10 border border-emerald-600/25 space-y-1">
                        <div className="flex items-center justify-between text-[11px] font-bold text-emerald-700 dark:text-emerald-300">
                          <span className="flex items-center gap-1.5">
                            <CheckCircle2 size={13} className="text-emerald-600 shrink-0" />
                            Treated &amp; Recovering
                          </span>
                          <span className="text-[10px] font-mono text-muted-foreground">{item.treatment.treatedAt}</span>
                        </div>
                        <div className="text-[10px] text-foreground font-semibold truncate">
                          {item.treatment.chemicalUsed}
                        </div>
                        <div className="flex items-center gap-1.5 text-[10px] text-primary font-semibold pt-0.5 border-t border-emerald-600/15">
                          <Clock size={11} className="shrink-0" />
                          <span>Follow-up Due: <strong>{item.treatment.followUpDate}</strong></span>
                        </div>
                      </div>
                    ) : item.disease !== "Healthy" && item.disease !== "Non-Arecanut" ? (
                      <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-between gap-2">
                        <div className="flex items-center gap-1.5 text-[11px] font-semibold text-amber-700 dark:text-amber-400">
                          <AlertTriangle size={13} className="shrink-0" />
                          <span>Action Pending</span>
                        </div>
                        <button
                          onClick={() => setScanToTreat(item)}
                          className="px-2.5 py-1 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-bold text-[10px] transition-colors shadow-xs"
                        >
                          Log Treatment
                        </button>
                      </div>
                    ) : (
                      <div className="p-2 rounded-xl bg-emerald-600/5 border border-emerald-600/15 flex items-center gap-1.5 text-[11px] text-emerald-700 dark:text-emerald-300 font-medium">
                        <CheckCircle2 size={13} className="text-emerald-600 shrink-0" />
                        <span>Optimal Vigor · Routine Maintenance</span>
                      </div>
                    )}

                    <div className="space-y-1 pt-2 border-t border-border text-[11px] text-muted-foreground">
                      <div className="flex items-center gap-1.5">
                        <Calendar size={12} /> {formatScanDate(item.date)}
                      </div>
                      <div className="flex items-center gap-1.5">
                        <MapPin size={12} /> {item.location}
                      </div>
                    </div>
                  </div>

                  <div className="px-4 py-3 bg-muted/20 border-t border-border flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handlePrintSlip(item)}
                        className="text-xs font-semibold text-muted-foreground hover:text-foreground flex items-center gap-1"
                        title="Download printable field audit certificate"
                      >
                        <Printer size={13} />
                        <span>Slip</span>
                      </button>
                      <button
                        onClick={() => {
                          setCalcModalDisease(item.disease)
                          setCalcModalOpen(true)
                        }}
                        className="text-xs font-semibold text-muted-foreground hover:text-foreground flex items-center gap-1"
                        title="Calculate exact pesticide or fertilizer dosages"
                      >
                        <Calculator size={13} />
                        <span>Dosage</span>
                      </button>
                    </div>

                    <div className="flex items-center gap-2">
                      <Link
                        to="/detection"
                        state={{ imageUrl: item.imageUrl }}
                        className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
                      >
                        {t("scans.reanalyze", "Re-analyze")} <ExternalLink size={12} />
                      </Link>
                      <button
                        onClick={() => setScanToDelete(item.id)}
                        className="p-1.5 text-muted-foreground hover:text-danger transition-colors rounded-lg"
                        title={t("scans.delete_scan", "Delete Scan")}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-muted-foreground">
                Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, filteredScans.length)} of {filteredScans.length} records
              </span>

              <div className="flex items-center gap-1">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-2 rounded-xl border border-border text-foreground hover:bg-muted disabled:opacity-40 transition-colors"
                >
                  <ChevronLeft size={16} />
                </button>
                <span className="text-xs font-bold px-3 py-1 bg-muted rounded-xl text-foreground">
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="p-2 rounded-xl border border-border text-foreground hover:bg-muted disabled:opacity-40 transition-colors"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Confirmation Delete Modal */}
      {scanToDelete && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div
            ref={deleteModalRef}
            tabIndex={-1}
            role="dialog"
            aria-modal="true"
            aria-labelledby="confirm-delete-title"
            className="bg-card border border-border rounded-2xl p-6 max-w-sm w-full space-y-4 shadow-2xl"
          >
            <div className="w-12 h-12 rounded-full bg-danger/10 text-danger flex items-center justify-center mx-auto">
              <Trash2 size={24} />
            </div>
            <div className="text-center space-y-1">
              <h2 id="confirm-delete-title" className="text-base font-bold text-foreground">
                {t("scans.delete_confirm_title", "Delete scan record?")}
              </h2>
              <p className="text-xs text-muted-foreground">
                {t("scans.delete_confirm_desc", "This will permanently remove this scan from your history.")}
              </p>
            </div>
            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={() => setScanToDelete(null)}
                className="flex-1 py-2 px-3 border border-border rounded-xl text-xs font-semibold text-foreground hover:bg-muted transition-colors"
              >
                {t("scans.cancel_btn", "Cancel")}
              </button>
              <button
                onClick={() => {
                  if (scanToDelete) {
                    deleteScan(scanToDelete)
                    setScanToDelete(null)
                    setFeedbackMessage(t("scans.deleted_msg", "Scan record deleted successfully."))
                    setTimeout(() => setFeedbackMessage(null), 3000)
                  }
                }}
                className="flex-1 py-2 px-3 bg-danger hover:bg-danger/90 text-white rounded-xl text-xs font-bold transition-colors shadow-sm"
              >
                {t("scans.confirm_delete_btn", "Delete")}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Clear All Modal */}
      {showClearModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div
            ref={clearModalRef}
            tabIndex={-1}
            role="dialog"
            aria-modal="true"
            aria-labelledby="confirm-clear-title"
            className="bg-card border border-border rounded-2xl p-6 max-w-sm w-full space-y-4 shadow-2xl"
          >
            <div className="w-12 h-12 rounded-full bg-danger/10 text-danger flex items-center justify-center mx-auto">
              <AlertTriangle size={24} />
            </div>
            <div className="text-center space-y-1">
              <h2 id="confirm-clear-title" className="text-base font-bold text-foreground">
                {t("scans.confirm_clear_title", "Clear scan history?")}
              </h2>
              <p className="text-xs text-muted-foreground">
                {t("scans.confirm_clear_desc", "Are you sure you want to clear your local scan history? Server records in SQLite remain preserved.")}
              </p>
            </div>
            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={() => setShowClearModal(false)}
                className="flex-1 py-2 px-3 border border-border rounded-xl text-xs font-semibold text-foreground hover:bg-muted transition-colors"
              >
                {t("scans.confirm_cancel_btn", "Cancel")}
              </button>
              <button
                onClick={() => {
                  clearHistory()
                  setShowClearModal(false)
                  setFeedbackMessage(t("scans.history_cleared", "Scan history successfully cleared."))
                  setTimeout(() => setFeedbackMessage(null), 4000)
                }}
                className="flex-1 py-2 px-3 bg-danger hover:bg-danger/90 text-white rounded-xl text-xs font-bold transition-colors shadow-sm"
              >
                {t("scans.confirm_clear_btn", "Yes, Clear History")}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Log Treatment Modal */}
      {scanToTreat && (
        <MarkTreatmentModal
          isOpen={scanToTreat !== null}
          onClose={() => setScanToTreat(null)}
          scan={scanToTreat}
          onConfirm={handleConfirmTreatment}
        />
      )}

      {/* Spray Dosage Modal */}
      {calcModalOpen && (
        <TreatmentCalculatorModal
          isOpen={calcModalOpen}
          onClose={() => setCalcModalOpen(false)}
          initialDisease={calcModalDisease}
          initialPalms={450}
        />
      )}
    </div>
  )
}
