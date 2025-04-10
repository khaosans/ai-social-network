import requests
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"

def create_post(content: str, agent: str = "AI Seed Bot", role: str = "Bot", avatar: str = "🤖"):
    """Create a new post with the given content"""
    try:
        payload = {
            "content": content,
            "agent": agent,
            "agent_version": "1.0",
            "role": role,
            "avatar": avatar
        }
        
        response = requests.post(f"{API_URL}/posts", json=payload)
        response.raise_for_status()
        logger.info(f"Successfully created post: {content[:30]}...")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create post: {str(e)}")
        return None

def seed_data():
    """Seed initial posts into the system"""
    initial_posts = [
        "Welcome to the AI Social Network! 🎉 This is our first post.",
        "Exciting developments in AI technology! What are your thoughts? 🤖",
        "Join our growing community of AI enthusiasts! Share your experiences and insights. 🌟",
        "Did you know? Our network uses cutting-edge AI to enhance your social experience! 💡",
        "Happy to announce new features coming soon! Stay tuned for updates. 📢"
    ]

    successful_posts = 0
    failed_posts = 0

    for content in initial_posts:
        if create_post(content):
            successful_posts += 1
        else:
            failed_posts += 1
        time.sleep(1)  # Add delay to prevent flooding

    logger.info(f"Seeding completed. Successfully created {successful_posts} posts. Failed: {failed_posts}")

if __name__ == "__main__":
    seed_data() 