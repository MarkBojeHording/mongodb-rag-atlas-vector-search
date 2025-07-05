# Deploying the Frontend to Netlify

1. **Set the API URL:**
   - In your Netlify dashboard, go to Site settings > Environment variables.
   - Add `VITE_API_BASE_URL` and set it to your backend's public URL: `https://mongodb-rag-atlas-vector-search.onrender.com`

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
