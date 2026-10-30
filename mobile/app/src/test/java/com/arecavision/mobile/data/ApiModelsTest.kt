package com.arecavision.mobile.data

import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ApiModelsTest {
    @Test
    fun parsesDiagnosisEnvelopeAndNestedInferenceFields() {
        val json = """
            {
              "success": true,
              "data": {
                "id": "job-123",
                "disease": "Yellow Leaf Disease",
                "confidence": 89.0,
                "stage": "Active Infection",
                "severity": "Severe",
                "description": "Progressive yellowing",
                "treatments": ["Improve drainage"],
                "organicControl": ["Apply compost"],
                "modelBreakdown": {"cnn": 99.4, "vit": 89.0, "yolo": 94.2},
                "tissueMorphometrics": {"healthyPct": 62, "chloroticPct": 16, "necroticPct": 22, "lesionCoveragePct": 19},
                "differentialDiagnosis": [{"disease": "yellow_leaf", "probability": 89.0}],
                "featureMapUrl": "data:image/jpeg;base64,Zm9v",
                "attentionMapUrl": null,
                "gradCamUrl": "data:image/jpeg;base64,YmFy"
              }
            }
        """.trimIndent()
        val responseType = object : TypeToken<ApiEnvelope<DiagnosisDto>>() {}.type

        val response: ApiEnvelope<DiagnosisDto> = Gson().fromJson(json, responseType)

        assertTrue(response.success)
        assertEquals("Yellow Leaf Disease", response.data?.disease)
        assertEquals(89.0, response.data?.modelBreakdown?.vit ?: 0.0, 0.0)
        assertEquals(19.0, response.data?.tissueMorphometrics?.lesionCoveragePct ?: 0.0, 0.0)
        assertEquals("yellow_leaf", response.data?.differentialDiagnosis?.firstOrNull()?.disease)
        assertEquals("data:image/jpeg;base64,Zm9v", response.data?.featureMapUrl)
        assertEquals("data:image/jpeg;base64,YmFy", response.data?.gradCamUrl)
    }
}
