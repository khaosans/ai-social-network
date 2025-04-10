from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os
from datetime import datetime
import uuid
import logging
import requests
import json
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class PostCreate(BaseModel):
    content: str
    agent: str | None = None
    agent_version: str | None = None
    role: str | None = None
    avatar: str | None = None
    
    class Config:
        from_attributes = True

class Post(PostCreate):
    id: str
    created_at: str
    likes: int = 0
    image: str | None = None

class PostResponse(BaseModel):
    message: str
    likes: int

class HealthResponse(BaseModel):
    status: str
    post_count: int
    version: str

app = FastAPI(title="Simple Social Network API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure data directory exists
DATA_DIR = "data"
POSTS_FILE = os.path.join(DATA_DIR, "posts.json")
os.makedirs(DATA_DIR, exist_ok=True)

# Load posts from file or initialize empty list
def load_posts():
    try:
        if os.path.exists(POSTS_FILE):
            with open(POSTS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading posts: {str(e)}")
        return []

def save_posts(posts_data):
    try:
        with open(POSTS_FILE, 'w') as f:
            json.dump(posts_data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving posts: {str(e)}")

# Initialize posts from file
posts = load_posts()

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

async def save_upload_file(upload_file: UploadFile, post_id: str) -> str:
    """Save an uploaded file and return its path"""
    try:
        file_extension = os.path.splitext(upload_file.filename)[1]
        filename = f"{post_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as f:
            content = await upload_file.read()
            f.write(content)
        
        return f"/uploads/{filename}"
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not save file")

@app.post("/posts", response_model=Post)
async def create_post(
    content: str = Form(...),
    agent: str | None = Form(None),
    agent_version: str | None = Form(None),
    role: str | None = Form(None),
    avatar: str | None = Form(None),
    image: UploadFile | None = None
):
    post_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Handle image upload if provided
    image_path = None
    if image:
        try:
            image_path = await save_upload_file(image, post_id)
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save image")

    new_post = Post(
        id=post_id,
        content=content,
        created_at=timestamp,
        likes=0,
        image=image_path,
        agent=agent,
        agent_version=agent_version,
        role=role,
        avatar=avatar
    )
    
    posts.append(new_post.dict())
    save_posts(posts)
    logger.info(f"Created new post with ID: {post_id}")
    return new_post

@app.get("/posts", response_model=List[Post])
async def get_posts() -> List[Post]:
    """Get all posts, sorted by creation date (newest first)."""
    sorted_posts = sorted(posts, key=lambda x: x["created_at"], reverse=True)
    return [Post(**post) for post in sorted_posts]

@app.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: str) -> Post:
    """Get a specific post by ID"""
    for post in posts:
        if post["id"] == post_id:
            return Post(**post)
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/posts/{post_id}/like", response_model=PostResponse)
async def like_post(post_id: str) -> PostResponse:
    """Like a post"""
    try:
        for post in posts:
            if post["id"] == post_id:
                post["likes"] += 1
                save_posts(posts)  # Save updated likes to file
                logger.info(f"Post {post_id} liked. Total likes: {post['likes']}")
                return PostResponse(message="Post liked successfully", likes=post["likes"])
        raise HTTPException(status_code=404, detail="Post not found")
    except Exception as e:
        logger.error(f"Error liking post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        post_count=len(posts),
        version="1.0.0"
    ) 