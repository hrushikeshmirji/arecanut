package com.arecavision.mobile

import android.net.Uri
import android.os.Bundle
import android.speech.tts.TextToSpeech
import androidx.core.content.FileProvider
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.viewmodel.compose.viewModel
import com.arecavision.mobile.ui.ArecaVisionApp
import com.arecavision.mobile.ui.ArecaVisionViewModel
import com.arecavision.mobile.ui.ArecaVisionViewModelFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.util.Locale

class MainActivity : ComponentActivity() {
    private var textToSpeech: TextToSpeech? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        textToSpeech = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                textToSpeech?.language = Locale.US
            }
        }
        val factory = ArecaVisionViewModelFactory(applicationContext)
        setContent {
            MaterialTheme {
                val viewModel: ArecaVisionViewModel = viewModel(factory = factory)
                val state by viewModel.state.collectAsState()
                var cameraOutput by remember { mutableStateOf<Uri?>(null) }
                val imagePicker = rememberLauncherForActivityResult(
                    contract = ActivityResultContracts.GetContent(),
                ) { uri: Uri? ->
                    if (uri != null) {
                        viewModel.setSelectedImage(uri)
                    }
                }
                val cameraCapture = rememberLauncherForActivityResult(
                    contract = ActivityResultContracts.TakePicture(),
                ) { captured ->
                    if (captured) cameraOutput?.let(viewModel::setSelectedImage)
                }
                val csvExporter = rememberLauncherForActivityResult(
                    contract = ActivityResultContracts.CreateDocument("text/csv"),
                ) { uri: Uri? ->
                    if (uri != null) {
                        viewModel.exportCsv { bytes ->
                            lifecycleScope.launch(Dispatchers.IO) {
                                contentResolver.openOutputStream(uri)?.use { it.write(bytes) }
                            }
                        }
                    }
                }

                ArecaVisionApp(
                    state = state,
                    onNavigate = viewModel::navigate,
                    onChooseImage = { imagePicker.launch("image/*") },
                    onTakePhoto = {
                        val photoDirectory = File(cacheDir, "specimens").apply { mkdirs() }
                        val photoFile = File(photoDirectory, "specimen-${System.currentTimeMillis()}.jpg")
                        cameraOutput = FileProvider.getUriForFile(
                            this@MainActivity,
                            "${BuildConfig.APPLICATION_ID}.fileprovider",
                            photoFile,
                        )
                        cameraOutput?.let(cameraCapture::launch)
                    },
                    onAnalyze = { uri ->
                        lifecycleScope.launch {
                            val bytes = withContext(Dispatchers.IO) {
                                contentResolver.openInputStream(uri)?.use { it.readBytes() }
                            }
                            if (bytes != null) viewModel.analyze(bytes)
                            else viewModel.showError("Could not read the selected image.")
                        }
                    },
                    onSpeak = { text ->
                        textToSpeech?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "arecavision-briefing")
                    },
                    onCancelAnalysis = viewModel::cancelAnalysis,
                    onBlockSelected = viewModel::selectBlock,
                    onRetry = viewModel::refresh,
                    onSendAssistantMessage = viewModel::sendAssistantMessage,
                    onMarkAllNotificationsRead = viewModel::markAllNotificationsRead,
                    onMarkNotificationRead = viewModel::markNotificationRead,
                    onDeleteScan = viewModel::deleteScan,
                    onExportCsv = { csvExporter.launch("arecavision-scan-report.csv") },
                    onCreateBlock = viewModel::createPlantationBlock,
                    onDeleteBlock = viewModel::deletePlantationBlock,
                    onCalculateFertilizer = viewModel::loadFertilizerPlan,
                    onUpdateBlock = viewModel::updatePlantationBlock,
                )
            }
        }
    }

    override fun onDestroy() {
        textToSpeech?.stop()
        textToSpeech?.shutdown()
        textToSpeech = null
        super.onDestroy()
    }
}
