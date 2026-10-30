# ArecaVision Android App Plan

## Goal and constraints

Build a native Android app in Kotlin and Jetpack Compose, starting from a clean `mobile/` folder. Reuse the existing FastAPI REST backend and keep authentication out of the first release. The product target is feature parity with the React web app, delivered in small, testable phases. The web app remains unchanged.

## Architecture

- Single Android application module initially; split into Gradle modules only when build time or ownership justifies it.
- Compose UI grouped by feature: dashboard, detection, plantation, diseases, weather/risk, history/reports, assistant, notifications, settings.
- MVVM: screen state exposed as `StateFlow`; ViewModels own UI actions; repositories own API orchestration and mapping.
- Retrofit + OkHttp for REST and multipart upload; Gson DTO mapping to match the backend envelope `{ success, data, error, timestamp }`.
- Room for durable scan/history/offline cache, DataStore for user preferences, selected language, and backend URL. No token/auth UI in phase one.
- Navigation Compose with a compact bottom bar for frequent destinations and secondary destinations in a drawer/menu.
- Material 3 with an ArecaVision green/charcoal palette; responsive layouts for phones and tablets.
- Gallery via Android Photo Picker and capture via the system camera; image processing and polling stay off the main thread.

## API contract and backend notes

Base path: `/api/v1`.

- Detection: `POST /detect` multipart `image` plus `blockId`; poll `GET /jobs/{job_id}` until `done` or `failed`.
- History: `GET /scans`; delete `DELETE /scans/{scan_id}`.
- Dashboard: `GET /dashboard/kpi`, `/dashboard/trends`, `/dashboard/distribution`.
- Plantation: `GET /plantation/summary`, `GET/POST /plantation/blocks`, `PUT/DELETE /plantation/blocks/{id}`.
- Reference data: `GET /diseases`, `GET /specimens`.
- Weather/risk: `GET /weather`, `GET /risk/forecast`.
- Assistant: `GET /assistant/history`, `POST /assistant/chat`.
- Alerts: `GET /notifications`, `PUT /notifications/read-all`, `PUT /notifications/{id}/read`.
- Reports: `POST /reports/export`, binary PDF/CSV response.

Responses use the envelope above. Inference is asynchronous and returns a job identifier; mobile UI must expose progress, cancellation, failure, and retry states. Backend upload images currently live in temporary storage and are cleaned after one hour, so long-term image retention requires a backend change.

## Phased delivery

1. **Foundation and diagnosis/history vertical slice**
   - Gradle 9.6.0 wrapper, app shell, theme, navigation, Retrofit client, DTOs, repository, ViewModel. Implemented.
   - Dashboard KPI and disease trend chart; photo picker and system camera capture; block selection; multipart diagnosis and job polling; confidence, tissue metrics, differential results, and XAI images; scan history delete and CSV export. Implemented.
   - Loading/error/empty states. JVM and device tests remain.
2. **Plantation and agronomy reference**
   - Plantation summary and create/delete block actions, disease library/search, and ICAR-CPCRI fertilizer calculator. Initial versions implemented.
   - Block editing, full prescription calculator parity, and broader treatment logging remain.
3. **Operations and risk**
   - Dashboard metrics/charts, weather, epidemiological forecasts, notifications and read-all state. Initial versions implemented.
4. **Assistant, reports, and localization**
   - Chat history/send and CSV export. Initial versions implemented.
   - PDF reports, English/Kannada/Hindi strings, and speech briefings remain.
5. **Offline, quality, and release**
   - Room/DataStore caching and sync strategy, accessibility/tablet polish, repository/UI/instrumentation tests, CI build, signing and Play release checklist.

## First-slice acceptance checks

- App compiles and launches on an Android emulator.
- Emulator talks to backend at `http://10.0.2.2:8000/api/v1/` (configurable).
- A gallery image can be uploaded, progress is polled, and diagnosis details render.
- Existing SQLite scans load in History; API failures produce an explicit retry state.
- No auth requirement is introduced in this phase.

## Current implementation boundary

The current app is a first usable parity slice, not a feature-complete port. Remaining planned work includes Room/DataStore offline caching, editing plantation blocks, camera/XAI device QA, treatment logging, PDF export, localization and voice, and automated JVM/UI tests. Final camera, network, and layout validation is planned in Android Studio on the user's physical phone.

## Risks and open technical notes

- The backend's current dev command binds to loopback. Emulator host access works via `10.0.2.2`; a physical phone requires the backend to bind to a LAN-accessible interface and firewall access.
- Uploaded files are temporary (one-hour cleanup) and should not be treated as durable history media.
- Full parity includes many features; each phase should remain independently usable rather than waiting for the entire port.
