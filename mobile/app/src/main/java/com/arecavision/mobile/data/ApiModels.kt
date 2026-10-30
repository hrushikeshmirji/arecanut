package com.arecavision.mobile.data

import com.google.gson.annotations.SerializedName

data class ApiEnvelope<T>(
    val success: Boolean = false,
    val data: T? = null,
    val error: ApiError? = null,
)

data class ApiError(
    val code: String? = null,
    val message: String? = null,
)

data class DashboardDto(
    val totalTrees: Int = 0,
    val healthyTrees: Int = 0,
    val diseasedTrees: Int = 0,
    val aiAccuracy: Double = 0.0,
    val todayScansCount: Int = 0,
    val pendingAlertsCount: Int = 0,
    val overallHealthScore: Int? = null,
)

data class DiseaseTrendDto(
    val date: String = "",
    val anthracnose: Int = 0,
    val koleroga: Int = 0,
    val fruitRot: Int = 0,
    val nutCracking: Int = 0,
    val sootyMold: Int = 0,
)

data class ScanDto(
    val id: String = "",
    val date: String = "",
    val block: String = "",
    val disease: String = "",
    val confidence: Double = 0.0,
    val severity: String = "",
    val status: String = "",
    @SerializedName("imageUrl") val imageUrl: String? = null,
)

data class DetectionSubmitDto(
    @SerializedName("job_id") val jobId: String = "",
    val status: String = "queued",
)

data class DetectionJobDto(
    @SerializedName("job_id") val jobId: String = "",
    val status: String = "queued",
    val progressPercent: Int = 0,
    val currentStage: String? = null,
    val result: DiagnosisDto? = null,
    val error: String? = null,
)

data class DiagnosisDto(
    val id: String = "",
    val disease: String = "Unknown",
    val confidence: Double = 0.0,
    val stage: String = "",
    val severity: String = "",
    val description: String = "",
    val treatments: List<String> = emptyList(),
    val organicControl: List<String> = emptyList(),
    val modelBreakdown: ModelBreakdownDto? = null,
    val tissueMorphometrics: TissueMorphometricsDto? = null,
    val differentialDiagnosis: List<DifferentialDto> = emptyList(),
    val featureMapUrl: String? = null,
    val attentionMapUrl: String? = null,
    val gradCamUrl: String? = null,
)

data class ModelBreakdownDto(
    val cnn: Double = 0.0,
    val vit: Double = 0.0,
    val yolo: Double = 0.0,
)

data class TissueMorphometricsDto(
    val healthyPct: Double = 0.0,
    val chloroticPct: Double = 0.0,
    val necroticPct: Double = 0.0,
    val lesionCoveragePct: Double = 0.0,
)

data class DifferentialDto(
    val disease: String = "",
    val probability: Double = 0.0,
)

data class DiseaseDto(
    val id: String = "",
    val name: String = "",
    val scientificName: String = "",
    val severity: String = "",
    val pathogenType: String = "",
    val description: String = "",
    val treatments: List<String> = emptyList(),
    val organicControl: List<String> = emptyList(),
)

data class PlantationBlockDto(
    val id: String = "",
    val name: String = "",
    val trees: Int = 0,
    val healthScore: Int = 0,
    val status: String = "",
    val primaryDisease: String = "",
    val lastScanned: String = "",
)

data class PlantationDto(
    val blocks: List<PlantationBlockDto> = emptyList(),
    val totalTrees: Int = 0,
    val totalAcres: Double = 0.0,
    val healthyTrees: Int = 0,
    val diseasedTrees: Int = 0,
    val overallHealthScore: Int = 0,
)

data class PlantationBlockRequestDto(
    val id: String? = null,
    val name: String,
    val trees: Int,
    val healthScore: Int = 100,
    val status: String = "Healthy",
    val primaryDisease: String = "None",
)

data class PlantationBlockUpdateDto(
    val healthScore: Int,
    val status: String,
    val primaryDisease: String,
)

data class FertilizerPlanDto(
    val standardsSource: String = "",
    val palms: Int = 0,
    val ageCategory: String = "mature",
    val annualRequirement: FertilizerRequirementDto = FertilizerRequirementDto(),
    val splitSchedule: FertilizerSplitScheduleDto? = null,
    val micronutrientRecommendations: MicronutrientDto? = null,
)

data class FertilizerRequirementDto(
    val ureaKg: Double = 0.0,
    val ureaBags50kg: Int = 0,
    val rockPhosphateKg: Double = 0.0,
    val rockPhosphateBags50kg: Int = 0,
    val muriateOfPotashKg: Double = 0.0,
    val mopBags50kg: Int = 0,
    val farmyardManureTons: Double = 0.0,
)

data class FertilizerSplitScheduleDto(
    val preMonsoonSplit: FertilizerSplitDto? = null,
    val postMonsoonSplit: FertilizerSplitDto? = null,
)

data class FertilizerSplitDto(
    val window: String = "",
    val share: String = "",
    val ureaGramsPerPalm: Int = 0,
    val rockPhosGramsPerPalm: Int = 0,
    val mopGramsPerPalm: Int = 0,
    val fymKgPerPalm: Int = 0,
)

data class MicronutrientDto(
    val boraxGramsPerPalm: Int = 0,
    val boraxIndication: String = "",
    val magnesiumSulphateGramsPerPalm: Int = 0,
    val magnesiumIndication: String = "",
    val zincSulphateGramsPerPalm: Int = 0,
    val zincIndication: String = "",
    val dolomiteLimeGramsPerPalm: Int = 0,
    val limeIndication: String = "",
)

data class PesticideRegistryDto(
    val source: String = "",
    val fungicides: List<PesticideGuideDto> = emptyList(),
    val insecticides: List<PesticideGuideDto> = emptyList(),
)

data class PesticideGuideDto(
    val target: String = "",
    val chemical: String = "",
    val alternative: String = "",
    val bioControl: String = "",
    val phiDays: Int = 0,
)

data class ForecastDto(
    val day: String = "",
    val tempMax: Int = 0,
    val tempMin: Int = 0,
    val condition: String = "",
    val rainProb: Int = 0,
)

data class WeatherDto(
    val city: String = "",
    val region: String = "",
    val temperature: Int = 0,
    val condition: String = "",
    val humidity: Int = 0,
    val windSpeed: Int = 0,
    val rainfall: Double = 0.0,
    val uvIndex: Int = 0,
    val riskLevel: String = "",
    val forecast: List<ForecastDto> = emptyList(),
)

data class RiskDto(
    val compositeIndex: Double = 0.0,
    val overallSeverity: String = "",
    val advisoryHeadline: String = "",
    val advisoryAction: String = "",
    val trajectory: List<RiskDayDto> = emptyList(),
    val blockVulnerability: List<BlockRiskDto> = emptyList(),
    val spraySchedule: SprayScheduleDto? = null,
)

data class RiskDayDto(
    val day: String = "",
    val date: String = "",
    val kolerogaRisk: Double = 0.0,
    val anthracnoseRisk: Double = 0.0,
    val nutCrackingRisk: Double = 0.0,
    val rainProbability: Int = 0,
)

data class BlockRiskDto(
    val name: String = "",
    val vulnerabilityScore: Double = 0.0,
    val primaryThreat: String = "",
    val severity: String = "",
)

data class SprayScheduleDto(
    val suitableWindow: String = "",
    val recommendedChemical: String = "",
    val organicAlternative: String = "",
    val withholdingPeriodDays: Int = 0,
)

data class NotificationsDto(
    val notifications: List<NotificationDto> = emptyList(),
    val unreadCount: Int = 0,
)

data class NotificationDto(
    val id: String = "",
    val type: String = "info",
    val title: String = "",
    val msg: String = "",
    val time: String = "",
    val unread: Boolean = false,
    val blockId: String? = null,
)

data class AssistantMessageDto(
    val id: String = "",
    val sender: String = "ai",
    val text: String = "",
    val timestamp: String = "",
    val suggestions: List<String> = emptyList(),
)

data class AssistantRequestDto(val message: String)

data class AssistantReplyDto(
    val reply: String = "",
    val suggestedActions: List<String> = emptyList(),
    val timestamp: String = "",
)
