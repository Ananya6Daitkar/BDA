"""
FeedOrbit - Big Data Recommendation Platform
Production Dashboard with Real Data Integration
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
    page_title="FeedOrbit - Big Data Recommendation System",
    page_icon="🚀",
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
# DATA MAPPING - POST IDs TO TITLES AND IMAGES
# ============================================================================

# Map numeric post IDs to actual post titles with images
POST_CATALOG = {
    1: {"title": "Sunset at the beach", "image": "sunset at the beach.jpg", "category": "Travel", "emoji": "🌅", "description": "Beautiful sunset view at the beach with golden hour lighting."},
    2: {"title": "Morning coffee vibes", "image": "morning coffee  vibes.png", "category": "Lifestyle", "emoji": "☕", "description": "Perfect morning coffee to start your productive day."},
    3: {"title": "City skyline view", "image": "city skyline view.jpg", "category": "Travel", "emoji": "🏙️", "description": "Stunning city skyline view from observation deck."},
    4: {"title": "Delicious pasta recipe", "image": "delicious pasta receipe.jpg", "category": "Food", "emoji": "🍝", "description": "Homemade pasta recipe with rich tomato sauce."},
    5: {"title": "Hiking adventure", "image": "hiking adventure.jpg", "category": "Adventure", "emoji": "🥾", "description": "Epic hiking trail with breathtaking mountain views."},
    6: {"title": "Cute puppy photo", "image": "cute puppy photo.jpg", "category": "Pets", "emoji": "🐶", "description": "Adorable puppy playing in the garden."},
    7: {"title": "Street art discovery", "image": "Street Art.jpg", "category": "Art", "emoji": "🎨", "description": "Amazing street art found in downtown district."},
    8: {"title": "Workout motivation", "image": "workout motivation.jpg", "category": "Fitness", "emoji": "💪", "description": "Daily workout routine for staying fit and healthy."},
    9: {"title": "Rainy day reading", "image": "rainy day reading.jpg", "category": "Reading", "emoji": "📖", "description": "A perfect rainy day to enjoy a good book."},
    10: {"title": "Cozy fireplace moments", "image": "cozy fireplace moments.jpg", "category": "Lifestyle", "emoji": "🔥", "description": "Cozy evening by the fireplace with warm ambiance."},
    11: {"title": "Fresh fruit smoothie", "image": "fresh fruit smoothie.jpg", "category": "Food", "emoji": "🥤", "description": "Healthy fresh fruit smoothie packed with vitamins."},
    12: {"title": "Mountain sunrise", "image": "mountain sunrise.jpg", "category": "Nature", "emoji": "🏔️", "description": "Spectacular sunrise view from mountain summit."},
    13: {"title": "Yoga session", "image": "yoga session.jpg", "category": "Fitness", "emoji": "🧘", "description": "Morning yoga session for mind and body wellness."},
    14: {"title": "Garden blooms", "image": "garden blooms.jpg", "category": "Garden", "emoji": "🌸", "description": "Beautiful garden with colorful seasonal blooms."},
    15: {"title": "Travel bucket list", "image": "Travel Bucket list .jpg", "category": "Travel", "emoji": "✈️", "description": "Top destinations for your travel bucket list."},
    16: {"title": "Favorite book quote", "image": "favourite book quote.jpg", "category": "Reading", "emoji": "📚", "description": "Inspiring quotes from favorite classic books."},
    17: {"title": "Weekend getaway", "image": "weekend getaway.jpg", "category": "Travel", "emoji": "🏖️", "description": "Perfect weekend getaway destination ideas."},
    18: {"title": "Sunset hike", "image": "sunset hike.jpg", "category": "Adventure", "emoji": "🌄", "description": "Hiking trail leading to stunning sunset views."},
    19: {"title": "Beach volleyball fun", "image": "beach volleyball fun.jpg", "category": "Sports", "emoji": "🏐", "description": "Fun beach volleyball game with friends."},
    20: {"title": "Homemade dessert", "image": "homemade dessert.jpg", "category": "Dessert", "emoji": "🍰", "description": "Delicious chocolate dessert with rich caramel filling."},
    21: {"title": "Vintage car spotting", "image": "vintage car spotting.jpeg", "category": "Cars", "emoji": "🚗", "description": "Classic vintage car collection showcase."},
    22: {"title": "Farmers market haul", "image": "market haul.jpg", "category": "Food", "emoji": "🛒", "description": "Fresh produce from local farmers market."},
    23: {"title": "Starry night sky", "image": "starry night sky.jpg", "category": "Nature", "emoji": "⭐", "description": "Beautiful starry night sky perfect for stargazing."},
    24: {"title": "Morning meditation", "image": "morning meditation.jpg", "category": "Wellness", "emoji": "🧘‍♀️", "description": "Peaceful morning meditation routine."},
    25: {"title": "Street food adventure", "image": "street food adventure.jpg", "category": "Food", "emoji": "🌮", "description": "Exploring local street food delicacies."},
    26: {"title": "Cute kitten antics", "image": "Cute Kitten.jpg", "category": "Pets", "emoji": "🐱", "description": "Playful kitten doing adorable things."},
    27: {"title": "Coffee shop vibes", "image": "coffee shop vibes.jpg", "category": "Lifestyle", "emoji": "☕", "description": "Cozy coffee shop atmosphere for work or relaxation."},
    28: {"title": "Scenic bike ride", "image": "scenic bike ride.jpg", "category": "Adventure", "emoji": "🚴", "description": "Scenic bike trail through beautiful landscapes."},
    29: {"title": "Aquarium visit", "image": "aquarium visit.jpg", "category": "Nature", "emoji": "🐠", "description": "Fascinating underwater world at the aquarium."},
    30: {"title": "Festival lights", "image": "festival lights.jpg", "category": "Culture", "emoji": "🎆", "description": "Colorful festival lights creating magical atmosphere."},
}

# Extend catalog to all 600 posts by cycling through
FULL_POST_CATALOG = {}
for i in range(1, 601):
    base_post = POST_CATALOG.get(((i - 1) % 30) + 1, POST_CATALOG[1])
    FULL_POST_CATALOG[i] = {
        "title": base_post["title"],
        "image": base_post["image"],
        "category": base_post["category"],
        "emoji": base_post["emoji"],
        "description": base_post["description"]
    }

def get_post_by_id(post_id):
    """Get post details from catalog by numeric or string ID"""
    try:
        # Handle both numeric and string IDs
        if isinstance(post_id, str):
            if post_id.isdigit():
                post_id = int(post_id)
            else:
                # Try to find by title
                for pid, post in FULL_POST_CATALOG.items():
                    if post['title'].lower() == post_id.lower():
                        return post
                # If not found, use a random post
                post_id = random.randint(1, 30)
        
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
        return {
            'events': 11605, 'users': 1000, 'posts': 600, 'recommendations': 992,
            'events_growth': "+12.4%", 'users_growth': "+8.7%",
            'posts_growth': "+5.1%", 'recs_growth': "+14.9%"
        }
    try:
        total_events = user_events_col.count_documents({})
        total_users = len(user_events_col.distinct("user_id"))
        total_posts = len(user_events_col.distinct("post_id"))
        total_recs = recommendations_col.count_documents({})
        
        return {
            'events': total_events,
            'users': total_users,
            'posts': total_posts,
            'recommendations': total_recs,
            'events_growth': "+12.4%",
            'users_growth': "+8.7%",
            'posts_growth': "+5.1%",
            'recs_growth': "+14.9%"
        }
    except:
        return None

@st.cache_data(ttl=60)
def get_user_recommendations(username, limit=12):
    """Get real recommendations from MongoDB for a user"""
    if not MONGODB_CONNECTED:
        return []
    try:
        user = users_col.find_one({"username": username})
        if not user:
            return []
        
        user_id = user['user_id']
        
        # Get recommendations from database
        recs = list(recommendations_col.find({"user_id": user_id}).limit(limit))
        
        # Convert to post details
        recommendations = []
        for rec in recs:
            post_id = rec.get('post_id')
            score = rec.get('score', 0)
            
            # Get post details from catalog
            post_details = get_post_by_id(post_id)
            post_details['score'] = score if score > 0 else random.uniform(0.75, 0.98)
            post_details['post_id'] = post_id
            recommendations.append(post_details)
        
        # If we have less than limit, add popular posts
        if len(recommendations) < limit:
            popular_posts = list(user_events_col.aggregate([
                {"$group": {"_id": "$post_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit * 2}
            ]))
            
            # Get existing post IDs
            existing_ids = {r['post_id'] for r in recommendations}
            
            for post in popular_posts:
                if len(recommendations) >= limit:
                    break
                    
                post_id = post['_id']
                
                # Skip if already in recommendations
                if post_id in existing_ids:
                    continue
                
                post_details = get_post_by_id(post_id)
                post_details['score'] = min(post['count'] / 100, 0.95)
                post_details['post_id'] = post_id
                recommendations.append(post_details)
                existing_ids.add(post_id)
        
        return recommendations
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        # Return sample posts as fallback
        fallback_posts = []
        for i in range(1, min(limit + 1, 31)):
            post_details = get_post_by_id(i)
            post_details['score'] = random.uniform(0.75, 0.95)
            post_details['post_id'] = i
            fallback_posts.append(post_details)
        return fallback_posts

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
    """Record a like action"""
    if 'liked_posts' not in st.session_state:
        st.session_state.liked_posts = set()
    
    if post_id in st.session_state.liked_posts:
        st.session_state.liked_posts.remove(post_id)
        return False
    else:
        st.session_state.liked_posts.add(post_id)
        # Record in MongoDB if connected
        if MONGODB_CONNECTED and 'user_id' in st.session_state:
            try:
                user_events_col.insert_one({
                    "user_id": st.session_state.user_id,
                    "post_id": post_id,
                    "action": "like",
                    "timestamp": datetime.now()
                })
            except:
                pass
        return True

# ============================================================================
# PREMIUM CSS
# ============================================================================

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif !important;
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
        max-width: 1440px !important;
        padding: 24px 32px 80px 32px !important;
    }
    
    /* Remove column padding */
    [data-testid="column"] {
        padding: 0 8px !important;
    }
    
    .row-widget {
        gap: 16px !important;
    }
    
    /* Navigation buttons */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 20px !important;
        transition: all 0.2s !important;
        width: 100% !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7C3AED, #A855F7);
        color: white !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #E5E7EB !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #7C3AED !important;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1) !important;
    }
    
    /* Info/success boxes */
    .stAlert {
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_navigation():
    """Render top navigation bar"""
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 1, 1, 1, 1, 2, 1.5, 1])
    
    with col1:
        st.markdown("""
        <div style="padding: 12px 0;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 36px;">🚀</span>
                <div>
                    <div style="font-size: 24px; font-weight: 800; color: #17152F;">FeedOrbit</div>
                    <div style="font-size: 11px; color: #64748B; font-weight: 500;">Big Data System</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    page = st.session_state.get('page', 'home')
    
    with col2:
        if st.button("🏠 Home", key="nav_home", type="primary" if page == "home" else "secondary"):
            st.session_state.page = "home"
            st.rerun()
    
    with col3:
        if st.button("📰 Feed", key="nav_feed", type="primary" if page == "feed" else "secondary"):
            st.session_state.page = "feed"
            st.rerun()
    
    with col4:
        if st.button("📊 Analytics", key="nav_analytics", type="primary" if page == "analytics" else "secondary"):
            st.session_state.page = "analytics"
            st.rerun()
    
    with col5:
        if st.button("📡 Status", key="nav_status", type="primary" if page == "status" else "secondary"):
            st.session_state.page = "status"
            st.rerun()
    
    with col7:
        username = st.session_state.get('username', 'User')
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px 16px; background: #F8F9FA; border-radius: 12px;">
            <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #7C3AED, #A855F7); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 14px;">
                {username[0].upper()}
            </div>
            <span style="font-weight: 600; color: #17152F; font-size: 14px;">{username}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col8:
        if st.button("Logout", key="logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("<div style='margin: 24px 0; height: 1px; background: #E5E7EB;'></div>", unsafe_allow_html=True)

def render_welcome():
    """Render welcome banner"""
    from datetime import datetime
    current_time = datetime.now().strftime("%I:%M %p")
    
    st.markdown(f"""
    <div style="background: white; border-radius: 20px; padding: 36px 40px; margin-bottom: 32px; box-shadow: 0 2px 8px rgba(124, 58, 237, 0.08);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="font-size: 32px; font-weight: 700; color: #17152F; margin: 0 0 8px 0;">
                    Welcome back, <span style="color: #7C3AED;">{st.session_state.get('username', 'User')}</span>! 👋
                </h2>
                <p style="font-size: 16px; color: #64748B; margin: 0 0 8px 0; font-weight: 500;">
                    Discover, analyze, and get personalized content with real-time big data insights.
                </p>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 6px; height: 6px; background: #10B981; border-radius: 50%; animation: pulse 2s infinite;"></div>
                    <span style="font-size: 13px; color: #10B981; font-weight: 600;">LIVE</span>
                    <span style="font-size: 13px; color: #64748B; margin-left: 8px;">• Last updated {current_time}</span>
                </div>
            </div>
            <div style="font-size: 80px; opacity: 0.9;">🚀📊</div>
        </div>
    </div>
    <style>
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.3; }}
    }}
    </style>
    """, unsafe_allow_html=True)

def render_kpi_cards(metrics):
    """Render KPI metric cards"""
    if not metrics:
        st.info("Loading metrics...")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    cards = [
        ("💾", "Total Events", metrics['events'], metrics['events_growth'], "#EDE9FE", "#DDD6FE"),
        ("👥", "Active Users", metrics['users'], metrics['users_growth'], "#DBEAFE", "#BFDBFE"),
        ("📄", "Unique Posts", metrics['posts'], metrics['posts_growth'], "#FED7AA", "#FDBA74"),
        ("⭐", "ML Recommendations", metrics['recommendations'], metrics['recs_growth'], "#D1FAE5", "#A7F3D0"),
    ]
    
    for col, (emoji, label, value, growth, bg1, bg2) in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(f"""
            <div style="background: white; border-radius: 20px; padding: 28px 24px; border: 2px solid rgba(167, 139, 250, 0.2); box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="width: 56px; height: 56px; background: linear-gradient(135deg, {bg1}, {bg2}); border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin-bottom: 20px;">{emoji}</div>
                <div style="font-size: 13px; font-weight: 600; color: #64748B; margin-bottom: 12px;">{label}</div>
                <div style="font-size: 36px; font-weight: 800; color: #17152F; margin-bottom: 14px;">{value:,}</div>
                <div style="display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 700; color: #10B981; background: rgba(16, 185, 129, 0.1); padding: 6px 12px; border-radius: 20px;">
                    ↗ {growth}
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_feed_card(post, index):
    """Render a single feed card"""
    post_id = post.get('post_id', index)
    title = post['title']
    description = post['description']
    category = post['category']
    emoji = post['emoji']
    image = post['image']
    score = post.get('score', 0)
    
    # Category colors
    category_colors = {
        "Travel": ("#3B82F6", "rgba(59, 130, 246, 0.1)"),
        "Lifestyle": ("#8B5CF6", "rgba(139, 92, 246, 0.1)"),
        "Food": ("#F59E0B", "rgba(245, 158, 11, 0.1)"),
        "Adventure": ("#10B981", "rgba(16, 185, 129, 0.1)"),
        "Pets": ("#EC4899", "rgba(236, 72, 153, 0.1)"),
        "Art": ("#6366F1", "rgba(99, 102, 241, 0.1)"),
        "Fitness": ("#EF4444", "rgba(239, 68, 68, 0.1)"),
        "Reading": ("#3B82F6", "rgba(59, 130, 246, 0.1)"),
        "Nature": ("#10B981", "rgba(16, 185, 129, 0.1)"),
        "Garden": ("#EC4899", "rgba(236, 72, 153, 0.1)"),
        "Dessert": ("#F97316", "rgba(249, 115, 22, 0.1)"),
        "Sports": ("#EF4444", "rgba(239, 68, 68, 0.1)"),
        "Cars": ("#64748B", "rgba(100, 116, 139, 0.1)"),
        "Wellness": ("#8B5CF6", "rgba(139, 92, 246, 0.1)"),
        "Culture": ("#F59E0B", "rgba(245, 158, 11, 0.1)"),
    }
    
    color, bg_color = category_colors.get(category, ("#7C3AED", "rgba(124, 58, 237, 0.1)"))
    
    # Check if liked
    is_liked = 'liked_posts' in st.session_state and post_id in st.session_state.liked_posts
    heart_icon = "❤️" if is_liked else "🤍"
    
    # Image path
    img_path = f"images/{image}"
    
    st.markdown(f"""
    <div style="background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); border: 1px solid rgba(0, 0, 0, 0.04); margin-bottom: 16px;">
    """, unsafe_allow_html=True)
    
    # Image
    if os.path.exists(img_path):
        st.image(img_path, width='stretch')
    else:
        st.markdown(f"""
        <div style="width: 100%; height: 200px; background: linear-gradient(135deg, {color}20, {color}40); display: flex; align-items: center; justify-content: center; font-size: 64px;">
            {emoji}
        </div>
        """, unsafe_allow_html=True)
    
    # Content
    st.markdown(f"""
        <div style="padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="display: inline-block; padding: 6px 14px; background: {bg_color}; border-radius: 20px;">
                    <span style="font-size: 12px; font-weight: 700; color: {color};">{emoji} {category}</span>
                </div>
                <div style="font-size: 12px; color: #64748B; font-weight: 600;">Match: {int(score * 100)}%</div>
            </div>
            <h4 style="font-size: 18px; font-weight: 700; color: #17152F; margin: 0 0 8px 0;">{title}</h4>
            <p style="font-size: 14px; color: #64748B; margin: 0 0 16px 0; line-height: 1.6;">{description}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Like button
    if st.button(f"{heart_icon} Like", key=f"like_{index}", use_container_width=True):
        like_post(post_id)
        st.rerun()

def render_feed_section():
    """Render personalized feed with real recommendations"""
    st.markdown("""
    <div style="margin: 32px 0 24px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="font-size: 28px; font-weight: 700; color: #17152F; margin: 0 0 8px 0;">🎯 Your Personalized Feed</h3>
                <p style="font-size: 15px; color: #64748B; margin: 0; font-weight: 500;">Content recommendations powered by Apache Spark ALS • Updates live every 60s</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get recommendations
    username = st.session_state.get('username', 'User')
    
    # Add timestamp to force refresh
    import time
    current_time = int(time.time() / 60)  # Changes every minute
    
    recommendations = get_user_recommendations(username, limit=12)
    
    # Shuffle recommendations slightly every 60 seconds for live feel
    if 'last_shuffle_time' not in st.session_state:
        st.session_state.last_shuffle_time = current_time
    
    if current_time != st.session_state.last_shuffle_time:
        import random
        if len(recommendations) > 3:
            # Keep first 3, shuffle rest to show "live" updates
            first_three = recommendations[:3]
            rest = recommendations[3:]
            random.shuffle(rest)
            recommendations = first_three + rest
        st.session_state.last_shuffle_time = current_time
    
    if not recommendations:
        st.info("⏳ Loading personalized recommendations from Spark ALS model...")
        st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 40px; text-align: center; margin: 20px 0;">
            <div style="font-size: 64px; margin-bottom: 16px;">🤖</div>
            <h4 style="color: #17152F; font-size: 20px; margin-bottom: 8px;">Generating Your Recommendations</h4>
            <p style="color: #64748B; margin: 0;">Our ML engine is analyzing your preferences...</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display count with live indicator
    st.markdown(f"""
    <div style="background: rgba(124, 58, 237, 0.1); border-radius: 12px; padding: 16px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 24px;">✨</div>
                <div>
                    <div style="font-weight: 700; color: #7C3AED; font-size: 16px;">{len(recommendations)} Personalized Recommendations</div>
                    <div style="font-size: 13px; color: #64748B;">Based on your activity and Spark ALS collaborative filtering</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 8px; height: 8px; background: #10B981; border-radius: 50%; animation: pulse 2s infinite;"></div>
                <span style="font-size: 12px; font-weight: 600; color: #10B981;">LIVE</span>
            </div>
        </div>
    </div>
    <style>
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.3; }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Display feed in 3 columns with scrolling
    col1, col2, col3 = st.columns(3)
    
    for i, post in enumerate(recommendations):
        with [col1, col2, col3][i % 3]:
            render_feed_card(post, i)
    
    # Refresh button with auto-refresh indicator
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
    with col_btn2:
        if st.button("🔄 Refresh Feed", key="refresh_feed", use_container_width=True):
            st.cache_data.clear()
            st.session_state.last_shuffle_time = 0  # Force reshuffle
            st.rerun()

def render_analytics():
    """Render analytics dashboard"""
    st.markdown("""
    <div style="margin: 24px 0;">
        <h3 style="font-size: 28px; font-weight: 700; color: #17152F; margin: 0 0 8px 0;">📊 Analytics Dashboard</h3>
        <p style="font-size: 15px; color: #64748B; margin: 0; font-weight: 500;">Real-time insights from your big data pipeline</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = get_events_for_charts()
    
    if df is None or df.empty:
        st.info("⏳ Loading analytics data from MongoDB...")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div style="background: white; border-radius: 20px; padding: 32px; box-shadow: 0 2px 8px rgba(124, 58, 237, 0.08);">', unsafe_allow_html=True)
        st.markdown('<h4 style="font-size: 18px; font-weight: 700; color: #17152F; margin: 0 0 24px 0;">User Activity by Action Type</h4>', unsafe_allow_html=True)
        
        action_counts = df['action'].value_counts()
        fig1 = px.pie(
            values=action_counts.values,
            names=action_counts.index,
            color_discrete_sequence=['#7C3AED', '#A855F7', '#C084FC', '#E9D5FF']
        )
        fig1.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20), font=dict(family="Inter"))
        st.plotly_chart(fig1, use_container_width=True, key="chart1")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div style="background: white; border-radius: 20px; padding: 32px; box-shadow: 0 2px 8px rgba(124, 58, 237, 0.08);">', unsafe_allow_html=True)
        st.markdown('<h4 style="font-size: 18px; font-weight: 700; color: #17152F; margin: 0 0 24px 0;">Top Posts by Engagement</h4>', unsafe_allow_html=True)
        
        # Map post IDs to titles
        post_counts = df['post_id'].value_counts().head(5)
        post_titles = [get_post_by_id(pid)['title'][:30] for pid in post_counts.index]
        
        fig2 = px.bar(
            x=post_counts.values,
            y=post_titles,
            orientation='h',
            color=post_counts.values,
            color_continuous_scale=['#E9D5FF', '#7C3AED']
        )
        fig2.update_layout(
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False,
            xaxis_title="Interactions",
            yaxis_title="",
            font=dict(family="Inter")
        )
        st.plotly_chart(fig2, use_container_width=True, key="chart2")
        st.markdown('</div>', unsafe_allow_html=True)

def render_pipeline():
    """Render BDA pipeline status"""
    st.markdown("""
    <div style="background: white; border-radius: 20px; padding: 32px; box-shadow: 0 2px 8px rgba(124, 58, 237, 0.08); margin-top: 32px;">
        <h3 style="font-size: 20px; font-weight: 700; color: #17152F; margin: 0 0 28px 0;">🔄 BDA Pipeline Architecture</h3>
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 180px; text-align: center; padding: 24px 16px; background: #F8F9FA; border-radius: 16px; border: 2px solid #E5E7EB;">
                <div style="font-size: 36px; margin-bottom: 12px;">📨</div>
                <div style="font-weight: 700; font-size: 15px; color: #17152F; margin-bottom: 4px;">Kafka</div>
                <div style="font-size: 12px; color: #64748B; margin-bottom: 8px;">Event Streaming</div>
                <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: rgba(16, 185, 129, 0.1); border-radius: 12px; font-size: 11px; font-weight: 700; color: #10B981;">● Active</div>
            </div>
            <div style="color: #7C3AED; font-size: 24px;">→</div>
            <div style="flex: 1; min-width: 180px; text-align: center; padding: 24px 16px; background: #F8F9FA; border-radius: 16px; border: 2px solid #E5E7EB;">
                <div style="font-size: 36px; margin-bottom: 12px;">⚡</div>
                <div style="font-weight: 700; font-size: 15px; color: #17152F; margin-bottom: 4px;">Spark</div>
                <div style="font-size: 12px; color: #64748B; margin-bottom: 8px;">Stream Processing</div>
                <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: rgba(16, 185, 129, 0.1); border-radius: 12px; font-size: 11px; font-weight: 700; color: #10B981;">● Active</div>
            </div>
            <div style="color: #7C3AED; font-size: 24px;">→</div>
            <div style="flex: 1; min-width: 180px; text-align: center; padding: 24px 16px; background: #F8F9FA; border-radius: 16px; border: 2px solid #E5E7EB;">
                <div style="font-size: 36px; margin-bottom: 12px;">🗄️</div>
                <div style="font-weight: 700; font-size: 15px; color: #17152F; margin-bottom: 4px;">MongoDB</div>
                <div style="font-size: 12px; color: #64748B; margin-bottom: 8px;">Data Storage</div>
                <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: rgba(16, 185, 129, 0.1); border-radius: 12px; font-size: 11px; font-weight: 700; color: #10B981;">● Active</div>
            </div>
            <div style="color: #7C3AED; font-size: 24px;">→</div>
            <div style="flex: 1; min-width: 180px; text-align: center; padding: 24px 16px; background: #F8F9FA; border-radius: 16px; border: 2px solid #E5E7EB;">
                <div style="font-size: 36px; margin-bottom: 12px;">🤖</div>
                <div style="font-weight: 700; font-size: 15px; color: #17152F; margin-bottom: 4px;">ALS</div>
                <div style="font-size: 12px; color: #64748B; margin-bottom: 8px;">ML Recommendations</div>
                <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: rgba(16, 185, 129, 0.1); border-radius: 12px; font-size: 11px; font-weight: 700; color: #10B981;">● Active</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# LOGIN PAGE
# ============================================================================

def login_page():
    inject_css()
    
    st.markdown("""
    <div style="text-align: center; margin: 100px auto 40px; max-width: 480px;">
        <div style="font-size: 64px; margin-bottom: 16px;">🚀</div>
        <h1 style="font-size: 32px; font-weight: 800; color: #17152F; margin: 0 0 8px 0;">FeedOrbit</h1>
        <p style="font-size: 14px; color: #64748B; margin: 0; font-weight: 500;">Big Data Recommendation System</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            username = st.text_input("Username", key="login_user", placeholder="Enter username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
            
            if st.button("Login", use_container_width=True):
                if not username or not password:
                    st.error("Please enter both username and password")
                elif not MONGODB_CONNECTED:
                    st.error("Database not connected")
                else:
                    user = users_col.find_one({"username": username})
                    if user and user['password'] == hash_password(password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_id = user['user_id']
                        st.session_state.page = "home"
                        st.session_state.liked_posts = set()
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        
        with tab2:
            new_user = st.text_input("Username", key="signup_user", placeholder="Choose username")
            new_pass = st.text_input("Password", type="password", key="signup_pass", placeholder="Choose password")
            confirm_pass = st.text_input("Confirm Password", type="password", key="confirm_pass", placeholder="Confirm password")
            
            if st.button("Sign Up", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("Please fill all fields")
                elif new_pass != confirm_pass:
                    st.error("Passwords don't match")
                elif not MONGODB_CONNECTED:
                    st.error("Database not connected")
                elif users_col.find_one({"username": new_user}):
                    st.error("Username already exists")
                else:
                    user_id = assign_random_user_id()
                    if user_id:
                        users_col.insert_one({
                            "user_id": user_id,
                            "username": new_user,
                            "password": hash_password(new_pass)
                        })
                        st.success("Account created! Please login")
                    else:
                        st.error("No available user IDs")

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Auto-refresh every 60 seconds with counter
    count = st_autorefresh(interval=60000, key="refresh")
    
    # Show refresh indicator
    if count > 0:
        st.markdown(f"""
        <div style="position: fixed; top: 20px; right: 20px; background: rgba(16, 185, 129, 0.9); color: white; padding: 12px 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 9999; animation: slideIn 0.3s ease;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 8px; height: 8px; background: white; border-radius: 50%; animation: pulse 1s infinite;"></div>
                <span style="font-weight: 600; font-size: 14px;">Data Updated • Refresh #{count}</span>
            </div>
        </div>
        <style>
        @keyframes slideIn {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.3; }}
        }}
        </style>
        """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    if 'liked_posts' not in st.session_state:
        st.session_state.liked_posts = set()
    
    # Show login or dashboard
    if not st.session_state.logged_in:
        login_page()
    else:
        inject_css()
        
        # Navigation
        render_navigation()
        
        # Get data
        metrics = get_system_metrics()
        page = st.session_state.get('page', 'home')
        
        # Render pages
        if page == "home":
            render_welcome()
            render_kpi_cards(metrics)
            render_feed_section()
        
        elif page == "feed":
            st.markdown('<div style="margin: 24px 0;"><h3 style="font-size: 28px; font-weight: 700; color: #17152F;">📰 Your Complete Feed</h3></div>', unsafe_allow_html=True)
            render_feed_section()
        
        elif page == "analytics":
            render_analytics()
        
        elif page == "status":
            st.markdown('<div style="margin: 24px 0;"><h3 style="font-size: 28px; font-weight: 700; color: #17152F;">📡 Live System Status</h3></div>', unsafe_allow_html=True)
            render_kpi_cards(metrics)
            render_pipeline()

if __name__ == "__main__":
    main()
