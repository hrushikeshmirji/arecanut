package com.arecavision.mobile.ui

import android.content.ContentResolver
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.util.Base64
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.FilterChip
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.foundation.rememberScrollState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.arecavision.mobile.BuildConfig
import com.arecavision.mobile.data.DashboardDto
import com.arecavision.mobile.data.DiagnosisDto
import com.arecavision.mobile.data.DiseaseTrendDto
import com.arecavision.mobile.data.ScanDto
import java.text.SimpleDateFormat
import java.util.Locale
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

private val Green = Color(0xFF0D7657)
private val Ink = Color(0xFF17231E)
private val Mist = Color(0xFFF3F6F0)

@Composable
fun ArecaVisionApp(
    state: MobileUiState,
    onNavigate: (String) -> Unit,
    onChooseImage: () -> Unit,
    onTakePhoto: () -> Unit,
    onAnalyze: (Uri) -> Unit,
    onCancelAnalysis: () -> Unit,
    onSpeak: (String) -> Unit,
    onBlockSelected: (String) -> Unit,
    onRetry: () -> Unit,
    onSendAssistantMessage: (String) -> Unit,
    onMarkAllNotificationsRead: () -> Unit,
    onMarkNotificationRead: (String) -> Unit,
    onDeleteScan: (String) -> Unit,
    onExportCsv: () -> Unit,
    onCreateBlock: (String, Int) -> Unit,
    onDeleteBlock: (String) -> Unit,
    onCalculateFertilizer: (Int) -> Unit,
    onUpdateBlock: (String, Int, String, String) -> Unit,
) {
    MaterialTheme(
        colorScheme = MaterialTheme.colorScheme.copy(
            primary = Green,
            secondary = Color(0xFFE0A533),
            background = Mist,
            surface = Color.White,
            onSurface = Ink,
        ),
    ) {
        Scaffold(
            containerColor = Mist,
            bottomBar = {
                NavigationBar(containerColor = Color.White) {
                    listOf("dashboard" to "Overview", "detection" to "Diagnose", "history" to "History", "more" to "More").forEach { (route, label) ->
                        NavigationBarItem(
                            selected = state.destination == route,
                            onClick = { onNavigate(route) },
                            icon = { Text(when (route) { "dashboard" -> "⌂"; "detection" -> "✳"; "history" -> "◷"; else -> "•••" }) },
                            label = { Text(label) },
                        )
                    }
                }
            },
        ) { padding ->
            Column(Modifier.fillMaxSize().padding(padding)) {
                AppHeader()
                when (state.destination) {
                    "detection" -> DetectionScreen(state, onChooseImage, onTakePhoto, onAnalyze, onBlockSelected, onCancelAnalysis, onSpeak)
                    "history" -> HistoryScreen(state.scans, state.isLoading, onDeleteScan)
                    "more" -> MoreScreen(onNavigate)
                    "diseases" -> DiseaseLibraryScreen(state.diseases, state.error)
                    "plantation" -> PlantationScreen(state.plantation, state.error, onCreateBlock, onDeleteBlock, onUpdateBlock)
                    "weather" -> WeatherScreen(state.weather, state.risk, state.error)
                    "assistant" -> AssistantScreen(state, onSendAssistantMessage)
                    "notifications" -> NotificationsScreen(state.notifications, state.error, onMarkAllNotificationsRead, onMarkNotificationRead)
                    "reports" -> ReportsScreen(state.scans.size, state.error, onExportCsv)
                    "calculator" -> FertilizerCalculatorScreen(state, onCalculateFertilizer)
                    "pesticides" -> PesticideCalculatorScreen(state.pesticideRegistry, state.error)
                    "settings" -> SettingsScreen()
                    else -> DashboardScreen(state.dashboard, state.diseaseTrends, state.scans.take(4), state.error, onRetry) {
                        onNavigate("detection")
                    }
                }
            }
        }
    }
}

@Composable
private fun AppHeader() {
    Row(
        modifier = Modifier.fillMaxWidth().background(Color.White).padding(horizontal = 20.dp, vertical = 16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier = Modifier.size(42.dp).clip(RoundedCornerShape(14.dp)).background(Green),
            contentAlignment = Alignment.Center,
        ) { Text("A", color = Color.White, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black) }
        Spacer(Modifier.width(12.dp))
        Column {
            Text("ArecaVision", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = Ink)
            Text("FIELD DIAGNOSTICS", style = MaterialTheme.typography.labelSmall, color = Green)
        }
    }
}

@Composable
private fun DashboardScreen(
    dashboard: DashboardDto?,
    trends: List<DiseaseTrendDto>,
    recentScans: List<ScanDto>,
    error: String?,
    onRetry: () -> Unit,
    onDiagnose: () -> Unit,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(18.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            Column {
                Text("Plant health, at a glance", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = Ink)
                Text("Arecanut diagnostics and field guidance", color = Color(0xFF617067))
            }
        }
        if (error != null && dashboard == null) {
            item { ErrorPanel(error, onRetry) }
        }
        if (dashboard != null) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        MetricCard("HEALTH SCORE", "${dashboard.overallHealthScore ?: 0}%", "Plantation vitality", Modifier.weight(1f))
                        MetricCard("TOTAL PALMS", dashboard.totalTrees.toString(), "Across all blocks", Modifier.weight(1f))
                    }
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        MetricCard("DISEASE WATCH", dashboard.diseasedTrees.toString(), "Palms at risk", Modifier.weight(1f))
                        MetricCard("FIELD ALERTS", dashboard.pendingAlertsCount.toString(), "Need attention", Modifier.weight(1f))
                    }
                }
            }
            item { DiseaseTrendChart(trends) }
        } else if (error == null) {
            item { LoadingPanel() }
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Green), shape = RoundedCornerShape(22.dp)) {
                Column(Modifier.fillMaxWidth().padding(20.dp)) {
                    Text("A field check starts with one photo.", color = Color.White, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(6.dp))
                    Text("Run an arecanut health scan and review treatment guidance.", color = Color.White.copy(alpha = 0.82f))
                    Spacer(Modifier.height(16.dp))
                    Button(onClick = onDiagnose) { Text("Start a diagnosis") }
                }
            }
        }
        item { Text("Recent field scans", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = Ink) }
        if (recentScans.isEmpty()) {
            item { Text("No recent scans yet.", color = Color(0xFF617067)) }
        } else {
            items(recentScans, key = { it.id }) { ScanRow(it) }
        }
    }
}

@Composable
private fun MetricCard(label: String, value: String, caption: String, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = Color.White),
        shape = RoundedCornerShape(18.dp),
    ) {
        Column(Modifier.padding(15.dp)) {
            Text(label, style = MaterialTheme.typography.labelSmall, color = Color(0xFF66756C), fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(7.dp))
            Text(value, style = MaterialTheme.typography.headlineSmall, color = Green, fontWeight = FontWeight.Bold)
            Text(caption, style = MaterialTheme.typography.bodySmall, color = Color(0xFF66756C), maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
    }
}

@Composable
private fun DiseaseTrendChart(trends: List<DiseaseTrendDto>) {
    val series = listOf(
        Triple("Anthracnose", Color(0xFF0D7657), trends.map { it.anthracnose }),
        Triple("Koleroga", Color(0xFFCB6A36), trends.map { it.koleroga }),
        Triple("Nut cracking", Color(0xFF5579A8), trends.map { it.nutCracking }),
        Triple("Sooty mold", Color(0xFF8A6D9F), trends.map { it.sootyMold }),
    )
    Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(18.dp)) {
        Column(Modifier.fillMaxWidth().padding(15.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("Disease activity", color = Ink, fontWeight = FontWeight.Bold)
            if (trends.size < 2) {
                Text("Trend data is not available yet.", color = Color(0xFF617067), style = MaterialTheme.typography.bodySmall)
            } else {
                val maximum = series.flatMap { it.third }.maxOrNull()?.toFloat()?.coerceAtLeast(1f) ?: 1f
                Canvas(Modifier.fillMaxWidth().height(150.dp)) {
                    val xStep = size.width / (trends.size - 1).toFloat()
                    for (lineIndex in 0..3) {
                        val y = size.height * lineIndex / 3f
                        drawLine(Color(0xFFE8ECE8), Offset(0f, y), Offset(size.width, y), strokeWidth = 1.dp.toPx())
                    }
                    series.forEach { (_, color, values) ->
                        val points = values.mapIndexed { index, value ->
                            Offset(index * xStep, size.height - (value / maximum) * size.height)
                        }
                        points.zipWithNext().forEach { (start, end) ->
                            drawLine(color, start, end, strokeWidth = 2.5.dp.toPx())
                        }
                        points.forEach { point -> drawCircle(color, radius = 3.5.dp.toPx(), center = point) }
                    }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    series.forEach { (label, color, _) ->
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            Box(Modifier.size(7.dp).clip(CircleShape).background(color))
                            Text(label, color = Color(0xFF617067), style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(trends.first().date, color = Color(0xFF617067), style = MaterialTheme.typography.labelSmall)
                    Text(trends.last().date, color = Color(0xFF617067), style = MaterialTheme.typography.labelSmall)
                }
            }
        }
    }
}

@Composable
private fun DetectionScreen(
    state: MobileUiState,
    onChooseImage: () -> Unit,
    onTakePhoto: () -> Unit,
    onAnalyze: (Uri) -> Unit,
    onBlockSelected: (String) -> Unit,
    onCancelAnalysis: () -> Unit,
    onSpeak: (String) -> Unit,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(18.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            Column {
                Text("New diagnosis", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = Ink)
                Text("Upload a clear photo of a leaf, nut bunch, or trunk.", color = Color(0xFF617067))
            }
        }
        item {
            BlockPicker(state.selectedBlockName, onBlockSelected)
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(20.dp)) {
                Column(Modifier.fillMaxWidth().padding(18.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("SPECIMEN PHOTO", style = MaterialTheme.typography.labelMedium, color = Green, fontWeight = FontWeight.Bold)
                    Text(
                        state.selectedImage?.lastPathSegment ?: "Choose a photo from your device",
                        color = Ink,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                    state.selectedImage?.let { SelectedPhotoPreview(it) }
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedButton(onClick = onChooseImage, modifier = Modifier.weight(1f)) { Text("Gallery") }
                        OutlinedButton(onClick = onTakePhoto, modifier = Modifier.weight(1f)) { Text("Camera") }
                    }
                    Button(
                        onClick = { state.selectedImage?.let(onAnalyze) },
                        enabled = state.selectedImage != null && !state.isAnalyzing,
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text(if (state.isAnalyzing) "Scanning..." else "Run diagnosis") }
                    if (state.isAnalyzing) {
                        LinearProgressIndicator(progress = { state.progress.coerceIn(0, 100) / 100f }, modifier = Modifier.fillMaxWidth())
                        Text("${state.progress}% · ${state.stage}", color = Color(0xFF617067), style = MaterialTheme.typography.bodySmall)
                        TextButton(onClick = onCancelAnalysis, modifier = Modifier.align(Alignment.End)) { Text("Cancel scan") }
                    }
                    state.error?.let { Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall) }
                }
            }
        }
        state.diagnosis?.let { diagnosis ->
            item { DiagnosisCard(diagnosis, onSpeak) }
        }
    }
}

@Composable
private fun BlockPicker(selectedName: String, onBlockSelected: (String) -> Unit) {
    var expanded by remember { mutableStateOf(false) }
    val blocks = listOf(
        "block-a1" to "Block A-1 (North Valley)",
        "block-a2" to "Block A-2 (North Slope)",
        "block-b1" to "Block B-1 (Central Basin)",
        "block-c1" to "Block C-1 (River Bank)",
    )
    Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(16.dp)) {
        Box {
            TextButton(onClick = { expanded = true }, modifier = Modifier.fillMaxWidth()) {
                Text("TARGET BLOCK   ·   $selectedName", color = Ink, maxLines = 1, overflow = TextOverflow.Ellipsis)
            }
            DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
                blocks.forEach { (id, name) ->
                    DropdownMenuItem(text = { Text(name) }, onClick = { onBlockSelected(id); expanded = false })
                }
            }
        }
    }
}

@Composable
private fun DiagnosisCard(diagnosis: DiagnosisDto, onSpeak: (String) -> Unit) {
    Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(20.dp)) {
        Column(Modifier.fillMaxWidth().padding(18.dp), verticalArrangement = Arrangement.spacedBy(9.dp)) {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text("DIAGNOSIS COMPLETE", modifier = Modifier.weight(1f), style = MaterialTheme.typography.labelMedium, color = Green, fontWeight = FontWeight.Bold)
                TextButton(onClick = {
                    val actions = diagnosis.treatments.joinToString(". ")
                    onSpeak("${diagnosis.disease}. ${diagnosis.confidence} percent confidence. ${diagnosis.description} Recommended actions: $actions")
                }) { Text("Listen") }
            }
            Text(diagnosis.disease, style = MaterialTheme.typography.headlineSmall, color = Ink, fontWeight = FontWeight.Bold)
            Text("${diagnosis.confidence}% confidence · ${diagnosis.severity}", color = Green, fontWeight = FontWeight.SemiBold)
            Text(diagnosis.description, color = Color(0xFF536158))
            diagnosis.modelBreakdown?.let { metrics ->
                Text("Model signals", fontWeight = FontWeight.Bold, color = Ink)
                Text("Gatekeeper ${metrics.cnn}% · ViT ${metrics.vit}% · YOLO ${metrics.yolo}%", color = Color(0xFF536158), style = MaterialTheme.typography.bodySmall)
            }
            diagnosis.tissueMorphometrics?.let { tissue ->
                Text("Tissue observations", fontWeight = FontWeight.Bold, color = Ink)
                Text("Healthy ${tissue.healthyPct}% · Chlorotic ${tissue.chloroticPct}% · Necrotic ${tissue.necroticPct}%", color = Color(0xFF536158), style = MaterialTheme.typography.bodySmall)
                Text("Estimated lesion coverage ${tissue.lesionCoveragePct}%", color = Color(0xFF536158), style = MaterialTheme.typography.bodySmall)
            }
            if (diagnosis.differentialDiagnosis.isNotEmpty()) {
                Text("Other possible classes", fontWeight = FontWeight.Bold, color = Ink)
                diagnosis.differentialDiagnosis.take(3).forEach { candidate ->
                    Text("${candidate.disease.replace('_', ' ')} · ${candidate.probability}%", color = Color(0xFF536158), style = MaterialTheme.typography.bodySmall)
                }
            }
            if (diagnosis.treatments.isNotEmpty()) {
                Spacer(Modifier.height(4.dp))
                Text("Recommended actions", fontWeight = FontWeight.Bold, color = Ink)
                diagnosis.treatments.forEach { Text("•  $it", color = Color(0xFF536158)) }
            }
            listOf(
                "Feature map" to diagnosis.featureMapUrl,
                "Attention rollout" to diagnosis.attentionMapUrl,
                "Grad-CAM" to diagnosis.gradCamUrl,
            ).forEach { (title, dataUrl) ->
                if (!dataUrl.isNullOrBlank()) ExplainabilityImage(title, dataUrl)
            }
        }
    }
}

@Composable
private fun SelectedPhotoPreview(uri: Uri) {
    val context = LocalContext.current
    val bitmap by produceState<Bitmap?>(initialValue = null, key1 = uri) {
        value = withContext(Dispatchers.IO) {
            decodeSampledBitmap(context.contentResolver, uri, 900)
        }
    }
    bitmap?.let {
        Image(
            bitmap = it.asImageBitmap(),
            contentDescription = "Selected arecanut specimen",
            modifier = Modifier.fillMaxWidth().height(220.dp).clip(RoundedCornerShape(14.dp)),
            contentScale = ContentScale.Crop,
        )
    }
}

@Composable
private fun ExplainabilityImage(title: String, dataUrl: String) {
    val bitmap by produceState<Bitmap?>(initialValue = null, key1 = dataUrl) {
        value = withContext(Dispatchers.IO) { decodeDataImage(dataUrl) }
    }
    Column(verticalArrangement = Arrangement.spacedBy(5.dp)) {
        Text(title, color = Ink, fontWeight = FontWeight.Bold)
        bitmap?.let {
            Image(
                bitmap = it.asImageBitmap(),
                contentDescription = title,
                modifier = Modifier.fillMaxWidth().aspectRatio(1.5f).clip(RoundedCornerShape(12.dp)),
                contentScale = ContentScale.Crop,
            )
        } ?: Text("Image unavailable", color = Color(0xFF617067), style = MaterialTheme.typography.bodySmall)
    }
}

private fun decodeSampledBitmap(resolver: ContentResolver, uri: Uri, maxDimension: Int): Bitmap? {
    val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
    resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, bounds) }
    if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return null

    val sampleSize = maxOf(1, bounds.outWidth / maxDimension, bounds.outHeight / maxDimension)
    val options = BitmapFactory.Options().apply { inSampleSize = sampleSize }
    return resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, options) }
}

private fun decodeDataImage(dataUrl: String): Bitmap? = runCatching {
    val encoded = dataUrl.substringAfter(',', dataUrl)
    val bytes = Base64.decode(encoded, Base64.DEFAULT)
    BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
}.getOrNull()

@Composable
private fun HistoryScreen(scans: List<ScanDto>, isLoading: Boolean, onDelete: (String) -> Unit) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(18.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item {
            Column {
                Text("Scan history", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = Ink)
                Text("Recent diagnoses from the plantation database", color = Color(0xFF617067))
            }
        }
        if (isLoading) item { LoadingPanel() }
        if (!isLoading && scans.isEmpty()) item { Text("No scans found.", color = Color(0xFF617067)) }
        items(scans, key = { it.id }) { ScanRow(it, onDelete) }
    }
}

@Composable
private fun ScanRow(scan: ScanDto, onDelete: ((String) -> Unit)? = null) {
    Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(16.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(15.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(Modifier.size(42.dp).clip(CircleShape).background(Green.copy(alpha = 0.11f)), contentAlignment = Alignment.Center) {
                Text(scan.disease.take(1).uppercase(), color = Green, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(scan.disease.replace('_', ' ').replaceFirstChar { it.uppercase() }, color = Ink, fontWeight = FontWeight.Bold)
                Text("${scan.block} · ${formatDate(scan.date)}", color = Color(0xFF66756C), style = MaterialTheme.typography.bodySmall)
            }
            Column(horizontalAlignment = Alignment.End) {
                Text("${scan.confidence}%", color = Green, fontWeight = FontWeight.Bold)
                Text(scan.severity, color = Color(0xFF66756C), style = MaterialTheme.typography.labelSmall)
            }
            if (onDelete != null) {
                TextButton(onClick = { onDelete(scan.id) }) { Text("Delete") }
            }
        }
    }
}

@Composable
private fun LoadingPanel() {
    Box(Modifier.fillMaxWidth().padding(24.dp), contentAlignment = Alignment.Center) {
        CircularProgressIndicator(color = Green, modifier = Modifier.size(28.dp), strokeWidth = 3.dp)
    }
}

@Composable
private fun ErrorPanel(message: String, onRetry: () -> Unit) {
    Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(18.dp)) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text("Could not reach ArecaVision", color = MaterialTheme.colorScheme.error, fontWeight = FontWeight.Bold)
            Text(message, color = Color(0xFF617067), style = MaterialTheme.typography.bodySmall)
            TextButton(onClick = onRetry) { Text("Retry") }
        }
    }
}

@Composable
private fun MoreScreen(onNavigate: (String) -> Unit) {
    val destinations = listOf(
        "plantation" to ("Plantation blocks" to "Tree counts, health, and active block conditions"),
        "diseases" to ("Disease library" to "Symptoms, severity, and field recommendations"),
        "weather" to ("Weather & risk" to "Microclimate observations and disease outlook"),
        "assistant" to ("Agronomy assistant" to "Ask a question about arecanut care"),
        "notifications" to ("Field alerts" to "Unread risk notices and scan alerts"),
        "reports" to ("Field reports" to "Export scan history as a CSV file"),
        "calculator" to ("Treatment calculator" to "Estimate annual ICAR-CPCRI fertilizer quantities"),
        "pesticides" to ("Spray estimator" to "Estimate spray volume and review approved field guidance"),
        "settings" to ("Settings" to "Language and connection preferences"),
    )
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(18.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item {
            Column(Modifier.padding(bottom = 4.dp)) {
                Text("Field tools", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = Ink)
                Text("More of ArecaVision", color = Color(0xFF617067))
            }
        }
        items(destinations) { (route, details) ->
            Card(
                modifier = Modifier.fillMaxWidth().clickable { onNavigate(route) },
                colors = CardDefaults.cardColors(containerColor = Color.White),
                shape = RoundedCornerShape(16.dp),
            ) {
                Row(Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) {
                        Text(details.first, color = Ink, fontWeight = FontWeight.Bold)
                        Text(details.second, color = Color(0xFF617067), style = MaterialTheme.typography.bodySmall)
                    }
                    Text("›", color = Green, style = MaterialTheme.typography.headlineSmall)
                }
            }
        }
    }
}

@Composable
private fun DiseaseLibraryScreen(diseases: List<com.arecavision.mobile.data.DiseaseDto>, error: String?) {
    var query by remember { mutableStateOf("") }
    var selectedSeverity by remember { mutableStateOf("All") }
    val filteredDiseases = remember(diseases, query, selectedSeverity) {
        diseases.filter { disease ->
            val searchMatches = listOf(disease.name, disease.scientificName, disease.description, disease.pathogenType, disease.id)
                .any { it.contains(query.trim(), ignoreCase = true) }
            val severityMatches = selectedSeverity == "All" || disease.severity.equals(selectedSeverity, ignoreCase = true)
            searchMatches && severityMatches
        }
    }
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(18.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item { SectionTitle("Disease library", "Field signs and recommended control") }
        item {
            TextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("Search disease or pathogen") },
                singleLine = true,
            )
        }
        item {
            Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("All", "Critical", "Severe", "Moderate", "Mild", "Healthy").forEach { severity ->
                    FilterChip(
                        selected = selectedSeverity == severity,
                        onClick = { selectedSeverity = severity },
                        label = { Text(severity) },
                    )
                }
            }
        }
        if (error != null && diseases.isEmpty()) item { Text(error, color = MaterialTheme.colorScheme.error) }
        if (diseases.isEmpty() && error == null) item { LoadingPanel() }
        if (diseases.isNotEmpty() && filteredDiseases.isEmpty()) {
            item { Text("No diseases match this search.", color = Color(0xFF617067)) }
        }
        items(filteredDiseases, key = { it.id }) { disease ->
            Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(18.dp)) {
                Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(disease.name, modifier = Modifier.weight(1f), color = Ink, fontWeight = FontWeight.Bold)
                        Text(disease.severity, color = Green, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold)
                    }
                    if (disease.scientificName.isNotBlank()) Text(disease.scientificName, color = Color(0xFF617067), style = MaterialTheme.typography.bodySmall)
                    Text(disease.description, color = Ink, style = MaterialTheme.typography.bodySmall)
                    disease.treatments.take(2).forEach { Text("•  $it", color = Color(0xFF536158), style = MaterialTheme.typography.bodySmall) }
                }
            }
        }
    }
}

@Composable
private fun PlantationScreen(
    plantation: com.arecavision.mobile.data.PlantationDto?,
    error: String?,
    onCreateBlock: (String, Int) -> Unit,
    onDeleteBlock: (String) -> Unit,
    onUpdateBlock: (String, Int, String, String) -> Unit,
) {
    var showAddDialog by remember { mutableStateOf(false) }
    var pendingDeleteId by remember { mutableStateOf<String?>(null) }
    var pendingEditBlock by remember { mutableStateOf<com.arecavision.mobile.data.PlantationBlockDto?>(null) }

    Box(Modifier.fillMaxSize()) {
        PlantationContent(
            plantation = plantation,
            error = error,
            onAddBlock = { showAddDialog = true },
            onDeleteBlock = { pendingDeleteId = it },
            onEditBlock = { pendingEditBlock = it },
        )
        if (showAddDialog) {
            AddBlockDialog(
                onDismiss = { showAddDialog = false },
                onConfirm = { name, trees ->
                    showAddDialog = false
                    onCreateBlock(name, trees)
                },
            )
        }
        pendingDeleteId?.let { blockId ->
            AlertDialog(
                onDismissRequest = { pendingDeleteId = null },
                title = { Text("Delete plantation block?") },
                text = { Text("This removes the block from the shared plantation registry.") },
                confirmButton = {
                    TextButton(onClick = { pendingDeleteId = null; onDeleteBlock(blockId) }) {
                        Text("Delete", color = MaterialTheme.colorScheme.error)
                    }
                },
                dismissButton = { TextButton(onClick = { pendingDeleteId = null }) { Text("Cancel") } },
            )
        }
        pendingEditBlock?.let { block ->
            EditBlockDialog(
                block = block,
                onDismiss = { pendingEditBlock = null },
                onConfirm = { health, status, disease ->
                    pendingEditBlock = null
                    onUpdateBlock(block.id, health, status, disease)
                },
            )
        }
    }
}

@Composable
private fun PlantationContent(
    plantation: com.arecavision.mobile.data.PlantationDto?,
    error: String?,
    onAddBlock: () -> Unit,
    onDeleteBlock: (String) -> Unit,
    onEditBlock: (com.arecavision.mobile.data.PlantationBlockDto) -> Unit,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(18.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item { SectionTitle("Plantation", "Blocks in your field registry") }
        item {
            Button(onClick = onAddBlock, modifier = Modifier.fillMaxWidth()) { Text("Add plantation block") }
        }
        if (error != null && plantation == null) item { Text(error, color = MaterialTheme.colorScheme.error) }
        if (plantation != null) {
            val summary = plantation
            item {
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    MetricCard("PALMS", summary.totalTrees.toString(), "Registered", Modifier.weight(1f))
                    MetricCard("AREA", "${summary.totalAcres}", "Acres", Modifier.weight(1f))
                }
            }
            item { Text("${summary.overallHealthScore}% overall health", color = Green, fontWeight = FontWeight.Bold) }
            items(summary.blocks, key = { it.id }) { block ->
                Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(16.dp)) {
                    Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(block.name, modifier = Modifier.weight(1f), color = Ink, fontWeight = FontWeight.Bold)
                            Text(block.status, color = Green, style = MaterialTheme.typography.labelSmall)
                        }
                        Text("${block.trees} palms · ${block.healthScore}% health", color = Color(0xFF617067))
                        Text("Primary concern: ${block.primaryDisease}", color = Color(0xFF536158), style = MaterialTheme.typography.bodySmall)
                        Row {
                            TextButton(onClick = { onEditBlock(block) }) { Text("Edit") }
                            TextButton(onClick = { onDeleteBlock(block.id) }) { Text("Delete block") }
                        }
                    }
                }
            }
        } else if (error == null) {
            item { LoadingPanel() }
        }
    }
}

@Composable
private fun AddBlockDialog(onDismiss: () -> Unit, onConfirm: (String, Int) -> Unit) {
    var name by remember { mutableStateOf("") }
    var treeCount by remember { mutableStateOf("") }
    val parsedTreeCount = treeCount.toIntOrNull()
    val canSubmit = name.isNotBlank() && parsedTreeCount != null && parsedTreeCount > 0

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Add plantation block") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                TextField(value = name, onValueChange = { name = it }, label = { Text("Block name") }, singleLine = true)
                TextField(value = treeCount, onValueChange = { treeCount = it.filter(Char::isDigit) }, label = { Text("Number of palms") }, singleLine = true)
                if (treeCount.isNotEmpty() && parsedTreeCount == null) {
                    Text("Enter a valid palm count.", color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall)
                }
            }
        },
        confirmButton = {
            TextButton(
                enabled = canSubmit,
                onClick = { parsedTreeCount?.let { onConfirm(name.trim(), it) } },
            ) { Text("Add block") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } },
    )
}

@Composable
private fun EditBlockDialog(
    block: com.arecavision.mobile.data.PlantationBlockDto,
    onDismiss: () -> Unit,
    onConfirm: (Int, String, String) -> Unit,
) {
    var healthScore by remember(block.id) { mutableStateOf(block.healthScore.toString()) }
    var status by remember(block.id) { mutableStateOf(block.status) }
    var primaryDisease by remember(block.id) { mutableStateOf(block.primaryDisease) }
    val parsedHealth = healthScore.toIntOrNull()?.takeIf { it in 0..100 }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Edit ${block.name}") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                TextField(value = healthScore, onValueChange = { healthScore = it.filter(Char::isDigit) }, label = { Text("Health score (0-100)") }, singleLine = true)
                TextField(value = status, onValueChange = { status = it }, label = { Text("Status") }, singleLine = true)
                TextField(value = primaryDisease, onValueChange = { primaryDisease = it }, label = { Text("Primary concern") }, singleLine = true)
            }
        },
        confirmButton = {
            TextButton(
                enabled = parsedHealth != null && status.isNotBlank(),
                onClick = { parsedHealth?.let { onConfirm(it, status.trim(), primaryDisease.trim()) } },
            ) { Text("Save") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } },
    )
}

@Composable
private fun WeatherScreen(
    weather: com.arecavision.mobile.data.WeatherDto?,
    risk: com.arecavision.mobile.data.RiskDto?,
    error: String?,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(18.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item { SectionTitle("Weather & disease risk", "Local microclimate and seven-day outlook") }
        if (error != null && weather == null) item { Text(error, color = MaterialTheme.colorScheme.error) }
        weather?.let { current ->
            item {
                Card(colors = CardDefaults.cardColors(containerColor = Green), shape = RoundedCornerShape(20.dp)) {
                    Column(Modifier.fillMaxWidth().padding(18.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                        Text(current.city, color = Color.White, fontWeight = FontWeight.Bold)
                        Text("${current.temperature}° · ${current.condition}", color = Color.White, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                        Text("Humidity ${current.humidity}% · Rain ${current.rainfall} mm · ${current.riskLevel} risk", color = Color.White.copy(alpha = 0.85f))
                    }
                }
            }
            item { Text("Forecast", color = Ink, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold) }
            items(current.forecast) { day ->
                Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(14.dp)) {
                    Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                        Text(day.day, modifier = Modifier.weight(1f), color = Ink, fontWeight = FontWeight.Bold)
                        Text("${day.tempMin}°–${day.tempMax}° · ${day.rainProb}% rain", color = Color(0xFF617067))
                    }
                }
            }
        }
        risk?.let { forecast ->
            item {
                Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(18.dp)) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                        Text("${forecast.overallSeverity} · ${forecast.compositeIndex}% pressure", color = Green, fontWeight = FontWeight.Bold)
                        Text(forecast.advisoryHeadline, color = Ink, fontWeight = FontWeight.Bold)
                        Text(forecast.advisoryAction, color = Color(0xFF536158), style = MaterialTheme.typography.bodySmall)
                        forecast.spraySchedule?.let { Text("Spray window: ${it.suitableWindow}", color = Ink, style = MaterialTheme.typography.bodySmall) }
                    }
                }
            }
            item { Text("Seven-day pathogen trajectory", color = Ink, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold) }
            items(forecast.trajectory) { day ->
                Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(14.dp)) {
                    Column(Modifier.fillMaxWidth().padding(13.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("${day.day} · ${day.date}", modifier = Modifier.weight(1f), color = Ink, fontWeight = FontWeight.Bold)
                            Text("Rain ${day.rainProbability}%", color = Color(0xFF617067), style = MaterialTheme.typography.labelSmall)
                        }
                        RiskMeter("Koleroga", day.kolerogaRisk, Color(0xFFCB6A36))
                        RiskMeter("Anthracnose", day.anthracnoseRisk, Green)
                        RiskMeter("Nut cracking", day.nutCrackingRisk, Color(0xFF5579A8))
                    }
                }
            }
            item { Text("Block vulnerability", color = Ink, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold) }
            items(forecast.blockVulnerability) { block ->
                Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(14.dp)) {
                    Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text(block.name, color = Ink, fontWeight = FontWeight.Bold)
                            Text(block.primaryThreat, color = Color(0xFF617067), style = MaterialTheme.typography.bodySmall)
                        }
                        Text("${block.vulnerabilityScore}%", color = Green, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
        if (weather == null && risk == null && error == null) item { LoadingPanel() }
    }
}

@Composable
private fun RiskMeter(label: String, score: Double, color: Color) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(label, modifier = Modifier.width(95.dp), color = Color(0xFF617067), style = MaterialTheme.typography.labelSmall)
        LinearProgressIndicator(
            progress = { (score / 100.0).toFloat().coerceIn(0f, 1f) },
            modifier = Modifier.weight(1f).height(5.dp),
            color = color,
        )
        Text("${score.toInt()}%", color = Ink, style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
private fun AssistantScreen(state: MobileUiState, onSend: (String) -> Unit) {
    var message by remember { mutableStateOf("") }
    Column(Modifier.fillMaxSize().padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        SectionTitle("Agronomy assistant", "Ask about diagnosis, treatment, or field care")
        LazyColumn(
            modifier = Modifier.weight(1f).fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            items(state.assistantMessages, key = { it.id }) { chat ->
                val isUser = chat.sender == "user"
                Card(
                    modifier = Modifier.fillMaxWidth(if (isUser) 0.9f else 1f).align(if (isUser) Alignment.End else Alignment.Start),
                    colors = CardDefaults.cardColors(containerColor = if (isUser) Green else Color.White),
                    shape = RoundedCornerShape(16.dp),
                ) {
                    Text(chat.text, Modifier.padding(14.dp), color = if (isUser) Color.White else Ink)
                }
            }
            if (state.isAssistantSending) item { LoadingPanel() }
        }
        state.error?.let { Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall) }
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            TextField(value = message, onValueChange = { message = it }, modifier = Modifier.weight(1f), placeholder = { Text("Ask your agronomist") }, maxLines = 3)
            Button(onClick = { onSend(message); message = "" }, enabled = message.isNotBlank() && !state.isAssistantSending) { Text("Send") }
        }
    }
}

@Composable
private fun NotificationsScreen(
    data: com.arecavision.mobile.data.NotificationsDto?,
    error: String?,
    onMarkAllRead: () -> Unit,
    onMarkRead: (String) -> Unit,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(18.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) { SectionTitle("Field alerts", "${data?.unreadCount ?: 0} unread notifications") }
                if ((data?.unreadCount ?: 0) > 0) TextButton(onClick = onMarkAllRead) { Text("Mark all read") }
            }
        }
        if (error != null && data == null) item { Text(error, color = MaterialTheme.colorScheme.error) }
        if (data == null && error == null) item { LoadingPanel() }
        items(data?.notifications.orEmpty(), key = { it.id }) { alert ->
            Card(colors = CardDefaults.cardColors(containerColor = if (alert.unread) Color(0xFFE7F3EC) else Color.White), shape = RoundedCornerShape(16.dp)) {
                Column(Modifier.fillMaxWidth().padding(15.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                    Text(alert.title, color = Ink, fontWeight = FontWeight.Bold)
                    Text(alert.msg, color = Color(0xFF536158), style = MaterialTheme.typography.bodySmall)
                    Text("${alert.type.uppercase()} · ${alert.time}", color = Green, style = MaterialTheme.typography.labelSmall)
                    if (alert.unread) TextButton(onClick = { onMarkRead(alert.id) }) { Text("Mark read") }
                }
            }
        }
    }
}

@Composable
private fun PesticideCalculatorScreen(
    registry: com.arecavision.mobile.data.PesticideRegistryDto?,
    error: String?,
) {
    var method by remember { mutableStateOf("Manual") }
    var palms by remember { mutableStateOf("450") }
    var acres by remember { mutableStateOf("1.0") }
    val waterLiters = if (method == "Manual") {
        (palms.toIntOrNull()?.coerceAtLeast(0) ?: 0) * 2.5
    } else {
        (acres.toDoubleOrNull()?.coerceAtLeast(0.0) ?: 0.0) * 50.0
    }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(18.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item { SectionTitle("Spray estimator", "Choose an application method and review field guidance") }
        item {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("Manual", "Drone").forEach { option ->
                    FilterChip(
                        selected = method == option,
                        onClick = { method = option },
                        label = { Text(option) },
                    )
                }
            }
        }
        item {
            TextField(
                value = if (method == "Manual") palms else acres,
                onValueChange = { value -> if (method == "Manual") palms = value.filter(Char::isDigit) else acres = value.filter { it.isDigit() || it == '.' } },
                modifier = Modifier.fillMaxWidth(),
                label = { Text(if (method == "Manual") "Palms to spray" else "Acres to spray") },
                singleLine = true,
            )
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Green), shape = RoundedCornerShape(18.dp)) {
                Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("ESTIMATED TANK VOLUME", color = Color.White.copy(alpha = 0.8f), style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold)
                    Text("${String.format(Locale.US, "%.1f", waterLiters)} L", color = Color.White, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                    Text(if (method == "Manual") "Based on 2.5 L per mature palm" else "Based on 50 L per acre" , color = Color.White.copy(alpha = 0.85f), style = MaterialTheme.typography.bodySmall)
                }
            }
        }
        if (error != null && registry == null) item { Text(error, color = MaterialTheme.colorScheme.error) }
        if (registry == null && error == null) item { LoadingPanel() }
        registry?.let { recommendations ->
            item { Text("Fungicide guidance", color = Ink, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold) }
            items(recommendations.fungicides) { guide -> PesticideGuideCard(guide) }
            item { Text("Insecticide guidance", color = Ink, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold) }
            items(recommendations.insecticides) { guide -> PesticideGuideCard(guide) }
            item { Text(recommendations.source, color = Color(0xFF617067), style = MaterialTheme.typography.labelSmall) }
        }
    }
}

@Composable
private fun PesticideGuideCard(guide: com.arecavision.mobile.data.PesticideGuideDto) {
    Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(16.dp)) {
        Column(Modifier.fillMaxWidth().padding(15.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
            Text(guide.target, color = Ink, fontWeight = FontWeight.Bold)
            Text(guide.chemical, color = Color(0xFF536158), style = MaterialTheme.typography.bodySmall)
            if (guide.alternative.isNotBlank()) Text("Alternative: ${guide.alternative}", color = Color(0xFF617067), style = MaterialTheme.typography.bodySmall)
            if (guide.bioControl.isNotBlank()) Text("Biological: ${guide.bioControl}", color = Green, style = MaterialTheme.typography.bodySmall)
            Text("Pre-harvest interval: ${guide.phiDays} days", color = Color(0xFF617067), style = MaterialTheme.typography.labelSmall)
        }
    }
}

@Composable
private fun FertilizerCalculatorScreen(state: MobileUiState, onCalculate: (Int) -> Unit) {
    var palmCount by remember { mutableStateOf("450") }
    val parsedPalmCount = palmCount.toIntOrNull()
    val validPalmCount = parsedPalmCount?.takeIf { it in 1..100000 }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(18.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item { SectionTitle("Fertilizer calculator", "ICAR-CPCRI annual plan for mature palms") }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                TextField(
                    value = palmCount,
                    onValueChange = { palmCount = it.filter(Char::isDigit) },
                    modifier = Modifier.weight(1f),
                    label = { Text("Number of palms") },
                    singleLine = true,
                )
                Button(onClick = { validPalmCount?.let(onCalculate) }, enabled = validPalmCount != null) {
                    Text("Calculate")
                }
            }
        }
        state.error?.let { message -> item { Text(message, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall) } }
        val plan = state.fertilizerPlan
        if (plan == null) {
            item { LoadingPanel() }
        } else {
            item {
                Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(18.dp)) {
                    Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Annual requirement · ${plan.palms} palms", color = Ink, fontWeight = FontWeight.Bold)
                        CalculatorValue("Urea", "${plan.annualRequirement.ureaKg} kg · ${plan.annualRequirement.ureaBags50kg} bags")
                        CalculatorValue("Rock phosphate", "${plan.annualRequirement.rockPhosphateKg} kg · ${plan.annualRequirement.rockPhosphateBags50kg} bags")
                        CalculatorValue("Muriate of potash", "${plan.annualRequirement.muriateOfPotashKg} kg · ${plan.annualRequirement.mopBags50kg} bags")
                        CalculatorValue("Farmyard manure", "${plan.annualRequirement.farmyardManureTons} tons")
                    }
                }
            }
            plan.splitSchedule?.let { schedule ->
                listOfNotNull(schedule.preMonsoonSplit, schedule.postMonsoonSplit).forEach { split ->
                    item {
                        Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(16.dp)) {
                            Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                                Text(split.window, color = Green, fontWeight = FontWeight.Bold)
                                Text(split.share, color = Ink, style = MaterialTheme.typography.bodySmall)
                                Text("Per palm: ${split.ureaGramsPerPalm} g urea · ${split.rockPhosGramsPerPalm} g rock phosphate · ${split.mopGramsPerPalm} g MOP", color = Color(0xFF536158), style = MaterialTheme.typography.bodySmall)
                                if (split.fymKgPerPalm > 0) Text("FYM: ${split.fymKgPerPalm} kg per palm", color = Color(0xFF536158), style = MaterialTheme.typography.bodySmall)
                            }
                        }
                    }
                }
            }
            item {
                plan.micronutrientRecommendations?.let { micronutrients ->
                    Card(colors = CardDefaults.cardColors(containerColor = Color(0xFFE7F3EC)), shape = RoundedCornerShape(16.dp)) {
                        Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text("Micronutrient reference", color = Green, fontWeight = FontWeight.Bold)
                            Text("Borax ${micronutrients.boraxGramsPerPalm} g · Magnesium sulphate ${micronutrients.magnesiumSulphateGramsPerPalm} g · Zinc sulphate ${micronutrients.zincSulphateGramsPerPalm} g per palm", color = Ink, style = MaterialTheme.typography.bodySmall)
                        }
                    }
                }
            }
            item { Text(plan.standardsSource, color = Color(0xFF617067), style = MaterialTheme.typography.labelSmall) }
        }
    }
}

@Composable
private fun CalculatorValue(label: String, value: String) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, color = Color(0xFF617067))
        Text(value, color = Ink, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
private fun SettingsScreen() {
    Column(Modifier.fillMaxSize().padding(18.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        SectionTitle("Settings", "Mobile app preferences")
        Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(16.dp)) {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                Text("Service connection", color = Ink, fontWeight = FontWeight.Bold)
                Text(BuildConfig.API_BASE_URL, color = Color(0xFF617067), style = MaterialTheme.typography.bodySmall)
                Text("Authentication is not enabled in this first mobile pass.", color = Color(0xFF617067), style = MaterialTheme.typography.bodySmall)
            }
        }
        Text("Language selection and offline preferences are planned next.", color = Color(0xFF617067), style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
private fun SectionTitle(title: String, subtitle: String) {
    Column(Modifier.padding(bottom = 4.dp)) {
        Text(title, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = Ink)
        Text(subtitle, color = Color(0xFF617067))
    }
}

@Composable
private fun ReportsScreen(scanCount: Int, error: String?, onExport: () -> Unit) {
    Column(Modifier.fillMaxSize().padding(18.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        SectionTitle("Field reports", "Export diagnostic records for your farm")
        Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(18.dp)) {
            Column(Modifier.fillMaxWidth().padding(18.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Scan register", color = Ink, fontWeight = FontWeight.Bold)
                Text("$scanCount records available from the server", color = Color(0xFF617067))
                Button(onClick = onExport, enabled = scanCount > 0) { Text("Export CSV") }
                error?.let { Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall) }
            }
        }
    }
}

private fun formatDate(value: String): String {
    val input = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.US)
    val output = SimpleDateFormat("MMM d, yyyy · h:mm a", Locale.getDefault())
    return runCatching { output.format(input.parse(value)!!) }.getOrDefault(value)
}
