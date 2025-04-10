from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
from dotenv import load_dotenv
import os
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Agent Webhook",
    description="Webhook endpoint for AI agent interactions",
    version="1.0.0"
)

class WebhookPayload(BaseModel):
    post_id: str
    content: str
    image_path: Optional[str] = None

# In-memory storage for agent responses
agent_responses = {}

def process_with_agent(content: str) -> dict:
    """Process content with the AI agent"""
    try:
        # Simulate agent processing time
        time.sleep(1)
        
        # Here you would implement your actual agent logic
        # For now, we'll return a simple analysis
        return {
            "sentiment": "positive",  # This would be determined by the agent
            "topics": ["social", "network"],  # This would be determined by the agent
            "processed_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in agent processing: {str(e)}")
        raise

@app.post("/webhook")
async def handle_webhook(payload: WebhookPayload):
    try:
        logger.info(f"Received webhook for post {payload.post_id}")
        
        # Process with agent
        agent_response = process_with_agent(payload.content)
        
        # Store the response
        agent_responses[payload.post_id] = agent_response
        
        response = {
            "status": "success",
            "message": f"Processed post: {payload.content}",
            "post_id": payload.post_id,
            "agent_response": agent_response
        }
        
        logger.info(f"Processed webhook for post {payload.post_id}")
        return response
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/responses/{post_id}")
async def get_agent_response(post_id: str):
    """Get agent response for a specific post"""
    if post_id not in agent_responses:
        raise HTTPException(status_code=404, detail="No agent response found for this post")
    return agent_responses[post_id]

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "processed_posts": len(agent_responses),
        "last_processed": max(agent_responses.values(), key=lambda x: x["processed_at"])["processed_at"] if agent_responses else None
    } 