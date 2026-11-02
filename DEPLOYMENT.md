# 🚀 FeedOrbit Deployment Guide

## Deploy to Vercel

This guide shows how to deploy FeedOrbit to Vercel for free hosting.

---

## 📋 Prerequisites

- Vercel account (free at [vercel.com](https://vercel.com))
- GitHub account
- Git installed on your machine

---

## 🔧 Step 1: Prepare Git Repository

```bash
# Navigate to project
cd /Users/nalinee/BDA/FeedOrbit

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "FeedOrbit: Ready for Vercel deployment"

# If you want to push to GitHub (optional)
# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/feedorbit.git
git branch -M main
git push -u origin main
```

---

## 🌐 Step 2: Connect to Vercel

### Option A: Using GitHub (Recommended)

1. **Push to GitHub**
   ```bash
   git push -u origin main
   ```

2. **Go to [vercel.com/dashboard](https://vercel.com/dashboard)**

3. **Click "Add New..." → "Project"**

4. **Select "Import Git Repository"**

5. **Search and select your GitHub repo**

6. **Configure:**
   - Framework Preset: **Other**
   - Root Directory: **./FeedOrbit**
   - Build Command: `pip install -r requirements.txt && streamlit run app.py`
   - Output Directory: *leave blank*

7. **Add Environment Variables:**
   ```
   MONGO_URI = mongodb+srv://newuser:Ananya%402006@cluster0.gm70avx.mongodb.net/instaFeed?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true
   ```

8. **Click Deploy**

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Vercel will prompt for:
# - Project name: feedorbit
# - Directory: ./
# - Environment variables: Add MONGO_URI

# Get your deployment URL
# Your app will be at: https://feedorbit.vercel.app
```

---

## ⚙️ Step 3: Environment Variables Setup

### In Vercel Dashboard

1. Go to your project settings
2. Click **Settings** → **Environment Variables**
3. Add variable:
   - **Key**: `MONGO_URI`
   - **Value**: `mongodb+srv://newuser:Ananya%402006@cluster0.gm70avx.mongodb.net/instaFeed?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true`
4. Select environments: **Production**, **Preview**, **Development**
5. Click **Save**

---

## 🎯 Step 4: MongoDB Atlas Setup

### Ensure MongoDB is Ready

1. **Whitelist IP** (allow all for development):
   - Go to [MongoDB Atlas](https://cloud.mongodb.com)
   - Project → Network Access
   - Add IP Address: `0.0.0.0/0` (allow all)
   - Or add Vercel IP range

2. **Verify Connection String**:
   ```
   mongodb+srv://newuser:Ananya%402006@cluster0.gm70avx.mongodb.net/instaFeed
   ```

3. **Test Connection**:
   ```bash
   python3 << 'EOF'
   from pymongo import MongoClient
   uri = "mongodb+srv://newuser:Ananya%402006@cluster0.gm70avx.mongodb.net/instaFeed?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
   client = MongoClient(uri, serverSelectionTimeoutMS=5000)
   client.admin.command('ping')
   print("✅ Connection OK")
   EOF
   ```

---

## 🖼️ Step 5: Verify Images

Ensure images are properly included:

```bash
# Check images folder
ls -la images/ | wc -l  # Should be 30+

# Verify in git
git ls-files images/
```

All images in `/images/` will be deployed with your app.

---

## ✅ Step 6: Deployment Verification

### Check Deployment Status

1. **In Vercel Dashboard:**
   - Click your project
   - View build logs
   - Check for errors

2. **Expected Output:**
   ```
   ✅ Build successful
   ✅ Function compiled successfully
   ```

3. **Visit your deployment:**
   ```
   https://feedorbit.vercel.app
   ```

### If Build Fails

1. **Check logs:**
   ```bash
   vercel logs https://feedorbit.vercel.app
   ```

2. **Common issues:**
   - Missing requirements.txt → Add it
   - MongoDB URI not set → Add to environment variables
   - Image paths wrong → Verify paths in app.py

---

## 🔄 Step 7: Continuous Deployment

### Auto-Deploy on Push

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

2. **Vercel automatically:**
   - Detects push
   - Runs build
   - Deploys new version
   - Your app updates instantly ✅

### Manual Redeploy

```bash
vercel --prod
```

---

## 🧪 Testing Your Deployment

### Test Workflow

1. **Open app:**
   ```
   https://feedorbit.vercel.app
   ```

2. **Test features:**
   - ✅ Create account
   - ✅ View feed with images
   - ✅ See match percentages
   - ✅ Navigate to Analytics
   - ✅ Check Status page

3. **Test data:**
   - Verify MongoDB connection
   - Check recommendations loading
   - Confirm images displaying

---

## 📊 Monitoring

### View Deployment Metrics

In Vercel Dashboard:
- **Deployments**: View all deployments
- **Analytics**: Track pageviews, errors
- **Logs**: Real-time logs
- **Functions**: Serverless function stats

---

## 🛠️ Troubleshooting

### Issue: "Build Failed"

**Solution:**
```bash
# Check requirements.txt
cat requirements.txt

# Verify app.py syntax
python3 -m py_compile app.py

# Check for import errors
python3 -c "import app"
```

### Issue: "MongoDB Connection Timeout"

**Solution:**
1. Verify MONGO_URI in environment variables
2. Check MongoDB IP whitelist (add 0.0.0.0/0)
3. Test locally first:
   ```bash
   python3 << 'EOF'
   import os
   from pymongo import MongoClient
   uri = os.getenv('MONGO_URI')
   client = MongoClient(uri, serverSelectionTimeoutMS=5000)
   client.admin.command('ping')
   print("✅ OK")
   EOF
   ```

### Issue: "Images Not Loading"

**Solution:**
1. Verify images in git:
   ```bash
   git status images/
   ```
2. Check image paths in app.py (line ~760)
3. Ensure `/images/` folder included in deployment

### Issue: "Page Timeout"

**Solution:**
1. Optimize MongoDB queries
2. Use caching with `@st.cache_data`
3. Reduce number of recommendations initially

---

## 🚀 Advanced Deployment Options

### Option: Deploy to Other Platforms

#### Render
```bash
# Push to GitHub
git push origin main

# Go to render.com/dashboard
# Connect GitHub repo
# Service type: Streamlit
# Build command: pip install -r requirements.txt
```

#### Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

#### AWS/GCP
- Use Docker container
- Deploy to App Engine or Lambda
- More complex setup

---

## 📝 Custom Domain (Optional)

### Add Your Own Domain

1. **In Vercel Dashboard:**
   - Settings → Domains
   - Add Domain
   - Follow DNS setup instructions

2. **Example:**
   - Domain: `feedorbit.com`
   - Vercel provides CNAME records
   - Point domain DNS to Vercel

---

## 💡 Tips & Best Practices

1. **Use environment variables** for sensitive data
2. **Commit requirements.txt** for reproducible builds
3. **Test locally** before pushing
4. **Monitor logs** after deployment
5. **Set up alerts** for deployment failures
6. **Keep MongoDB connection alive** with connection pooling

---

## 📚 Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Streamlit on Vercel](https://vercel.com/guides/deploying-python)
- [MongoDB Atlas Free Tier](https://www.mongodb.com/cloud/atlas/register)
- [GitHub + Vercel Integration](https://vercel.com/docs/git)

---

## ✅ Deployment Checklist

- [ ] All code committed to GitHub
- [ ] requirements.txt up to date
- [ ] .env.example created (no secrets)
- [ ] Images folder included in git
- [ ] MongoDB connection tested locally
- [ ] Vercel account created
- [ ] Environment variables set on Vercel
- [ ] MongoDB IP whitelist updated
- [ ] Build successful on Vercel
- [ ] App loads at vercel.app URL
- [ ] Login/signup working
- [ ] Feed shows images & match %
- [ ] Analytics page loads
- [ ] Status page displays

---

## 🎉 Success!

Your FeedOrbit dashboard is now **live on Vercel**! 🚀

**Share your deployment:**
```
Check out my FeedOrbit dashboard: https://feedorbit.vercel.app
```

---

**Last Updated:** November 2, 2026  
**Version:** 1.0.0  
**Status:** Ready for Production

