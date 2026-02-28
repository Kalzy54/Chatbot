# Quick Render Deployment (5 Minutes)

Follow this **exact sequence** to deploy your backend to Render in ~5 minutes.

---

## ✅ Checklist

### Step 1: Push to GitHub (2 min)

```powershell
cd C:\Users\Va_d3R\Desktop\GodSent\ChatBot-System\Mewarchat

# Initialize git if needed
git init

# Add all files
git add .
git commit -m "Mewarchat backend for Render"

# Push to GitHub (create repo first at github.com)
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/MewarChat.git
git push -u origin main
```

### Step 2: Create Render Service (1 min)

1. Go to https://render.com → Sign in with GitHub
2. Click **+ New +** → **Web Service**
3. Select your `MewarChat` repository
4. Click **Create Web Service** (auto-detects `render.yaml`)

### Step 3: Add Secrets (1 min)

In Render dashboard for your service → **Environment** tab:

**Add Variable:**
```
OPENAI_API_KEY = sk-xxxxxxx...
```
(Click lock icon to mark as Secret)

### Step 4: Wait & Deploy (1-2 min)

Render auto-builds and deploys. Watch the logs. Once you see:
```
Build succeeded
```

Your backend is live at:
```
https://mewarchat-backend-xxxxx.onrender.com
```

### Step 5: Update Streamlit URL (optional)

In `streamlit_app.py` line ~16:
```python
API_DEFAULT = os.environ.get("API_BASE", "https://mewarchat-backend-xxxxx.onrender.com/api")
```

### Done ✅

Test your API:
```powershell
curl https://mewarchat-backend-xxxxx.onrender.com/health
# Returns: {"status":"ok"}
```

---

## That's It!

Your FastAPI backend is now running on **Render's free tier**.

- ✅ Backend: Running 24/7 (sleeps after 15 min idle)
- ✅ HTTPS: Auto-provided
- ✅ Auto-redeploy: Any GitHub push → auto-redeploy within 1 min
- ✅ Logs: View in Render dashboard

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Build takes >10 min | Normal for torch download; be patient |
| 500 error in API | Check Render logs; verify `OPENAI_API_KEY` is set |
| "Connection refused" from Streamlit | Verify backend URL is correct in `streamlit_app.py` |
| Service keeps crashing | Check Render logs for memory/resource errors |

---

## Optional: Keep Service Awake

Free tier sleeps after 15 min idle. To prevent:

Use free https://kping.io:
1. Go to kping.io
2. Add URL: `https://mewarchat-backend-xxxxx.onrender.com/health`
3. Ping every 10 min

Or upgrade to Render Starter ($7/mo) for always-on.

---

## Full Documentation

See [DEPLOY_TO_RENDER.md](DEPLOY_TO_RENDER.md) for detailed guide with troubleshooting, monitoring, and cost breakdowns.
