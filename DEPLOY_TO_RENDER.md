# Deploy to Render

This guide walks you through deploying your MewarChat FastAPI backend to **Render** (free tier).

## Prerequisites

- GitHub account (free)
- Render account (free) → https://render.com
- Your OpenAI API key

---

## Step 1: Prepare Your GitHub Repository

### 1a. Initialize Git (if not already done)

```powershell
cd C:\Users\Va_d3R\Desktop\GodSent\ChatBot-System\Mewarchat
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 1b. Create `.gitignore` to exclude venv and sensitive files

Create/update `.gitignore` in your project root:

```
.venv/
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.env.local
.DS_Store
*.pdf
processed_data/
```

### 1c. Commit and push to GitHub

```powershell
git add .
git commit -m "Initial commit: MewarChat backend for Render deployment"
```

Then:
1. Go to GitHub → Create New Repository (name: `MewarChat` or similar)
2. Copy the commands GitHub shows:
   ```powershell
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/MewarChat.git
   git push -u origin main
   ```

---

## Step 2: Deploy to Render

### 2a. Sign up on Render

1. Go to https://render.com
2. Click "Get Started" → Sign up with GitHub
3. Authorize Render to access your GitHub repos

### 2b. Create a Web Service

1. Dashboard → **+ New +** → **Web Service**
2. Select your MewarChat repository
3. Fill in settings:
   - **Name:** `mewarchat-backend` (or your choice)
   - **Environment:** Python 3
   - **Region:** `oregon` (closest to you, or choose your region)
   - **Branch:** `main`
   - **Build Command:** (leave blank - Render auto-detects `render.yaml`)
   - **Start Command:** (leave blank - uses `render.yaml`)
   - **Plan:** Free

### 2c. Add Environment Variables

On the Render dashboard for your service, go to **Environment**:

**Add these as environment variables:**

```
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
CHUNK_SIZE_TOKENS=900
CHUNK_OVERLAP_TOKENS=300
SIMILARITY_THRESHOLD=0.35
TOP_K=8
OPENAI_API_KEY=sk-xxxxxxx... (your actual key)
UNIVERSITY_WEB_URL= (leave blank or add your library URL)
```

⚠️ **IMPORTANT:** For `OPENAI_API_KEY`, you can mark it as a **Secret** by clicking the lock icon so it doesn't show in logs.

### 2d. Deploy

Click **Create Web Service** → Render auto-deploys your code.

**Wait 5-10 minutes** for the first build. You'll see:
- Build logs scrolling
- Once done, you get a public URL: `https://mewarchat-backend-xxxxx.onrender.com`

---

## Step 3: Test Your Deployed Backend

Once deployed, test the API:

```powershell
# Check health endpoint
curl https://mewarchat-backend-xxxxx.onrender.com/health

# Should return: {"status":"ok"}
```

---

## Step 4: Connect Streamlit Frontend to Remote Backend

### 4a. Update `streamlit_app.py`

Open [streamlit_app.py](streamlit_app.py) and update the API endpoint:

```python
# Around line 16, change:
API_DEFAULT = os.environ.get("API_BASE", "https://mewarchat-backend-xxxxx.onrender.com/api")
```

Replace `xxxxx` with your actual Render service name from the URL.

### 4b. Deploy Streamlit Locally or to Streamlit Cloud

**Option A: Run Streamlit locally (quick)**
```powershell
streamlit run streamlit_app.py
```

**Option B: Deploy to Streamlit Cloud (recommended for persistent frontend)**
1. Push updated `streamlit_app.py` to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repo → select `streamlit_app.py`
4. Deploy (automatic on each GitHub push)

---

## Troubleshooting

### Build fails: "ModuleNotFoundError: No module named 'torch'"

**Cause:** Torch is large (~1GB); Render's free tier has limited resources  
**Solution:** 
- Wait for build to complete (can take 10+ minutes)
- If it repeatedly fails, add this to `render.yaml`:
  ```yaml
  buildCommand: pip install --no-cache-dir -r requirements.txt
  ```

### Service goes to sleep after 15 minutes

**This is normal on Render's free tier.** First request after inactivity takes 10-30s (cold start).  
**Solutions:**
- Upgrade to Render's paid tier ($7+/month)
- Use a free service like https://kping.io to ping your backend every 15 min
- Accept the cold start delay

### API returns 500 error

1. Check Render dashboard → Logs tab
2. Look for error messages
3. Check your `OPENAI_API_KEY` is correct
4. Verify `data/` folder contents are sufficient

### "Connection refused" from Streamlit

1. Confirm Render backend is deployed and running
2. Verify URL in `streamlit_app.py` matches your Render service URL
3. Backend must be on HTTPS (Render auto-provides this)

---

## Monitoring Your Deployment

### Check logs in real-time

On Render dashboard → Logs tab, you see live output as requests come in.

### Monitor resource usage

Render's free tier: 512 MB RAM, shared CPU. Watch for:
- Memory spikes (embeddings loading)
- CPU throttling (slow responses)

If consistently hitting limits, upgrade plan or optimize settings (use smaller embedding model).

---

## Keeping Your Backend Updated

Any push to GitHub auto-triggers a redeploy:

```powershell
# Make changes locally
git add .
git commit -m "Update settings"
git push origin main

# Within 1 minute, Render redeploys automatically
```

---

## Cost Estimate

| Service | Tier | Cost |
|---------|------|------|
| **Render Backend** | Free (512 MB, sleeps) | $0/mo |
| **Render Backend** | Starter (1 GB, always on) | $7/mo |
| **Streamlit Frontend** | Free (Streamlit Cloud) | $0/mo |
| **TOTAL Free** | - | $0/mo |
| **TOTAL Optimized** | - | $7/mo |

---

## Next Steps (Optional Improvements)

1. **Add monitoring:** https://uptimerobot.com (free uptime checks)
2. **Custom domain:** Render supports custom domains ($3/mo)
3. **Database:** Later, add PostgreSQL if needed ($12-15/mo)
4. **Caching API responses:** Reduce OpenAI calls with Redis (costs extra)

---

## Questions?

- Render Docs: https://docs.render.com
- FastAPI on Render: https://docs.render.com/deploy-fastapi
- Use Render's support chat (bottom right of dashboard)
