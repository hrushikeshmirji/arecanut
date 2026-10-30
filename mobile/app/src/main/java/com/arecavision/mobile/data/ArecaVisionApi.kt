package com.arecavision.mobile.data

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.arecavision.mobile.BuildConfig
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.ResponseBody
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Part
import retrofit2.http.Path
import retrofit2.http.Query
import retrofit2.http.Streaming
import kotlinx.coroutines.flow.first

private val Context.mobileDataStore by preferencesDataStore(name = "arecavision-mobile")

interface ArecaVisionApi {
    @GET("dashboard/kpi")
    suspend fun getDashboard(): ApiEnvelope<DashboardDto>

    @GET("dashboard/trends")
    suspend fun getDiseaseTrends(): ApiEnvelope<List<DiseaseTrendDto>>

    @GET("scans")
    suspend fun getScans(@Query("limit") limit: Int = 100): ApiEnvelope<List<ScanDto>>

    @DELETE("scans/{scanId}")
    suspend fun deleteScan(@Path("scanId") scanId: String): ApiEnvelope<Map<String, Any>>

    @Streaming
    @POST("reports/export")
    suspend fun exportReport(@Body request: Map<String, String>): ResponseBody

    @GET("diseases")
    suspend fun getDiseases(): ApiEnvelope<List<DiseaseDto>>

    @GET("plantation/summary")
    suspend fun getPlantation(): ApiEnvelope<PlantationDto>

    @POST("plantation/blocks")
    suspend fun createPlantationBlock(@Body block: PlantationBlockRequestDto): ApiEnvelope<PlantationBlockDto>

    @DELETE("plantation/blocks/{blockId}")
    suspend fun deletePlantationBlock(@Path("blockId") blockId: String): ApiEnvelope<Map<String, Any>>

    @PUT("plantation/blocks/{blockId}")
    suspend fun updatePlantationBlock(
        @Path("blockId") blockId: String,
        @Body update: PlantationBlockUpdateDto,
    ): ApiEnvelope<PlantationBlockDto>

    @GET("weather")
    suspend fun getWeather(): ApiEnvelope<WeatherDto>

    @GET("risk/forecast")
    suspend fun getRisk(): ApiEnvelope<RiskDto>

    @GET("agronomy/fertilizer-plan")
    suspend fun getFertilizerPlan(
        @Query("palms") palms: Int,
        @Query("age") age: String,
    ): ApiEnvelope<FertilizerPlanDto>

    @GET("agronomy/pesticides")
    suspend fun getPesticideRegistry(): ApiEnvelope<PesticideRegistryDto>

    @GET("notifications")
    suspend fun getNotifications(): ApiEnvelope<NotificationsDto>

    @PUT("notifications/read-all")
    suspend fun markAllNotificationsRead(): ApiEnvelope<Map<String, Any>>

    @PUT("notifications/{notificationId}/read")
    suspend fun markNotificationRead(@Path("notificationId") notificationId: String): ApiEnvelope<Map<String, Any>>

    @GET("assistant/history")
    suspend fun getAssistantHistory(): ApiEnvelope<List<AssistantMessageDto>>

    @POST("assistant/chat")
    suspend fun sendAssistantMessage(@Body request: AssistantRequestDto): ApiEnvelope<AssistantReplyDto>

    @Multipart
    @POST("detect")
    suspend fun submitDetection(
        @Part image: MultipartBody.Part,
        @Part("blockId") blockId: RequestBody,
    ): ApiEnvelope<DetectionSubmitDto>

    @GET("jobs/{jobId}")
    suspend fun getJob(@Path("jobId") jobId: String): ApiEnvelope<DetectionJobDto>

    @POST("jobs/{jobId}/cancel")
    suspend fun cancelJob(@Path("jobId") jobId: String): ApiEnvelope<Map<String, Any>>
}

object ApiFactory {
    val api: ArecaVisionApi by lazy {
        Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ArecaVisionApi::class.java)
    }
}

class ArecaRepository(context: Context, private val api: ArecaVisionApi = ApiFactory.api) {
    private val dataStore = context.applicationContext.mobileDataStore
    private val gson = Gson()
    private val scansCacheKey = stringPreferencesKey("scan_history_cache")

    suspend fun dashboard(): DashboardDto = api.getDashboard().requireData()

    suspend fun diseaseTrends(): List<DiseaseTrendDto> = api.getDiseaseTrends().requireData()

    suspend fun scans(): List<ScanDto> {
        return try {
            api.getScans().requireData().also { scans -> cacheScans(scans) }
        } catch (exception: Exception) {
            readCachedScans().takeIf { it.isNotEmpty() } ?: throw exception
        }
    }

    suspend fun deleteScan(scanId: String) {
        api.deleteScan(scanId).requireData()
        cacheScans(readCachedScans().filterNot { it.id == scanId })
    }

    suspend fun exportCsv(): ByteArray = api.exportReport(mapOf("type" to "detailed", "format" to "csv")).bytes()

    suspend fun diseases(): List<DiseaseDto> = api.getDiseases().requireData()

    suspend fun plantation(): PlantationDto = api.getPlantation().requireData()

    suspend fun createPlantationBlock(name: String, trees: Int): PlantationBlockDto =
        api.createPlantationBlock(PlantationBlockRequestDto(name = name, trees = trees)).requireData()

    suspend fun deletePlantationBlock(blockId: String) {
        api.deletePlantationBlock(blockId).requireData()
    }

    suspend fun updatePlantationBlock(blockId: String, healthScore: Int, status: String, primaryDisease: String) {
        api.updatePlantationBlock(
            blockId,
            PlantationBlockUpdateDto(healthScore, status, primaryDisease),
        ).requireData()
    }

    suspend fun weather(): WeatherDto = api.getWeather().requireData()

    suspend fun risk(): RiskDto = api.getRisk().requireData()

    suspend fun fertilizerPlan(palms: Int, age: String): FertilizerPlanDto =
        api.getFertilizerPlan(palms, age).requireData()

    suspend fun pesticideRegistry(): PesticideRegistryDto = api.getPesticideRegistry().requireData()

    suspend fun notifications(): NotificationsDto = api.getNotifications().requireData()

    suspend fun markAllNotificationsRead() {
        api.markAllNotificationsRead().requireData()
    }

    suspend fun markNotificationRead(notificationId: String) {
        api.markNotificationRead(notificationId).requireData()
    }

    suspend fun assistantHistory(): List<AssistantMessageDto> = api.getAssistantHistory().requireData()

    suspend fun sendAssistantMessage(message: String): AssistantReplyDto =
        api.sendAssistantMessage(AssistantRequestDto(message)).requireData()

    suspend fun submitDetection(imageBytes: ByteArray, blockId: String): DetectionSubmitDto {
        val imageBody = imageBytes.toRequestBody("image/jpeg".toMediaType())
        val imagePart = MultipartBody.Part.createFormData("image", "areca-scan.jpg", imageBody)
        val blockPart = blockId.toRequestBody("text/plain".toMediaType())
        return api.submitDetection(imagePart, blockPart).requireData()
    }

    suspend fun job(jobId: String): DetectionJobDto = api.getJob(jobId).requireData()

    suspend fun cancelJob(jobId: String) {
        api.cancelJob(jobId).requireData()
    }

    private suspend fun cacheScans(scans: List<ScanDto>) {
        dataStore.edit { preferences -> preferences[scansCacheKey] = gson.toJson(scans) }
    }

    private suspend fun readCachedScans(): List<ScanDto> {
        val json = dataStore.data.first()[scansCacheKey] ?: return emptyList()
        val type = object : TypeToken<List<ScanDto>>() {}.type
        return runCatching { gson.fromJson<List<ScanDto>>(json, type) }.getOrNull().orEmpty()
    }
}

private fun <T> ApiEnvelope<T>.requireData(): T {
    if (!success) throw IllegalStateException(error?.message ?: "The server rejected the request.")
    return data ?: throw IllegalStateException("The server returned an empty response.")
}
