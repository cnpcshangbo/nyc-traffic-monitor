# Deployment Guide

## GitHub Pages Deployment

### For Original Repository (cnpcshangbo/nyc-traffic-monitor)
The repository is configured to automatically deploy to GitHub Pages at:
https://cnpcshangbo.github.io/nyc-traffic-monitor/

### For Forked Repositories

If you've forked this repository, follow these steps to deploy to your GitHub Pages:

1. **Update the base path in `vite.config.ts`:**
   ```typescript
   // Change this line to match your repository name
   const base = process.env.VITE_BASE_PATH || '/UMDL2/';
   ```
   Replace `/UMDL2/` with your repository name (e.g., `/your-repo-name/`)

2. **Enable GitHub Pages in your repository:**
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: Select `gh-pages` (will be created automatically)
   - Click Save

3. **Trigger the deployment:**
   - Push any commit to the main branch, OR
   - Go to Actions → Deploy to GitHub Pages → Run workflow

4. **Access your deployed site:**
   Your site will be available at:
   `https://[your-username].github.io/[your-repo-name]/`

### Important Notes

- The `.nojekyll` file is required to prevent Jekyll processing
- Videos are served from the backend at https://classificationbackend.boshang.online
- Make sure your repository name in `vite.config.ts` matches your actual GitHub repository name
- The GitHub Actions workflow runs on pushes to `main`, `master`, or `feature/transportation-yolov8-model` branches

### Environment Variables (Optional)

You can also set the base path using an environment variable during build:
```bash
VITE_BASE_PATH=/your-repo-name/ npm run build
```

### Troubleshooting

If you encounter build errors:
1. Make sure all dependencies are installed: `npm ci`
2. Check that the base path matches your repository name
3. Ensure GitHub Pages is enabled in your repository settings
4. Check the Actions tab for any workflow errors