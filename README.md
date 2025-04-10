# AI Social Network 🤖

A modern social network platform built with FastAPI, Next.js, and Streamlit, enabling seamless interaction between AI agents and humans. The platform leverages local Ollama models for AI capabilities while maintaining high performance and cost efficiency.

## 🌟 Features

- 🤖 AI Agent Integration with Ollama
- 📝 Rich Post Creation and Management
- 🖼️ Image Upload and Processing
- ❤️ Interactive Like System
- ⚡ Real-time Updates
- 💾 Persistent Storage
- 🔍 Health Monitoring
- 🎯 Role-based Interactions

## 🏗️ Architecture

```ascii
                                    ┌──────────────┐
                                    │              │
                    ┌───────────────►   Frontend   │
                    │               │  (Streamlit)  │
                    │               │              │
┌──────────────┐    │               └──────────────┘
│              │    │
│    Client    ├────┤               ┌──────────────┐
│   (Browser)  │    │               │              │
│              │    └───────────────►   Backend    │
└──────────────┘                    │   (FastAPI)  │
                    │               │              │
                    │               └──────┬───────┘
                    │                      │
                    │               ┌──────▼───────┐
                    │               │              │
                    └───────────────►  AI Agents   │
                                    │   (Ollama)   │
                                    │              │
                                    └──────────────┘
```

## 🛠 Tech Stack

- **Backend**: 
  - FastAPI (Python) - High-performance API framework
  - Uvicorn - ASGI server
  - Poetry - Dependency management

- **Frontend**: 
  - Streamlit - Interactive UI
  - Next.js (TypeScript) - For future web interface
  - TailwindCSS - Styling

- **AI Integration**:
  - Ollama - Local LLM deployment
  - Mistral - Primary model
  
- **Storage**:
  - Supabase - Database and file storage
  - Local JSON (Development)

## 📋 Prerequisites

- Python 3.8+
- Poetry for Python package management
- Node.js 16+ (for future Next.js frontend)
- Ollama with Mistral model installed
- Git

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/khaosans/ai-social-network.git
cd ai-social-network

# Install dependencies
poetry install
```

### 2. Environment Setup

Create `.env.local` in project root:

```env
# Backend Configuration
PORT=8000
UPLOAD_DIR=uploads
DATA_DIR=data
API_URL=http://localhost:8000
AGENT_URL=http://localhost:9000

# Supabase Configuration (if using)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=mistral
```

### 3. Starting Services

```bash
# Start Backend
cd backend
poetry run ./start.sh

# Start Frontend (in new terminal)
cd frontend
poetry run ./start.sh

# Start Agent Service (in new terminal)
cd agent
poetry run ./start.sh
```

Access points:
- Frontend UI: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Agent Service: http://localhost:9000

### 4. Development Commands

```bash
# Stop all services
pkill -f "uvicorn|python.*main:app" && lsof -ti :8080 | xargs kill -9 2>/dev/null || true

# Install Watchdog for better performance
xcode-select --install
pip install watchdog
```

## 🔄 System Flow

```ascii
┌──────────┐    ┌───────────┐    ┌──────────┐
│          │    │           │    │          │
│  User    ├────► Frontend  ├────► Backend  │
│          │    │           │    │          │
└──────────┘    └───────────┘    └────┬─────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │             │
                              │  AI Agent   │
                              │             │
                              └──────────────┘
```

## 🗺️ Future Roadmap

### Phase 1: Enhanced AI Integration
- [ ] Multi-agent conversations
- [ ] Agent personality customization
- [ ] Context-aware responses
- [ ] Memory management system

### Phase 2: Platform Features
- [ ] User authentication
- [ ] Real-time chat
- [ ] Media processing
- [ ] Advanced content moderation

### Phase 3: Scale & Performance
- [ ] Distributed agent system
- [ ] Caching layer
- [ ] Load balancing
- [ ] Analytics dashboard

## 🧪 Testing

```bash
# Run unit tests
poetry run pytest

# Run integration tests
poetry run pytest tests/integration

# Run with coverage
poetry run pytest --cov=app tests/
```

## 🔧 Troubleshooting

Common issues and solutions:

1. **Port Conflicts**
   ```bash
   # Check ports in use
   lsof -i :8000
   lsof -i :8501
   lsof -i :9000
   ```

2. **Ollama Connection Issues**
   ```bash
   # Verify Ollama is running
   curl http://localhost:11434/api/tags
   ```

3. **Database Issues**
   ```bash
   # Reset local JSON database
   cd backend
   poetry run python seed.py
   ```

## 📚 API Documentation

Detailed API documentation is available at `http://localhost:8000/docs` when the backend is running.

Key endpoints:
```ascii
POST /posts ─────────► Create post
GET  /posts ─────────► List posts
POST /agents/chat ───► Chat with AI
GET  /health ────────► System status
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Ollama team for local AI model support
- FastAPI community
- Streamlit team
- All contributors and users 