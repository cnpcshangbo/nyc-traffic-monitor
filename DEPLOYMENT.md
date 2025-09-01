# Deployment Guide

## GitHub Pages Deployment (Actions-only)

This repository deploys via GitHub Actions to GitHub Pages. Use a single deployment path (Actions) to avoid conflicts.

### Configure Pages

1. Go to Settings → Pages
2. Build and deployment → Source: GitHub Actions

### Build Base Path

The site is hosted under a subpath (e.g., `/UMDL2/`). The build uses `VITE_BASE_PATH` to set the correct base:

```bash
VITE_BASE_PATH=/UMDL2/ npm run build
```

`vite.config.ts` reads this env var and sets `base` accordingly.

### Deployment Workflow

Deployment is automated by `.github/workflows/deploy.yml`:
- Installs deps and runs tests
- Sets `VITE_BASE_PATH` to `/${GITHUB_REPOSITORY#*/}/` (e.g., `/UMDL2/`)
- Builds the frontend
- Adds `.nojekyll` and SPA `404.html`
- Publishes via `actions/deploy-pages`

To trigger a deployment:
- Push to `main` (or run the workflow manually from the Actions tab)

### Access your site

`https://[org-or-user].github.io/[repo-name]/` (e.g., `https://ai-mobility-research-lab.github.io/UMDL2/`)

### Notes

- Videos are served by `https://classificationbackend.boshang.online`
- Ensure the repo name matches the base path you expect (the workflow handles this automatically)
- Avoid pushing built artifacts to `gh-pages` manually; use the Actions workflow only

### Troubleshooting

If you encounter issues:
1. Verify Pages source is set to GitHub Actions
2. Check Actions logs for build/deploy errors
3. Confirm `VITE_BASE_PATH` matches the repository path
4. Hard refresh the site (clear cache) after deployments
