# Deploy the frontend to Vercel

The React app can be deployed independently from the Python backend. In Vercel, import the repository and set **Root Directory** to `frontend`.

Use these project settings:

- Framework preset: **Vite**
- Build command: `npm run build`
- Output directory: `dist`
- Install command: `npm install`

The `frontend/vercel.json` rewrite keeps React Router routes such as `/login`, `/register`, and `/detection` working when opened directly or refreshed.

## Backend requirement

Set `VITE_API_BASE_URL` in Vercel's Production and Preview environment settings to the public HTTPS API base URL, including `/api/v1`, for example:

```text
https://your-api-host.example.com/api/v1
```

This value is compiled into the browser bundle, so it is public configuration and must not contain secrets. Redeploy after changing it.

The current local `.env.production` points to `http://localhost:8001/api/v1`; that address is not reachable by Vercel visitors. Without a deployed backend, the landing page and static UI can load, but login, profile updates, saved data, weather, and real image analysis will not work. The existing mock mode can simulate scan results, but authentication still calls the backend.

The backend must be hosted separately with HTTPS and allow requests from the deployed Vercel origin. The repository's current backend CORS configuration is permissive; tighten it to the deployed frontend origin before using real accounts publicly.

## Frontend-only demo login

If you are deploying only the frontend for a presentation, set `VITE_DEMO_AUTH=true` in the Vercel project environment and redeploy. The login page will accept any username and password, then open the default farmer profile and keep a demo session in that browser. This is a presentation-only client-side bypass, not authentication; do not use it to protect private data. Leave it unset or set it to `false` when using a backend. Registration is disabled while frontend demo auth is enabled.
