# Project structure

Run commands from the project root (`D:\arecanut_project`).

## Application

- `backend/` — FastAPI service, inference code, and model weights.
- `frontend/` — React and Vite application.
- `mobile/` — Android application.
- `start_arecavision.bat` — starts the local backend and frontend.
- `package.json` — root development, build, preview, and healthcheck commands.

## Python tools

- `scripts/analysis/` — dataset and generalization audits.
- `scripts/datasets/` — dataset ingestion, preparation, and export.
- `scripts/evaluation/` — model evaluation and verification tools.
- `scripts/inspection/` — dataset inspection utilities.
- `scripts/maintenance/` — project healthcheck entry point.
- `scripts/reporting/` — report and figure generation.
- `scripts/training/` — model training scripts.
- `tests/` — manual pipeline and endpoint checks.

Run a tool from the project root, for example:

```powershell
python scripts/datasets/build_dataset_unified_v4.py
python tests/test_system_health.py
npm run healthcheck
```

## Data and generated output

- Dataset directories remain at the project root because existing scripts and backend code use those paths.
- `evaluation_reports/` holds evaluation results and report documents.
- `report_figures/` holds generated report figures.
- `mendeley_raw/source_archives/` holds the downloaded source ZIP archive.
- `temp_uploads/` is runtime upload storage; `node_modules/` and `__pycache__/` are generated caches.

`frontend_backup_previous/` and `ArecaVision_Combined/` are retained as legacy/reference copies and are not used by the launcher.
