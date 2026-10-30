# ArecaVision AI

ArecaVision is an arecanut crop-health application. The web client lets growers review crop information and submit palm photos for AI-assisted screening. The repository also contains a FastAPI inference service, a native Android client, and dataset/model development tools.

## Project components

| Path | Purpose |
| --- | --- |
| `frontend/` | React, TypeScript, and Vite web app |
| `backend/` | FastAPI API, inference pipeline, database, and model integration |
| `mobile/` | Kotlin and Jetpack Compose Android client |
| `scripts/` | Dataset, training, evaluation, reporting, and maintenance tools |
| `tests/` | Manual API and inference pipeline checks |
| `docs/` | Project organization and deployment notes |

Dataset folders and trained model checkpoints are intentionally excluded from Git because they are large assets. The root `.gitignore` covers dataset folders named `dataset*`, raw dataset sources, generated reports, and `backend/weights/`.

## Run the web app locally

Run these commands from the project root in PowerShell:

```powershell
npm install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
Copy-Item frontend/.env.example frontend/.env
npm run dev
```

The root `npm run dev` command starts the API and Vite client together. Open [http://localhost:5173](http://localhost:5173). The FastAPI documentation is at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

On Windows, `start_arecavision.bat` is also available to start both services. Stop them with `stop_arecavision.bat`.

### Model files required by the backend

The inference service loads a ViT classifier from one of these folders, in order: `backend/weights/vit_areca_classifier_v4/`, `vit_areca_classifier_v3/`, or `vit_areca_classifier_v2/`. It also requires `backend/weights/best.pt` for YOLO. These checkpoints are not committed; provide the trained files locally before starting the backend. Dataset folders are needed for training and evaluation, but not as substitutes for the checkpoints.

The app starts with local API settings from `frontend/.env.example`:

```dotenv
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_MOCK_DATA=false
VITE_DEMO_MODE=false
```

`VITE_DEMO_MODE=true` simulates scan results for a UI demo. Login and registration still call the backend, so demo mode does not provide offline authentication.

On a fresh local database, the backend seeds a farmer demo account:

```text
Email: farmer@arecavision.ai
Password: farmer123
```

Use that account only for local demonstrations. Registration is available from the login page.

## Build the frontend

From the project root:

```powershell
npm run build
```

The Vite output is written to `frontend/dist/`.

## Deploy the frontend to Vercel

The web client can be deployed separately from the API. In Vercel, import this repository and set **Root Directory** to `frontend`. Use the Vite preset, `npm run build` as the build command, and `dist` as the output directory. `frontend/vercel.json` handles client-side routes such as `/login` and `/detection` on direct visits and refreshes.

For login, saved data, weather, and real image analysis, deploy the backend separately and set `VITE_API_BASE_URL` in Vercel to its public HTTPS API URL, including `/api/v1`, for example:

```text
https://your-api-host.example.com/api/v1
```

Vite embeds `VITE_` variables in the client bundle; never put secrets in them. The local `frontend/.env.production` currently points to `localhost:8001`, which is only a local address and must not be used for a public deployment. See [docs/VERCEL_FRONTEND.md](docs/VERCEL_FRONTEND.md) for the full setup.

## Python tools

Run tools from the project root; several scripts use the workspace path `D:\arecanut_project`.

- `scripts/datasets/` — dataset ingestion and preparation.
- `scripts/training/` — ViT training scripts.
- `scripts/evaluation/` and `scripts/analysis/` — model checks and audits.
- `scripts/reporting/` — report and figure generation.
- `scripts/inspection/` — dataset inspection utilities.
- `scripts/maintenance/` — project healthcheck entry point.

Generated evaluation documents and metrics go to `evaluation_reports/`; generated figures go to `report_figures/`. Those folders are ignored by Git.

## Android app

Open `mobile/` in Android Studio, sync Gradle, select a device, and run the `app` configuration. The emulator API URL and physical-device setup are documented in [mobile/README.md](mobile/README.md).
