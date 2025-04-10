import asyncio
import logging
from typing import List, Dict
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
import random
from fastapi import FastAPI, HTTPException
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define agents configuration
AGENTS = [
    {
        "name": "Tech Enthusiast",
        "role": "AI Technology Expert",
        "description": "Passionate about the latest AI developments and tools",
        "avatar": "🤖",
        "templates": [
            "Just discovered an amazing AI tool! {emoji}",
            "The future of AI is looking bright! {emoji}",
            "Check out this cool tech development! {emoji}"
        ],
        "emojis": ["🤖", "💻", "🚀", "⚡"]
    },
    {
        "name": "Community Builder",
        "role": "Community Manager",
        "description": "Focused on building and engaging the AI community",
        "avatar": "🤝",
        "templates": [
            "Let's connect and share our AI experiences! {emoji}",
            "What's your favorite AI tool? {emoji}",
            "Join our growing community! {emoji}"
        ],
        "emojis": ["🤝", "🌟", "💡", "🎯"]
    },
    {
        "name": "AI Explorer",
        "role": "AI Researcher",
        "description": "Exploring the frontiers of artificial intelligence",
        "avatar": "🔍",
        "templates": [
            "Exploring new AI frontiers! {emoji}",
            "The possibilities with AI are endless! {emoji}",
            "Learning something new about AI every day! {emoji}"
        ],
        "emojis": ["🔍", "🎓", "💫", "🌌"]
    }
]

class AgentManager:
    def __init__(self):
        self.api_url = os.getenv("API_URL", "http://localhost:8000")
        self.agent_url = os.getenv("AGENT_URL", "http://localhost:9000")
        self.processed_posts = set()
        self.running = True
        self.last_agent_post = datetime.min
        self.status = {
            "last_post_time": None,
            "last_agent": None,
            "last_agent_details": None,
            "total_posts_created": 0,
            "total_posts_processed": 0,
            "last_error": None,
            "uptime": datetime.now(),
            "agent_status": {agent["name"]: {
                "count": 0,
                "last_post_time": None,
                "role": agent["role"],
                "description": agent["description"],
                "avatar": agent["avatar"]
            } for agent in AGENTS}
        }
        
    async def create_agent_post(self):
        """Create a new post from an agent"""
        try:
            # Check if enough time has passed since last agent post
            time_since_last_post = (datetime.now() - self.last_agent_post).total_seconds()
            if time_since_last_post < 60:  # Reduced to 1 minute between posts
                return
            
            # Select a random agent
            agent = random.choice(AGENTS)
            template = random.choice(agent["templates"])
            emoji = random.choice(agent["emojis"])
            
            # Create the post content
            content = template.format(emoji=emoji)
            
            # Send the post to the API
            response = requests.post(
                f"{self.api_url}/posts",
                data={
                    "content": content,
                    "agent": agent["name"],
                    "role": agent["role"],
                    "avatar": agent["avatar"],
                    "agent_version": "1.0.0"
                }
            )
            response.raise_for_status()
            
            # Update status
            now = datetime.now()
            self.status["last_post_time"] = now
            self.status["last_agent"] = agent["name"]
            self.status["last_agent_details"] = {
                "role": agent["role"],
                "description": agent["description"],
                "avatar": agent["avatar"]
            }
            self.status["total_posts_created"] += 1
            self.status["agent_status"][agent["name"]]["count"] += 1
            self.status["agent_status"][agent["name"]]["last_post_time"] = now
            self.status["last_error"] = None
            
            logger.info(f"Agent '{agent['name']}' ({agent['role']}) created a new post: {content}")
            self.last_agent_post = now
            
        except Exception as e:
            error_msg = f"Error creating agent post: {str(e)}"
            logger.error(error_msg)
            self.status["last_error"] = error_msg
    
    async def process_new_posts(self):
        """Process new posts that haven't been handled by agents yet"""
        try:
            response = requests.get(f"{self.api_url}/posts")
            response.raise_for_status()
            posts = response.json()
            
            for post in posts:
                if post["id"] not in self.processed_posts:
                    logger.info(f"Processing new post: {post['id']}")
                    await self.send_to_agent(post)
                    self.processed_posts.add(post["id"])
                    self.status["total_posts_processed"] += 1
        except Exception as e:
            error_msg = f"Error processing posts: {str(e)}"
            logger.error(error_msg)
            self.status["last_error"] = error_msg
    
    async def send_to_agent(self, post: Dict):
        """Send post to agent for processing"""
        try:
            payload = {
                "post_id": post["id"],
                "content": post["content"],
                "image_path": post.get("image_path")
            }
            
            response = requests.post(
                f"{self.agent_url}/webhook",
                json=payload
            )
            response.raise_for_status()
            logger.info(f"Successfully processed post {post['id']} with agent")
        except Exception as e:
            error_msg = f"Error sending to agent: {str(e)}"
            logger.error(error_msg)
            self.status["last_error"] = error_msg
    
    async def health_check(self):
        """Periodic health check of agent service"""
        try:
            response = requests.get(f"{self.agent_url}/health")
            response.raise_for_status()
            logger.info("Agent health check successful")
            return True
        except Exception as e:
            error_msg = f"Agent health check failed: {str(e)}"
            logger.error(error_msg)
            self.status["last_error"] = error_msg
            return False
    
    async def run(self):
        """Main loop for agent manager"""
        logger.info("Starting Agent Manager")
        
        # Create first post immediately
        await self.create_agent_post()
        
        while self.running:
            try:
                # Check agent health
                if not await self.health_check():
                    logger.warning("Agent service is not healthy, attempting to restart...")
                    # Here you would implement agent service restart logic
                
                # Process new posts
                await self.process_new_posts()
                
                # Create new agent posts
                await self.create_agent_post()
                
                # Sleep for a while before next iteration
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                error_msg = f"Error in agent manager loop: {str(e)}"
                logger.error(error_msg)
                self.status["last_error"] = error_msg
                await asyncio.sleep(5)  # Wait before retrying

    def get_status(self):
        """Get current status of the agent manager"""
        return {
            **self.status,
            "uptime": str(datetime.now() - self.status["uptime"]),
            "next_post_in": max(0, 60 - (datetime.now() - self.last_agent_post).total_seconds()),
            "agents": AGENTS  # Include full agent information
        }

# Create FastAPI app for status endpoint
app = FastAPI(title="Agent Manager Status")

@app.get("/status")
async def get_status():
    return manager.get_status()

async def main():
    global manager
    manager = AgentManager()
    
    # Start the status server
    config = uvicorn.Config(app, host="0.0.0.0", port=9001)
    server = uvicorn.Server(config)
    
    # Run both the agent manager and status server
    await asyncio.gather(
        manager.run(),
        server.serve()
    )

if __name__ == "__main__":
    asyncio.run(main()) 