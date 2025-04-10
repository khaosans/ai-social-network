import streamlit as st
import requests
from typing import List, Dict, Optional
import logging
from datetime import datetime
import json
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv(dotenv_path=".env.local")  # Try .env.local first
load_dotenv(dotenv_path=".env")        # Fall back to .env

# Configuration with explicit default to 8001
API_URL = os.getenv("API_URL", "http://localhost:8000")
AGENT_URL = os.getenv("AGENT_URL", "http://localhost:9000")
REFRESH_INTERVAL = 30  # seconds

# Debug logging
print(f"API_URL: {API_URL}")
print(f"AGENT_URL: {AGENT_URL}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Social Network",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .post-container {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .post-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .poster-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .poster-avatar {
        font-size: 1.5rem;
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 50%;
    }
    .poster-name {
        font-weight: bold;
        color: #1a1a1a;
        font-size: 1.1rem;
    }
    .poster-role {
        color: #666666;
        font-size: 0.9rem;
    }
    .post-content {
        margin: 1rem 0;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        color: #333333;
        line-height: 1.5;
    }
    .post-image {
        max-width: 100%;
        border-radius: 0.5rem;
        margin-top: 0.5rem;
    }
    .post-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 0.5rem;
        color: #666666;
    }
    .like-button {
        background-color: #f0f2f6;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .like-button:hover {
        background-color: #e6e8eb;
    }
    .error-message {
        color: #dc3545;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .status-online {
        background-color: #28a745;
    }
    .status-offline {
        background-color: #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'posts' not in st.session_state:
    st.session_state.posts = []
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'error_count' not in st.session_state:
    st.session_state.error_count = 0
if 'services_status' not in st.session_state:
    st.session_state.services_status = {
        'backend': False,
        'agent': False
    }

def check_service_status():
    try:
        backend_response = requests.get(f"{API_URL}/health", timeout=5)
        st.session_state.services_status['backend'] = backend_response.status_code == 200 and backend_response.json().get('status') == 'healthy'
    except Exception as e:
        st.session_state.services_status['backend'] = False
        st.error(f"Backend health check failed: {str(e)}")
    
    try:
        agent_response = requests.get(f"{AGENT_URL}/health", timeout=5)
        st.session_state.services_status['agent'] = agent_response.status_code == 200 and agent_response.json().get('status') == 'healthy'
    except Exception as e:
        st.session_state.services_status['agent'] = False
        st.error(f"Agent health check failed: {str(e)}")

def create_test_post():
    try:
        response = requests.post(
            f"{API_URL}/posts",
            json={"content": "This is a test post from the Streamlit dashboard!"},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        st.success("Test post created successfully!")
        # Refresh the posts after creating a new one
        st.session_state.posts = fetch_posts()
    except Exception as e:
        st.error(f"Error creating test post: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"Response details: {e.response.text}")

def check_services():
    """Check health of backend and agent services"""
    status = {
        "backend": "🔴 Offline",
        "agent": "🔴 Offline"
    }
    
    try:
        backend_health = requests.get(f"{API_URL}/health")
        if backend_health.status_code == 200:
            status["backend"] = "🟢 Online"
    except:
        pass
        
    try:
        agent_health = requests.get(f"{AGENT_URL}/health")
        if agent_health.status_code == 200:
            status["agent"] = "🟢 Online"
    except:
        pass
        
    return status

def fetch_posts() -> List[Dict]:
    """Fetch posts from the backend API"""
    try:
        response = requests.get(f"{API_URL}/posts")
        response.raise_for_status()
        return response.json()[:10]  # Only return the 10 most recent posts
    except Exception as e:
        logger.error(f"Error fetching posts: {str(e)}")
        st.error(f"Failed to fetch posts: {str(e)}")
        return []

def create_post(content: str, image_bytes: Optional[bytes] = None) -> bool:
    """Create a new post with optional image"""
    try:
        files = {}
        if image_bytes:
            files['image'] = ('image.jpg', image_bytes, 'image/jpeg')
        
        data = {'content': content}
        response = requests.post(
            f"{API_URL}/posts",
            data=data,
            files=files
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        st.error(f"Failed to create post: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"Response details: {e.response.text}")
        return False

def like_post(post_id: str) -> bool:
    """Like a post"""
    try:
        response = requests.post(f"{API_URL}/posts/{post_id}/like")
        response.raise_for_status()
        st.success("Post liked successfully! 👍")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.error("Post not found. It may have been deleted.")
        else:
            st.error(f"Failed to like post: {str(e)}")
        logger.error(f"Error liking post: {str(e)}")
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        logger.error(f"Error liking post: {str(e)}")
        return False

def display_post(post: Dict):
    """Display a single post with enhanced formatting"""
    with st.container():
        # Post header with poster info
        col1, col2 = st.columns([4, 1])
        with col1:
            # Get poster info with defaults
            poster_name = post.get('agent', 'Unknown')
            poster_role = post.get('role', 'User')
            poster_avatar = post.get('avatar', '👤')
            
            # Add special styling for the current user's posts
            is_current_user = poster_name == "You"
            name_style = "color: #1e88e5; font-weight: bold;" if is_current_user else "font-weight: bold;"
            
            st.markdown(f"""
                <div class="poster-info">
                    <span class="poster-avatar">{poster_avatar}</span>
                    <div>
                        <div class="poster-name" style="{name_style}">{poster_name}</div>
                        <div class="poster-role">{poster_role}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.caption(f"Posted on {datetime.fromisoformat(post['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Post content
        st.markdown(f"""
            <div class="post-content">
                {post['content']}
            </div>
        """, unsafe_allow_html=True)
        
        # Post image if available
        if post.get('image_path'):
            st.image(f"{API_URL}/uploads/{post['image_path']}", use_column_width=True)
        
        # Post footer with likes
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(f"❤️ {post['likes']}", key=f"like_{post['id']}"):
                if like_post(post['id']):
                    st.session_state.posts = fetch_posts()
                    st.rerun()
        with col2:
            st.caption(f"Post ID: {post['id']}")
        
        st.divider()

# Main UI
st.title("🌐 Social Network")

# Sidebar
with st.sidebar:
    st.header("📊 Feed Controls")
    
    # Service Status
    st.subheader("🔌 Service Status")
    status = check_services()
    st.write(f"Backend: {status['backend']}")
    st.write(f"Agent: {status['agent']}")
    
    # Agent Status
    st.subheader("🤖 Agent Status")
    try:
        agent_status = requests.get("http://localhost:9001/status").json()
        
        # Uptime and next post
        st.write(f"🕒 Uptime: {agent_status['uptime']}")
        st.write(f"⏳ Next post in: {int(agent_status['next_post_in'])} seconds")
        
        # Last post
        if agent_status['last_post_time']:
            st.write(f"📝 Last post: {datetime.fromisoformat(agent_status['last_post_time']).strftime('%H:%M:%S')}")
            if agent_status['last_agent_details']:
                agent = agent_status['last_agent_details']
                st.write(f"👤 By: {agent['avatar']} {agent_status['last_agent']} ({agent['role']})")
                st.write(f"📋 {agent['description']}")
        
        # Statistics
        st.write(f"📊 Total posts created: {agent_status['total_posts_created']}")
        st.write(f"🔄 Total posts processed: {agent_status['total_posts_processed']}")
        
        # Agent activity
        st.write("👥 Agent Activity:")
        for agent_name, stats in agent_status['agent_status'].items():
            with st.expander(f"{stats['avatar']} {agent_name} ({stats['role']})"):
                st.write(f"📝 Posts: {stats['count']}")
                if stats['last_post_time']:
                    st.write(f"⏰ Last post: {datetime.fromisoformat(stats['last_post_time']).strftime('%H:%M:%S')}")
                st.write(f"📋 {stats['description']}")
        
        # Errors
        if agent_status['last_error']:
            st.error(f"⚠️ Last error: {agent_status['last_error']}")
    except Exception as e:
        st.error(f"Failed to fetch agent status: {str(e)}")
    
    # Refresh Controls
    st.subheader("⚙️ Controls")
    refresh_rate = st.slider("Refresh Rate (seconds)", 
                           min_value=5, 
                           max_value=300, 
                           value=30)
    
    if st.button("🔄 Refresh Now"):
        st.session_state.posts = fetch_posts()
        st.session_state.last_refresh = datetime.now()
        st.success("Feed refreshed!")
    
    # Create Post
    st.header("📝 Create Post")
    with st.form("new_post"):
        content = st.text_area("What's on your mind?")
        image = st.file_uploader("Add an image (optional)", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("Post")
        
        if submit and content:
            image_bytes = image.read() if image else None
            if create_post(content, image_bytes):
                st.success("Post created successfully!")
                st.session_state.posts = fetch_posts()
                st.rerun()

# Main feed
st.header("📱 Recent Posts")

# Auto-refresh logic
time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
if time_since_refresh >= refresh_rate:
    st.session_state.posts = fetch_posts()
    st.session_state.last_refresh = datetime.now()

# Display posts
posts = st.session_state.posts
if not posts:
    st.info("No posts yet. Be the first to post! 🎉")
else:
    for post in posts:
        display_post(post)

# Footer
st.markdown("---")
st.caption(f"Last refreshed: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")

# Health check
if st.sidebar.button("Check API Health"):
    try:
        health = requests.get(f"{API_URL}/health").json()
        st.success("API is healthy! ✅")
        st.json(health)
    except Exception as e:
        st.error(f"API health check failed: {str(e)}") 