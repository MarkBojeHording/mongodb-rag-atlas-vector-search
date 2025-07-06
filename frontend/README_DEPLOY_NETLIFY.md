# Deploying the Frontend to Netlify

1. **API Configuration:**
   - The frontend automatically uses `/api` endpoints which are proxied to your backend via `netlify.toml`
   - No environment variables needed - the redirects handle the API routing automatically

2. **Build Command:**
   - `npm run build`

3. **Publish Directory:**
   - `dist`

4. **Redirects:**
   - The provided `netlify.toml` handles SPA routing and proxies `/api/*` to your backend.

5. **Deploy:**
   - Push your code to GitHub and connect the repo to Netlify, or drag-and-drop the `dist` folder in the Netlify UI.

---

**Note:** Your FastAPI backend must be deployed separately (e.g., Render, Heroku, Railway, etc.) and accessible from the Netlify site.
