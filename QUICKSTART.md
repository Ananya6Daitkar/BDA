# ⚡ FeedOrbit Quick Start

Get FeedOrbit running in 2 minutes!

---

## 🚀 Local Setup (Development)

### Step 1: Install Dependencies
```bash
cd /Users/nalinee/BDA/FeedOrbit
pip install -r requirements.txt
```

### Step 2: Set Environment
```bash
# Copy example
cp .env.example .env

# The .env already contains:
# MONGO_URI=mongodb+srv://newuser:Ananya%402006@cluster0.gm70avx.mongodb.net/instaFeed...
```

### Step 3: Run Dashboard
```bash
streamlit run app.py
```

### Step 4: Open Browser
```
http://localhost:8501
```

---

## 📱 Using the Dashboard

### First Time
1. **Click "Sign Up"**
2. **Create username & password** (any values work)
3. **Click "Create Account"**

### Explore
- **Dashboard**: See KPI cards & 12 recommendations
- **Feed**: Full feed view with images
- **Analytics**: 4 interactive charts
- **Status**: System health indicators

---

## 🌐 Deploy to Vercel

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Initial commit"
git push -u origin main
```

### Step 2: Connect Vercel
- Go to [vercel.com/dashboard](https://vercel.com/dashboard)
- Click "Add New" → "Project"
- Select your GitHub repo
- Click "Import"

### Step 3: Add Environment Variable
- In Vercel: Settings → Environment Variables
- Add `MONGO_URI` with your MongoDB connection string
- Click "Save"

### Step 4: Deploy
- Click "Deploy"
- Wait 2-3 minutes
- Visit `https://your-project.vercel.app`

---

## 📊 What You'll See

### Feed Cards
```
┌──────────────┐
│  [Image]     │
│  ┌─────────┐ │
│  │TRAVEL   │ │
│  │Sunset   │ │
│  │Watch... │ │
│  │✓ 85%    │ │
│  │❤️ Like   │ │
│  └─────────┘ │
└──────────────┘
```

### Match Percentage
- Shows ML recommendation confidence
- 0-100% from Spark ALS model
- Higher = better match

### Analytics
- User Activity (pie chart)
- Top Posts (bar chart)
- Timeline (line chart)
- Distribution (histogram)

---

## 🔑 Key Features

✅ **30+ Images** - Real product photos  
✅ **Live Recommendations** - From ML model  
✅ **Match %" - Shows relevance score  
✅ **Beautiful Design** - Lavender SaaS theme  
✅ **Analytics** - 4 interactive charts  
✅ **Authentication** - Login/signup  
✅ **Real-Time Data** - 14k+ events in DB  

---

## 🆘 Troubleshooting

### App won't start?
```bash
# Check dependencies
pip install -r requirements.txt --upgrade

# Run with verbose output
streamlit run app.py --logger.level=debug
```

### Images not showing?
```bash
# Verify images folder exists
ls -la images/ | head -10

# Check paths in app.py
grep -n "images/" app.py
```

### MongoDB not connecting?
```bash
# Test connection
python3 << 'EOF'
from pymongo import MongoClient
uri = "mongodb+srv://newuser:Ananya%402006@cluster0.gm70avx.mongodb.net/instaFeed?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
client.admin.command('ping')
print("✅ Connected!")
EOF
```

### Vercel deployment fails?
```bash
# View build logs
vercel logs https://your-app.vercel.app --follow

# Check requirements.txt
cat requirements.txt

# Rebuild
vercel --prod --force
```

---

## 📁 Project Structure
```
FeedOrbit/
├── app.py                  # Main app (980 lines)
├── requirements.txt        # Dependencies
├── .env                    # MongoDB connection
├── PROJECT_SUMMARY.md      # Full documentation
├── DEPLOYMENT.md           # Vercel setup guide
├── QUICKSTART.md          # This file
├── images/                 # 30+ images
└── .streamlit/config.toml  # Streamlit config
```

---

## 🎯 Next Steps

1. ✅ Run locally and test
2. ✅ Create GitHub repo
3. ✅ Deploy to Vercel
4. ✅ Share with friends
5. ✅ Customize & extend

---

## 💬 Tips

- **Save user preferences** → Add favorites
- **Add filters** → By category, date, engagement
- **Build API** → RESTful endpoints
- **Mobile app** → React Native version
- **Real dashboard** → Use your own data

---

## 📚 Learn More

- Read **PROJECT_SUMMARY.md** for full details
- Read **DEPLOYMENT.md** for Vercel guide
- Check **app.py** (980 lines of code)

---

## 🎉 Ready?

```bash
# Local
streamlit run app.py

# Or deploy
# https://feedorbit.vercel.app
```

**Enjoy! 🚀**
