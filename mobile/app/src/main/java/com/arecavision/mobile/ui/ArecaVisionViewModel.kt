package com.arecavision.mobile.ui

import android.content.Context
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.arecavision.mobile.data.ArecaRepository
import com.arecavision.mobile.data.AssistantMessageDto
import com.arecavision.mobile.data.DashboardDto
import com.arecavision.mobile.data.DiagnosisDto
import com.arecavision.mobile.data.DiseaseDto
import com.arecavision.mobile.data.DiseaseTrendDto
import com.arecavision.mobile.data.FertilizerPlanDto
import com.arecavision.mobile.data.PesticideRegistryDto
import com.arecavision.mobile.data.NotificationsDto
import com.arecavision.mobile.data.PlantationDto
import com.arecavision.mobile.data.RiskDto
import com.arecavision.mobile.data.ScanDto
import com.arecavision.mobile.data.WeatherDto
import kotlinx.coroutines.delay
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.UUID

private val availableBlocks = listOf(
    "block-a1" to "Block A-1 (North Valley)",
    "block-a2" to "Block A-2 (North Slope)",
    "block-b1" to "Block B-1 (Central Basin)",
    "block-c1" to "Block C-1 (River Bank)",
)

data class MobileUiState(
    val destination: String = "dashboard",
    val dashboard: DashboardDto? = null,
    val diseaseTrends: List<DiseaseTrendDto> = emptyList(),
    val scans: List<ScanDto> = emptyList(),
    val diseases: List<DiseaseDto> = emptyList(),
    val plantation: PlantationDto? = null,
    val weather: WeatherDto? = null,
    val risk: RiskDto? = null,
    val fertilizerPlan: FertilizerPlanDto? = null,
    val pesticideRegistry: PesticideRegistryDto? = null,
    val notifications: NotificationsDto? = null,
    val assistantMessages: List<AssistantMessageDto> = emptyList(),
    val isAssistantSending: Boolean = false,
    val selectedImage: Uri? = null,
    val selectedBlockId: String = availableBlocks.first().first,
    val selectedBlockName: String = availableBlocks.first().second,
    val isLoading: Boolean = false,
    val isAnalyzing: Boolean = false,
    val activeJobId: String? = null,
    val progress: Int = 0,
    val stage: String = "",
    val diagnosis: DiagnosisDto? = null,
    val error: String? = null,
)

class ArecaVisionViewModel(
    private val repository: ArecaRepository,
) : ViewModel() {
    private val _state = MutableStateFlow(MobileUiState())
    private var analysisJob: Job? = null
    val state = _state.asStateFlow()

    init {
        refresh()
    }

    fun navigate(destination: String) {
        _state.update { it.copy(destination = destination, error = null) }
        when (destination) {
            "history" -> refreshScans()
            "diseases" -> loadDiseases()
            "plantation" -> loadPlantation()
            "weather" -> loadWeather()
            "calculator", "pesticides" -> {
                loadFertilizerPlan(450)
                loadPesticideRegistry()
            }
            "assistant" -> loadAssistantHistory()
            "notifications" -> loadNotifications()
        }
    }

    fun setSelectedImage(uri: Uri) {
        _state.update { it.copy(selectedImage = uri, diagnosis = null, error = null) }
    }

    fun selectBlock(id: String) {
        val block = availableBlocks.firstOrNull { it.first == id } ?: return
        _state.update { it.copy(selectedBlockId = block.first, selectedBlockName = block.second) }
    }

    fun showError(message: String) {
        _state.update { it.copy(error = message) }
    }

    fun refresh() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }
            try {
                val dashboard = repository.dashboard()
                val trends = repository.diseaseTrends()
                _state.update { it.copy(dashboard = dashboard, diseaseTrends = trends) }
            } catch (exception: Exception) {
                _state.update { it.copy(error = exception.message ?: "Dashboard is unavailable.") }
            }
            refreshScans()
            _state.update { it.copy(isLoading = false) }
        }
    }

    private fun refreshScans() {
        viewModelScope.launch {
            try {
                val scans = repository.scans()
                _state.update { it.copy(scans = scans) }
            } catch (exception: Exception) {
                _state.update {
                    it.copy(error = it.error ?: (exception.message ?: "Scan history is unavailable."))
                }
            }
        }
    }

    private fun loadDiseases() {
        viewModelScope.launch {
            try {
                _state.update { it.copy(diseases = repository.diseases()) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Disease library is unavailable.")
            }
        }
    }

    private fun loadPlantation() {
        viewModelScope.launch {
            try {
                _state.update { it.copy(plantation = repository.plantation()) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Plantation data is unavailable.")
            }
        }
    }

    fun createPlantationBlock(name: String, trees: Int) {
        viewModelScope.launch {
            try {
                repository.createPlantationBlock(name.trim(), trees)
                _state.update { it.copy(plantation = repository.plantation()) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Could not add the plantation block.")
            }
        }
    }

    fun deletePlantationBlock(blockId: String) {
        viewModelScope.launch {
            try {
                repository.deletePlantationBlock(blockId)
                _state.update { current ->
                    current.copy(plantation = current.plantation?.let { plantation ->
                        plantation.copy(blocks = plantation.blocks.filterNot { it.id == blockId })
                    }) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Could not delete the plantation block.")
            }
        }
    }

    fun updatePlantationBlock(blockId: String, healthScore: Int, status: String, primaryDisease: String) {
        if (healthScore !in 0..100) return
        viewModelScope.launch {
            try {
                repository.updatePlantationBlock(blockId, healthScore, status.trim(), primaryDisease.trim())
                _state.update { it.copy(plantation = repository.plantation()) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Could not update the plantation block.")
            }
        }
    }

    fun loadFertilizerPlan(palms: Int) {
        if (palms !in 1..100000) return
        viewModelScope.launch {
            try {
                _state.update { it.copy(fertilizerPlan = repository.fertilizerPlan(palms, "mature"), error = null) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Fertilizer plan is unavailable.")
            }
        }
    }

    private fun loadPesticideRegistry() {
        viewModelScope.launch {
            try {
                _state.update { it.copy(pesticideRegistry = repository.pesticideRegistry()) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Pesticide recommendations are unavailable.")
            }
        }
    }

    private fun loadWeather() {
        viewModelScope.launch {
            try {
                val weather = repository.weather()
                val risk = repository.risk()
                _state.update { it.copy(weather = weather, risk = risk) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Weather and risk data are unavailable.")
            }
        }
    }

    private fun loadNotifications() {
        viewModelScope.launch {
            try {
                _state.update { it.copy(notifications = repository.notifications()) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Notifications are unavailable.")
            }
        }
    }

    private fun loadAssistantHistory() {
        viewModelScope.launch {
            try {
                _state.update { it.copy(assistantMessages = repository.assistantHistory()) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Assistant history is unavailable.")
            }
        }
    }

    fun sendAssistantMessage(message: String) {
        val trimmed = message.trim()
        if (trimmed.isEmpty() || _state.value.isAssistantSending) return
        val userMessage = AssistantMessageDto(
            id = UUID.randomUUID().toString(),
            sender = "user",
            text = trimmed,
        )
        _state.update { it.copy(assistantMessages = it.assistantMessages + userMessage, isAssistantSending = true) }
        viewModelScope.launch {
            try {
                val response = repository.sendAssistantMessage(trimmed)
                val assistantMessage = AssistantMessageDto(
                    id = UUID.randomUUID().toString(),
                    sender = "ai",
                    text = response.reply,
                    timestamp = response.timestamp,
                    suggestions = response.suggestedActions,
                )
                _state.update { it.copy(assistantMessages = it.assistantMessages + assistantMessage) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Could not send your question.")
            } finally {
                _state.update { it.copy(isAssistantSending = false) }
            }
        }
    }

    fun markAllNotificationsRead() {
        viewModelScope.launch {
            try {
                repository.markAllNotificationsRead()
                _state.update { current ->
                    val notifications = current.notifications ?: return@update current
                    current.copy(
                        notifications = notifications.copy(
                            unreadCount = 0,
                            notifications = notifications.notifications.map { it.copy(unread = false) },
                        ),
                    )
                }
            } catch (exception: Exception) {
                showError(exception.message ?: "Could not update notifications.")
            }
        }
    }

    fun markNotificationRead(notificationId: String) {
        viewModelScope.launch {
            try {
                repository.markNotificationRead(notificationId)
                _state.update { current ->
                    val notifications = current.notifications ?: return@update current
                    val updatedItems = notifications.notifications.map { item ->
                        if (item.id == notificationId) item.copy(unread = false) else item
                    }
                    current.copy(
                        notifications = notifications.copy(
                            notifications = updatedItems,
                            unreadCount = updatedItems.count { it.unread },
                        ),
                    )
                }
            } catch (exception: Exception) {
                showError(exception.message ?: "Could not update this notification.")
            }
        }
    }

    fun deleteScan(scanId: String) {
        viewModelScope.launch {
            try {
                repository.deleteScan(scanId)
                _state.update { it.copy(scans = it.scans.filterNot { scan -> scan.id == scanId }) }
            } catch (exception: Exception) {
                showError(exception.message ?: "Could not delete this scan.")
            }
        }
    }

    fun cancelAnalysis() {
        val jobId = _state.value.activeJobId
        if (jobId != null) {
            viewModelScope.launch { runCatching { repository.cancelJob(jobId) } }
        }
        analysisJob?.cancel()
        analysisJob = null
        _state.update { it.copy(isAnalyzing = false, activeJobId = null, progress = 0, stage = "") }
    }

    fun exportCsv(onReady: (ByteArray) -> Unit) {
        viewModelScope.launch {
            try {
                onReady(repository.exportCsv())
            } catch (exception: Exception) {
                showError(exception.message ?: "Could not export scan history.")
            }
        }
    }

    fun analyze(imageBytes: ByteArray) {
        if (_state.value.isAnalyzing) return
        analysisJob = viewModelScope.launch {
            _state.update {
                it.copy(
                    isAnalyzing = true,
                    progress = 10,
                    stage = "Uploading image",
                    diagnosis = null,
                    error = null,
                )
            }
            try {
                val submit = repository.submitDetection(imageBytes, _state.value.selectedBlockId)
                _state.update { it.copy(activeJobId = submit.jobId) }
                var attempts = 0
                while (attempts < 80) {
                    delay(700)
                    val job = repository.job(submit.jobId)
                    _state.update {
                        it.copy(progress = job.progressPercent, stage = job.currentStage ?: job.status)
                    }
                    if (job.status == "done") {
                        val result = job.result ?: error("The completed job did not include a diagnosis.")
                        _state.update { it.copy(isAnalyzing = false, activeJobId = null, progress = 100, diagnosis = result) }
                        refreshScans()
                        return@launch
                    }
                    if (job.status == "failed") error(job.error ?: "Diagnosis failed.")
                    attempts++
                }
                error("Diagnosis timed out. Check the backend and try again.")
            } catch (exception: CancellationException) {
                throw exception
            } catch (exception: Exception) {
                _state.update {
                    it.copy(isAnalyzing = false, activeJobId = null, error = exception.message ?: "Diagnosis failed.")
                }
            }
        }
    }
}

class ArecaVisionViewModelFactory(private val context: Context) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(ArecaVisionViewModel::class.java)) {
            return ArecaVisionViewModel(ArecaRepository(context)) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class: ${modelClass.name}")
    }
}
