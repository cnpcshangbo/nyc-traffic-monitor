# Repository Guidelines

## Project Structure & Module Organization
- `src/`: React + TypeScript app
  - `components/` UI components (e.g., `VideoPlayerEnhanced.tsx`)
  - `services/` detection/API helpers
  - `config/` runtime config, test setup (`setupTests.ts`)
  - `utils/`, `assets/`, `index.css`, `App.tsx`
- `public/`: static assets and sample videos
- `backend/`: FastAPI YOLOv8 service
  - `app/main.py` API, processed video serving
  - `processed_videos/` output artifacts
  - `requirements.txt`, tests `test_*.py`
- Tooling: `vite.config.ts`, `eslint.config.js`, `docker-compose.yml`, scripts (`run_servers.sh`, `test-browser.sh`).

## Build, Test, and Development Commands
- Frontend dev: `npm run dev` (Vite on `http://localhost:5173`)
- Frontend build: `npm run build` → files in `dist/`
- Preview build: `npm run preview`
- Lint: `npm run lint` (TypeScript ESLint + React Hooks rules)
- Frontend tests: `npm test` (Vitest + Testing Library)
- Backend dev: `cd backend && python -m uvicorn app.main:app --reload --port 8001`
- Backend tests: `cd backend && pytest`
- One‑shot both: `./run_servers.sh`

## Coding Style & Naming Conventions
- TypeScript + React function components; 2‑space indent.
- Components: PascalCase filenames in `src/components`.
- Variables/functions: `camelCase`; constants: `SCREAMING_SNAKE_CASE`.
- Keep hooks rules green; prefer pure components and type‑safe props.
- Run `npm run lint` before pushing; fix warnings where reasonable.

## Testing Guidelines
- Frontend: place tests next to code as `*.test.tsx`; use Testing Library queries and avoid implementation details.
- Backend: pytest files `backend/test_*.py`; create a venv (`python -m venv venv`) and `pip install -r requirements.txt` before running.
- Aim to cover data flows (video selection → detection → render) and API happy paths and errors.

## Commit & Pull Request Guidelines
- Use Conventional Commits (`feat:`, `fix:`, `chore:`, `test:`, `docs:`).
- Small, focused PRs with:
  - Clear description and rationale; link issues.
  - Steps to reproduce and verify (commands, URLs).
  - Screenshots/GIFs for UI changes; API diffs for backend.
  - Passing lint/build/tests (`npm run lint && npm test && npm run build`).

## Security & Configuration Tips
- Frontend API URL: set `VITE_API_URL` (e.g., `.env.local`). Example:
  - `echo 'VITE_API_URL=https://classificationbackend.boshang.online' > .env.local`
- Backend environment:
  - `MODEL_PATH` (YOLOv8 weights): override default in `backend/app/main.py`.
  - `PROCESSED_VIDEOS_DIR` and `ORIGINAL_VIDEOS_DIR` for IO paths.
  - Example: `MODEL_PATH=/models/best.pt PROCESSED_VIDEOS_DIR=/app/processed_videos uvicorn app.main:app`.
- Keep CORS origins aligned with deployment domains.
- Avoid committing large media; use `backend/processed_videos/` for outputs.
