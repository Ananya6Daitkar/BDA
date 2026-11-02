# 🚀 Deploy to Render (Best for Streamlit)

Since Vercel has limitations with Streamlit, **Render.com** is the best alternative for deploying your FeedOrbit dashboard.

---

## Why Render?

✅ Native Streamlit support  
✅ Free tier available  
✅ Easy GitHub integration  
✅ Automatic deploys on push  
✅ Environment variables management  
✅ 24/7 uptime  

---

## Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Sign Up"
3. Sign in with GitHub (recommended)

---

## Step 2: Create New Service

1. **Dashboard** → Click **"New +"** 
2. Select **"Web Service"**
3. **Connect your GitHub repository:**
   - Search for: `BDA` or `FeedOrbit`
   - Click "Connect"
4. **Configure:**

```
Name:                    feedorbit
Environment:             Python 3
Root Directory:          FeedOrbit
Build Command:           pip install -r requirements.txt
Start Command:           streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Instance Type:           Free ($0/month)
```

---

## Step 3: Add Environment Variables

1. In Render dashboard: **Settings → Environment**
2. Add variable:

```
Key:   MONGO_URI
Value: mongodb+srv://newuser:Ananya%402006@cluster0.gm70avx.mongodb.net/instaFeed?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true
```

3. Click **"Save Changes"**

---

## Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for build (~3-5 minutes)
3. Your app will be live at: `https://feedorbit.onrender.com`

---

## Manual Deployment from CLI

If you prefer CLI:

```bash
# Install Render CLI (optional)
npm install -g render-cli

# Or use web dashboard at render.com/dashboard
```

---

## What Gets Deployed

```
✅ app.py (988 lines)
✅ requirements.txt
✅ images/ (30 product images)
✅ All source code
✅ MongoDB connection
```

---

## Expected URL

```
Production: https://feedorbit.onrender.com
Status:     Live 24/7
```

---

## Features After Deployment

- ✅ Professional feed with images
- ✅ Live match percentages (0-100%)
- ✅ Real recommendations from ML model
- ✅ Analytics with 4 charts
- ✅ System status dashboard
- ✅ User authentication

---

## Monitoring

In Render dashboard:
- View live logs
- Monitor CPU/memory usage
- Check deployment history
- Set up alerts

---

## Troubleshooting

**If deploy fails:**
1. Check build logs in Render dashboard
2. Verify MONGO_URI is correct
3. Ensure requirements.txt is in FeedOrbit folder

**If app is slow:**
1. May be on free tier (auto-spins down after 15 min inactivity)
2. Upgrade to paid tier for 24/7 uptime

---

## Free Tier Limits

- 0.5 GB RAM
- Spins down after 15 minutes inactivity
- Paid tier: $7/month for always-on

---

## Cost Comparison

| Provider | Streamlit | Free | Best For |
|----------|-----------|------|----------|
| **Render** | ✅ Native | ✅ Yes | **Best for Streamlit** |
| **Railway** | ✅ Docker | ✅ $5 credit | Good alternative |
| **Vercel** | ⚠️ Docker only | ✅ Yes | Next.js/static |
| **Heroku** | ✅ Native | ❌ No | Paid only |

---

## Quick Deploy Command

Once in Render dashboard:
1. Connect GitHub repo
2. Click "Deploy"
3. Done! 🎉

---

**Recommendation: Use Render.com for best Streamlit experience**

