# Wind Forecast Monitor

Web app comparing UK national wind generation actuals (Elexon FUELHH) against forecasts (Elexon WINDFOR) for January 2026.

## Files
- backend/app.py - Flask API (data loading, forecast selection, error stats)
- backend/data.json - cached Elexon data for January 2026
- backend/requirements.txt, Dockerfile, vercel.json
- frontend/src/App.jsx - React UI (charts, date range, horizon slider)
- frontend/src/main.jsx, index.html, vite.config.js, package.json, Dockerfile
- docker-compose.yml

## Run without Docker
Backend: cd backend, pip install -r requirements.txt, python app.py
Frontend: cd frontend, npm install, npm run dev

## How forecasts are picked
For each half-hour target, the forecast used is the latest one published at least `horizon` hours before the target. Default horizon is 24h.

## Live app
- Frontend: PASTE_FRONTEND_URL
- Backend: PASTE_BACKEND_URL

## AI tools used
Claude was used to assist with writing the code.
