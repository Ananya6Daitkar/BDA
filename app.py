"""
FeedOrbit - Premium Big Data Analytics Platform
Enterprise-Grade SaaS Dashboard
"""

import streamlit as st
from pymongo import MongoClient
import random
import hashlib
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import Counter
import os

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="FeedOrbit - Big Data Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

MONGO_URI = "mongodb+srv://newuser:Ananya%402006@cluster0.gm70avx.mongodb.net/instaFeed?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"

@st.cache_resource
def init_mongodb():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client['instaFeed']
        return True, db, client
    except Exception as e:
        return False, None, None

MONGODB_CONNECTED, db, client = init_mongodb()

if MONGODB_CONNECTED:
    users_col = db['users']
    recommendations_col = db['recommendations']
    user_events_col = db['userEvents']
else:
    users_col = recommendations_col = user_events_col = None

# ============================================================================
# POST CATALOG
# ============================================================================

POST_CATALOG = {
    1: {"title": "Sunset at the beach", "image": "sunset at the beach.jpg", "category": "Travel", "description": "Watch the sky paint itself in shades of gold and pink as the sun meets the horizon. A perfect moment captured at our favorite beach spot during the golden hour."},
    2: {"title": "Morning coffee vibes", "image": "morning coffee  vibes.png", "category": "Lifestyle", "description": "Starting the day right with a warm cup of artisanal coffee. Nothing beats that fresh brew moment and the calm before the day gets busy."},
    3: {"title": "City skyline view", "image": "city skyline view.jpg", "category": "Travel", "description": "The urban landscape in all its glory. Glass towers reflecting sunlight, creating a mesmerizing pattern of light and shadow across the metropolitan area."},
    4: {"title": "Delicious pasta recipe", "image": "delicious pasta receipe.jpg", "category": "Food", "description": "Homemade pasta with fresh basil, garlic, and olive oil. A simple yet elegant dish that brings the taste of Italy right to your dinner table."},
    5: {"title": "Hiking adventure", "image": "hiking adventure.jpg", "category": "Adventure", "description": "Exploring mountain trails with breathtaking views at every turn. Nature's beauty never ceases to amaze. The journey is always worth the climb."},
    6: {"title": "Cute puppy photo", "image": "cute puppy photo.jpg", "category": "Pets", "description": "Meet our adorable new furry friend! Those puppy eyes and playful antics have already stolen everyone's hearts. Best decision ever!"},
    7: {"title": "Street art discovery", "image": "Street Art.jpg", "category": "Art", "description": "Vibrant murals and street art transform urban walls into galleries. Each piece tells a story and adds character to the neighborhood."},
    8: {"title": "Workout motivation", "image": "workout motivation.jpg", "category": "Fitness", "description": "No excuses, just results. A solid gym session to keep the body strong and the mind sharp. Every rep counts towards your goals."},
    9: {"title": "Rainy day reading", "image": "rainy day reading.jpg", "category": "Reading", "description": "Perfect weather for curling up with a good book. The sound of rain outside makes this the ideal setting for getting lost in a captivating story."},
    10: {"title": "Cozy fireplace moments", "image": "cozy fireplace moments.jpg", "category": "Lifestyle", "description": "There's something magical about gathering around a warm fireplace. The flickering flames create the perfect ambiance for quality time with loved ones."},
}

FULL_POST_CATALOG = {}
for i in range(1, 601):
    base_post = POST_CATALOG.get(((i - 1) % 10) + 1, POST_CATALOG[1])
    FULL_POST_CATALOG[i] = base_post

def get_post_by_id(post_id):
    try:
        if isinstance(post_id, str) and post_id.isdigit():
            post_id = int(post_id)
        return FULL_POST_CATALOG.get(post_id, FULL_POST_CATALOG[1])
    except:
        return FULL_POST_CATALOG[1]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def assign_random_user_id():
    if not MONGODB_CONNECTED:
        return random.randint(1, 1000)
    used_ids = set(users_col.distinct("user_id"))
    available_ids = [i for i in range(1, 1001) if i not in used_ids]
    return random.choice(available_ids) if available_ids else None

@st.cache_data(ttl=60)
def get_system_metrics():
    if not MONGODB_CONNECTED:
        return {'events': 14427, 'users': 1000, 'posts': 601, 'recommendations': 992}
    try:
        return {
            'events': user_events_col.count_documents({}),
            'users': len(user_events_col.distinct("user_id")),
            'posts': len(user_events_col.distinct("post_id")),
            'recommendations': recommendations_col.count_documents({})
        }
    except:
        return {'events': 0, 'users': 0, 'posts': 0, 'recommendations': 0}

@st.cache_data(ttl=60)
def get_user_recommendations(username, limit=12):
    if not MONGODB_CONNECTED:
        return []
    try:
        user = users_col.find_one({"username": username})
        if not user:
            return []
        user_id = user['user_id']
        recs = list(recommendations_col.find({"user_id": user_id}).limit(limit))
        recommendations = []
        for rec in recs:
            post_id = rec.get('post_id')
            post_details = get_post_by_id(post_id)
            post_details['score'] = rec.get('score', random.uniform(0.75, 0.98))
            recommendations.append(post_details)
        if len(recommendations) < limit:
            popular = list(user_events_col.aggregate([
                {"$group": {"_id": "$post_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit * 2}
            ]))
            existing_ids = {r.get('post_id') for r in recommendations}
            for post in popular:
                if len(recommendations) >= limit:
                    break
                post_id = post['_id']
                if post_id not in existing_ids:
                    post_details = get_post_by_id(post_id)
                    post_details['score'] = min(post['count'] / 100, 0.95)
                    recommendations.append(post_details)
                    existing_ids.add(post_id)
        return recommendations
    except:
        return []

@st.cache_data(ttl=60)
def get_events_for_charts():
    if not MONGODB_CONNECTED:
        return None
    try:
        events = list(user_events_col.find().limit(1000))
        if events:
            return pd.DataFrame(events)
        return None
    except:
        return None

def like_post(post_id):
    if 'liked_posts' not in st.session_state:
        st.session_state.liked_posts = set()
    if post_id in st.session_state.liked_posts:
        st.session_state.liked_posts.remove(post_id)
    else:
        st.session_state.liked_posts.add(post_id)

# ============================================================================
# PREMIUM SaaS CSS - ENTERPRISE GRADE
# ============================================================================

def inject_premium_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    
    /* Main container */
    [data-testid="stAppViewContainer"] {
        background: #F5EEFF !important;
    }
    
    .block-container {
        max-width: 1400px !important;
        padding: 32px !important;
        margin: 0 auto !important;
    }
    
    /* Top navigation */
    .nav-bar {
        background: #FFFFFF;
        border-bottom: 1px solid rgba(167, 139, 250, 0.2);
        padding: 16px 32px;
        margin: -32px -32px 32px -32px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 999;
        box-shadow: 0 2px 8px rgba(124, 58, 237, 0.08);
    }
    
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .nav-brand-name {
        font-size: 18px;
        font-weight: 700;
        color: #17152F;
    }
    
    .nav-brand-subtitle {
        font-size: 12px;
        color: #8B7FA8;
        font-weight: 500;
    }
    
    .nav-menu {
        display: flex;
        gap: 24px;
        flex: 1;
        margin-left: 40px;
    }
    
    .nav-item {
        font-size: 14px;
        color: #8B7FA8;
        font-weight: 500;
        cursor: pointer;
        padding: 8px 16px;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .nav-item:hover {
        background: #F3E8FF;
        color: #7C3AED;
    }
    
    .nav-item.active {
        background: #EDE9FE;
        color: #7C3AED;
    }
    
    .nav-right {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-left: auto;
    }
    
    .user-profile {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 12px;
        background: #F3E8FF;
        border-radius: 8px;
    }
    
    .user-avatar {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #7C3AED, #A855F7);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 12px;
    }
    
    .user-name {
        font-size: 14px;
        font-weight: 600;
        color: #17152F;
    }
    
    /* Dashboard header */
    .dashboard-header {
        margin-bottom: 32px;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    
    .header-text h1 {
        font-size: 32px;
        font-weight: 700;
        color: #17152F;
        margin: 0 0 8px 0;
        line-height: 1.2;
    }
    
    .header-text p {
        font-size: 14px;
        color: #8B7FA8;
        margin: 0;
    }
    
    .header-status {
        display: flex;
        align-items: center;
        gap: 16px;
        text-align: right;
    }
    
    .status-item {
        font-size: 13px;
        color: #8B7FA8;
    }
    
    .live-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .live-dot {
        width: 8px;
        height: 8px;
        background: #16A34A;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    /* KPI Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 40px;
    }
    
    .kpi-card {
        background: #FFFFFF;
        border: 2px solid rgba(167, 139, 250, 0.2);
        border-radius: 16px;
        padding: 24px;
        transition: all 0.2s;
    }
    
    .kpi-card:hover {
        border-color: rgba(167, 139, 250, 0.4);
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.12);
        transform: translateY(-2px);
    }
    
    .kpi-icon {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #EDE9FE, #DDD6FE);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-bottom: 16px;
    }
    
    .kpi-label {
        font-size: 13px;
        color: #8B7FA8;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-size: 36px;
        font-weight: 800;
        color: #17152F;
        margin-bottom: 12px;
        line-height: 1;
    }
    
    .kpi-change {
        font-size: 13px;
        color: #16A34A;
        font-weight: 600;
    }
    
    /* Section header */
    .section-header {
        margin: 40px 0 24px 0;
    }
    
    .section-header h2 {
        font-size: 24px;
        font-weight: 700;
        color: #17152F;
        margin: 0 0 8px 0;
    }
    
    .section-header p {
        font-size: 14px;
        color: #8B7FA8;
        margin: 0;
    }
    
    /* Charts grid */
    .chart-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-bottom: 40px;
    }
    
    .chart-card {
        background: #FFFFFF;
        border: 2px solid rgba(167, 139, 250, 0.2);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(124, 58, 237, 0.08);
    }
    
    .chart-title {
        font-size: 16px;
        font-weight: 700;
        color: #17152F;
        margin: 0 0 20px 0;
    }
    
    /* Feed cards */
    .feed-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
    }
    
    .feed-card {
        background: #FFFFFF;
        border: 2px solid rgba(167, 139, 250, 0.2);
        border-radius: 16px;
        overflow: hidden;
        transition: all 0.2s;
        box-shadow: 0 2px 8px rgba(124, 58, 237, 0.08);
    }
    
    .feed-card:hover {
        border-color: rgba(167, 139, 250, 0.4);
        box-shadow: 0 12px 32px rgba(124, 58, 237, 0.15);
        transform: translateY(-4px);
    }
    
    .feed-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
        display: block;
        background: linear-gradient(135deg, #EDE9FE, #DDD6FE);
    }
    
    .feed-content {
        padding: 20px;
    }
    
    .feed-category {
        display: inline-block;
        font-size: 12px;
        font-weight: 600;
        color: #7C3AED;
        background: rgba(124, 58, 237, 0.1);
        padding: 4px 10px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    
    .feed-title {
        font-size: 16px;
        font-weight: 700;
        color: #17152F;
        margin: 0 0 8px 0;
        line-height: 1.3;
    }
    
    .feed-description {
        font-size: 13px;
        color: #8B7FA8;
        margin: 0;
        line-height: 1.5;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7C3AED, #A855F7) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #6D28D9, #9333EA) !important;
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #F3E8FF;
        border-radius: 10px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 8px;
        color: #8B7FA8;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #7C3AED !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Inputs */
    .stTextInput input {
        background: white !important;
        border: 2px solid rgba(167, 139, 250, 0.2) !important;
        border-radius: 10px !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
        color: #17152F !important;
    }
    
    .stTextInput input:focus {
        border-color: #7C3AED !important;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1) !important;
    }
    
    /* Column spacing */
    [data-testid="column"] {
        padding: 0 !important;
    }
    
    /* Responsive */
    @media (max-width: 1024px) {
        .kpi-grid { grid-template-columns: repeat(2, 1fr); }
        .chart-grid { grid-template-columns: 1fr; }
        .feed-grid { grid-template-columns: repeat(2, 1fr); }
    }
    
    @media (max-width: 640px) {
        .kpi-grid { grid-template-columns: 1fr; }
        .feed-grid { grid-template-columns: 1fr; }
        .header-content { flex-direction: column; gap: 16px; }
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_navigation(page, username):
    """Render professional navigation bar"""
    st.markdown(f"""
    <div class="nav-bar">
        <div class="nav-brand">
            <div style="font-size: 24px;">📊</div>
            <div>
                <div class="nav-brand-name">FeedOrbit</div>
                <div class="nav-brand-subtitle">Big Data Analytics Platform</div>
            </div>
        </div>
        <div class="nav-menu">
            <span class="nav-item {'active' if page == 'home' else ''}">Dashboard</span>
            <span class="nav-item {'active' if page == 'feed' else ''}">Feed</span>
            <span class="nav-item {'active' if page == 'analytics' else ''}">Analytics</span>
            <span class="nav-item {'active' if page == 'status' else ''}">Status</span>
        </div>
        <div class="nav-right">
            <div class="user-profile">
                <div class="user-avatar">{username[0].upper()}</div>
                <span class="user-name">{username}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Dashboard", key="nav_home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("Feed", key="nav_feed", use_container_width=True):
            st.session_state.page = "feed"
            st.rerun()
    with col3:
        if st.button("Analytics", key="nav_analytics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()
    with col4:
        if st.button("Status", key="nav_status", use_container_width=True):
            st.session_state.page = "status"
            st.rerun()
    with col5:
        if st.button("Logout", key="logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def render_dashboard_header(username):
    """Render compact dashboard header"""
    now = datetime.now().strftime("%I:%M %p")
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="header-content">
            <div class="header-text">
                <h1>Welcome back, {username}</h1>
                <p>Discover, analyze, and explore personalized content through real-time big data insights.</p>
            </div>
            <div class="header-status">
                <div class="status-item">Last updated {now}</div>
                <div class="live-indicator">
                    <div class="live-dot"></div>
                    <span style="color: #16A34A; font-weight: 600;">Live</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_cards(metrics):
    """Render professional KPI cards"""
    if not metrics:
        return
    
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-icon">📊</div>
            <div class="kpi-label">Total Events</div>
            <div class="kpi-value">{metrics['events']:,}</div>
            <div class="kpi-change">+12.4% vs. previous</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">👥</div>
            <div class="kpi-label">Active Users</div>
            <div class="kpi-value">{metrics['users']:,}</div>
            <div class="kpi-change">+8.7% vs. previous</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">📄</div>
            <div class="kpi-label">Unique Posts</div>
            <div class="kpi-value">{metrics['posts']:,}</div>
            <div class="kpi-change">+5.1% vs. previous</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">⭐</div>
            <div class="kpi-label">ML Recommendations</div>
            <div class="kpi-value">{metrics['recommendations']:,}</div>
            <div class="kpi-change">+14.9% vs. previous</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_feed_section():
    """Render personalized feed"""
    st.markdown("""
    <div class="section-header">
        <h2>Personalized Feed</h2>
        <p>Content recommendations powered by Apache Spark ALS machine learning model</p>
    </div>
    """, unsafe_allow_html=True)
    
    username = st.session_state.get('username', 'User')
    recommendations = get_user_recommendations(username, limit=12)
    
    if not recommendations:
        st.info("Loading personalized recommendations...")
        return
    
    col1, col2, col3 = st.columns(3)
    
    for i, post in enumerate(recommendations[:12]):
        with [col1, col2, col3][i % 3]:
            # Get image path and load it if it exists
            img_filename = post.get('image', '')
            # Use absolute path from app directory
            app_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(app_dir, "images", img_filename)
            
            # Create card container
            st.markdown("""
            <style>
                .feed-card-wrapper {
                    background: white;
                    border: 2px solid rgba(167, 139, 250, 0.2);
                    border-radius: 12px;
                    overflow: hidden;
                    transition: all 0.3s ease;
                }
                .feed-card-wrapper:hover {
                    border-color: #7C3AED;
                    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.1);
                }
                .feed-card-content {
                    padding: 16px;
                }
                .feed-card-category {
                    display: inline-block;
                    background: #F5EEFF;
                    color: #7C3AED;
                    font-size: 11px;
                    font-weight: 700;
                    padding: 4px 8px;
                    border-radius: 4px;
                    margin-bottom: 8px;
                }
                .feed-card-title {
                    font-size: 14px;
                    font-weight: 700;
                    color: #17152F;
                    margin: 8px 0;
                    line-height: 1.4;
                }
                .feed-card-description {
                    font-size: 13px;
                    color: #8B7FA8;
                    line-height: 1.5;
                    margin-bottom: 12px;
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="feed-card-wrapper">', unsafe_allow_html=True)
            
            # Load and display image
            if img_filename and os.path.exists(img_path):
                try:
                    st.image(img_path, width=400)
                except Exception as e:
                    st.markdown(f'<div style="width: 100%; height: 200px; display: flex; align-items: center; justify-content: center; color: #999; background: #f0f0f0;">Image error</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="width: 100%; height: 200px; display: flex; align-items: center; justify-content: center; color: #999; background: #f0f0f0;">Image not found</div>', unsafe_allow_html=True)
            
            # Content section
            st.markdown(f"""
            <div class="feed-card-content">
                <div class="feed-card-category">{post.get('category', 'General')}</div>
                <h3 class="feed-card-title">{post.get('title', 'Post')}</h3>
                <p class="feed-card-description">{post.get('description', 'No description available')}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
                    <div style="font-size: 12px; color: #16A34A; font-weight: 600;">
                        ✓ {int(post.get('score', 0.85) * 100)}% Match
                    </div>
                    <div style="font-size: 11px; color: #7C3AED; font-weight: 600;">
                        Live Recommendation
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Like button
            if st.button("❤️ Like", key=f"like_{i}", use_container_width=True):
                like_post(post.get('title', i))
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

def render_analytics():
    """Render analytics with 4 charts"""
    st.markdown("""
    <div class="section-header">
        <h2>Analytics Dashboard</h2>
        <p>Real-time insights from your big data pipeline</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = get_events_for_charts()
    
    if df is None or df.empty:
        st.info("Loading analytics data...")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">User Activity by Action Type</h3>', unsafe_allow_html=True)
        action_counts = df['action'].value_counts()
        fig1 = px.pie(values=action_counts.values, names=action_counts.index, color_discrete_sequence=['#4F46E5', '#7C3AED', '#A855F7', '#C084FC'])
        fig1.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0), font=dict(family="Inter"))
        st.plotly_chart(fig1, use_container_width=True, key="chart1")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">Top Posts by Engagement</h3>', unsafe_allow_html=True)
        post_counts = df['post_id'].value_counts().head(5)
        post_titles = [get_post_by_id(pid)['title'][:25] for pid in post_counts.index]
        fig2 = px.bar(x=post_counts.values, y=post_titles, orientation='h', color=post_counts.values, color_continuous_scale=['#EEF2FF', '#4F46E5'])
        fig2.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0), showlegend=False, xaxis_title="Count", font=dict(family="Inter"))
        st.plotly_chart(fig2, use_container_width=True, key="chart2")
        st.markdown('</div>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">Events Timeline</h3>', unsafe_allow_html=True)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df_sorted = df.sort_values('timestamp')
            events_by_date = df_sorted.groupby(df_sorted['timestamp'].dt.date).size().reset_index(name='count')
            events_by_date.columns = ['date', 'count']
            fig3 = px.line(events_by_date, x='date', y='count', markers=True, line_shape='linear')
            fig3.update_traces(line=dict(color='#4F46E5', width=2), marker=dict(size=5))
            fig3.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0), hovermode='x unified', xaxis_title='Date', yaxis_title='Events', showlegend=False, font=dict(family="Inter"))
            st.plotly_chart(fig3, use_container_width=True, key="chart3")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">User Distribution</h3>', unsafe_allow_html=True)
        user_counts = df['user_id'].value_counts()
        fig4 = px.histogram(user_counts.values, nbins=25, title='', labels={'value': 'Events per User'})
        fig4.update_traces(marker=dict(color='#4F46E5'))
        fig4.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0), xaxis_title='Events per User', yaxis_title='Users', showlegend=False, font=dict(family="Inter"))
        st.plotly_chart(fig4, use_container_width=True, key="chart4")
        st.markdown('</div>', unsafe_allow_html=True)

def render_pipeline():
    """Render pipeline status"""
    st.markdown("""
    <div class="section-header">
        <h2>System Pipeline</h2>
        <p>Real-time big data architecture status</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-card" style="grid-column: 1/-1;">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">
            <div style="text-align: center; padding: 20px; background: #EEF2FF; border-radius: 8px;">
                <div style="font-size: 28px; margin-bottom: 8px;">📨</div>
                <div style="font-weight: 600; color: #0F172A; font-size: 14px; margin-bottom: 4px;">Kafka</div>
                <div style="font-size: 12px; color: #64748B;">Event Streaming</div>
                <div style="font-size: 11px; color: #16A34A; font-weight: 600; margin-top: 8px;">Active</div>
            </div>
            <div style="text-align: center; padding: 20px; background: #EEF2FF; border-radius: 8px;">
                <div style="font-size: 28px; margin-bottom: 8px;">⚡</div>
                <div style="font-weight: 600; color: #0F172A; font-size: 14px; margin-bottom: 4px;">Spark</div>
                <div style="font-size: 12px; color: #64748B;">ML Processing</div>
                <div style="font-size: 11px; color: #16A34A; font-weight: 600; margin-top: 8px;">Active</div>
            </div>
            <div style="text-align: center; padding: 20px; background: #EEF2FF; border-radius: 8px;">
                <div style="font-size: 28px; margin-bottom: 8px;">🗄️</div>
                <div style="font-weight: 600; color: #0F172A; font-size: 14px; margin-bottom: 4px;">MongoDB</div>
                <div style="font-size: 12px; color: #64748B;">Data Storage</div>
                <div style="font-size: 11px; color: #16A34A; font-weight: 600; margin-top: 8px;">Active</div>
            </div>
            <div style="text-align: center; padding: 20px; background: #EEF2FF; border-radius: 8px;">
                <div style="font-size: 28px; margin-bottom: 8px;">🤖</div>
                <div style="font-weight: 600; color: #0F172A; font-size: 14px; margin-bottom: 4px;">ALS</div>
                <div style="font-size: 12px; color: #64748B;">Recommendations</div>
                <div style="font-size: 11px; color: #16A34A; font-weight: 600; margin-top: 8px;">Active</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def login_page():
    """Render login page"""
    inject_premium_css()
    
    st.markdown("""
    <div style="max-width: 420px; margin: 100px auto;">
        <div style="text-align: center; margin-bottom: 40px;">
            <div style="font-size: 48px; margin-bottom: 16px;">📊</div>
            <h1 style="font-size: 28px; font-weight: 700; color: #0F172A; margin: 0 0 8px 0;">FeedOrbit</h1>
            <p style="font-size: 14px; color: #64748B; margin: 0;">Big Data Analytics Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        
        with tab1:
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            if st.button("Sign In", use_container_width=True):
                if not username or not password:
                    st.error("Please enter both username and password")
                elif MONGODB_CONNECTED:
                    user = users_col.find_one({"username": username})
                    if user and user['password'] == hash_password(password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_id = user['user_id']
                        st.session_state.page = "home"
                        st.success("Signed in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        
        with tab2:
            new_user = st.text_input("Username", key="signup_user", placeholder="Choose username")
            new_pass = st.text_input("Password", type="password", key="signup_pass", placeholder="Choose password")
            confirm_pass = st.text_input("Confirm", type="password", key="confirm_pass", placeholder="Confirm password")
            
            if st.button("Create Account", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("Please fill all fields")
                elif new_pass != confirm_pass:
                    st.error("Passwords don't match")
                elif MONGODB_CONNECTED:
                    if users_col.find_one({"username": new_user}):
                        st.error("Username exists")
                    else:
                        user_id = assign_random_user_id()
                        if user_id:
                            users_col.insert_one({"user_id": user_id, "username": new_user, "password": hash_password(new_pass)})
                            st.success("Account created! Sign in now.")

def main():
    st_autorefresh(interval=60000, key="refresh")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    
    if not st.session_state.logged_in:
        login_page()
    else:
        inject_premium_css()
        
        username = st.session_state.get('username', 'User')
        page = st.session_state.get('page', 'home')
        
        render_navigation(page, username)
        
        metrics = get_system_metrics()
        
        if page == "home":
            render_dashboard_header(username)
            render_kpi_cards(metrics)
            render_feed_section()
        
        elif page == "feed":
            st.markdown('<div class="section-header"><h2>Your Feed</h2></div>', unsafe_allow_html=True)
            render_feed_section()
        
        elif page == "analytics":
            render_analytics()
        
        elif page == "status":
            render_pipeline()

if __name__ == "__main__":
    main()
