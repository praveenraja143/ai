# 🎓 EduAI - Educational AI Platform

An intelligent educational assistant that answers questions with **text explanations** and **animated videos**, powered by a **local LLM** (no API keys required).

## ✨ Features

- 📝 **Text & Voice Input** - Ask questions by typing or speaking
- 🤖 **Local LLM** - Uses Ollama (Mistral/LLaMA) running on your machine
- 🎬 **Animated Explanations** - Auto-generates educational videos using Manim
- 🔒 **Privacy First** - All processing happens locally, no data sent to external APIs
- 🎨 **Modern UI** - Beautiful, responsive interface with glassmorphism design
- ⚡ **Real-time Processing** - Instant text answers, videos generated in background

## 🎯 Example Questions

- "What is the Pythagorean theorem?"
- "Explain Newton's first law of motion"
- "What is Bayes' theorem?"
- "Explain the quadratic formula"

## 📋 Requirements

- **Python 3.10+**
- **8GB RAM** (16GB recommended)
- **10GB free disk space** (for models)
- **Modern browser** (Chrome/Edge for voice input)

## 🚀 Quick Start

### Option 1: Windows One-Click (Easiest) ⚡

**First Time Setup:**
1. Double-click: `setup-first-time.bat`
2. Follow the prompts (installs everything automatically)

**Every Time After:**
1. Double-click: `start.bat`
2. Browser opens automatically to http://localhost:8000

**To Stop:**
- Press `Ctrl+C` in the terminal, or
- Double-click: `stop.bat`

---

### Option 2: Automated Setup (Cross-Platform)

```bash
# Clone or download the project
cd guvi

# Run setup script
python setup.py
```

The setup script will:
1. ✅ Check Python version
2. ✅ Install Python dependencies
3. ✅ Install Ollama
4. ✅ Download LLM model (~4-7GB)
5. ✅ Create necessary directories

### Option 2: Manual Setup

#### Step 1: Install Ollama

**Windows:**
1. Download from [ollama.ai/download](https://ollama.ai/download)
2. Run the installer
3. Open terminal and run: `ollama serve`

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

#### Step 2: Download LLM Model

```bash
# Choose one:
ollama pull mistral      # 7B - Fast and efficient (Recommended)
ollama pull llama3       # 8B - High quality
ollama pull phi3         # 3.8B - Lightweight
```

#### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Create Directories

```bash
mkdir videos temp
```

## 🎮 Usage

### Start the Server

```bash
python app.py
```

You should see:
```
🚀 Starting Educational AI Platform...
✅ Ollama is running
✅ Model 'mistral' is ready
🌐 Server running at http://localhost:8000
```

### Open the Web Interface

Open your browser to: **http://localhost:8000**

### Ask Questions

1. **Text Input**: Type your question in the text area
2. **Voice Input**: Click the microphone button and speak
3. Click "Ask Question"
4. Get instant text answer + animated video explanation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Frontend (Browser)                │
│  - HTML/CSS/JavaScript                      │
│  - Web Speech API (Voice Input)             │
│  - Video Player                             │
└──────────────┬──────────────────────────────┘
               │ HTTP/REST API
┌──────────────▼──────────────────────────────┐
│         FastAPI Backend                     │
│  - Question Processing                      │
│  - Async Video Generation                   │
└──────┬──────────────────┬───────────────────┘
       │                  │
┌──────▼──────┐    ┌──────▼──────────────────┐
│  LLM Engine │    │  Animation Generator    │
│  (Ollama)   │    │  (Manim)                │
│  - Mistral  │    │  - Math Animations      │
│  - LLaMA3   │    │  - Visual Explanations  │
└─────────────┘    └─────────────────────────┘
```

## 📁 Project Structure

```
guvi/
├── app.py                    # FastAPI backend server
├── llm_engine.py             # Ollama LLM integration
├── animation_generator.py    # Manim video generation
├── config.py                 # Configuration settings
├── setup.py                  # Automated setup script
├── requirements.txt          # Python dependencies
├── index.html                # Frontend interface
├── style.css                 # Premium styling
├── script.js                 # Frontend logic + voice input
├── videos/                   # Generated videos (auto-created)
├── temp/                     # Temporary files (auto-created)
└── README.md                 # This file
```

## 🔧 Configuration

Edit `config.py` to customize:

- **LLM Model**: Change `LLM_CONFIG["model"]` to use different models
- **Video Quality**: Adjust `ANIMATION_CONFIG["quality"]` (low/medium/high/production)
- **Resolution**: Set `ANIMATION_CONFIG["resolution"]` (480p/720p/1080p)
- **Server Port**: Modify `SERVER_CONFIG["port"]`

## 🎨 Customization

### Switch LLM Model

```python
# In config.py
LLM_CONFIG = {
    "model": "llama3",  # Change to llama3, phi3, etc.
    ...
}
```

Or use the API:
```bash
curl -X POST http://localhost:8000/api/switch-model/llama3
```

### Adjust Video Quality

```python
# In config.py
ANIMATION_CONFIG = {
    "quality": "high_quality",  # low, medium, high, production
    "resolution": "1080p",      # 480p, 720p, 1080p
    "fps": 60,                  # Frame rate
}
```

## 🐛 Troubleshooting

### Ollama Not Running

**Error**: `Ollama is not running`

**Solution**:
```bash
# Start Ollama service
ollama serve
```

### Model Not Found

**Error**: `Model 'mistral' not found`

**Solution**:
```bash
# Download the model
ollama pull mistral
```

### Voice Input Not Working

**Issue**: Microphone button disabled

**Solution**:
- Use Chrome or Edge browser (Web Speech API support)
- Allow microphone permissions when prompted
- Check browser console for errors

### Video Generation Fails

**Issue**: Videos not appearing

**Solution**:
1. Check Manim installation: `manim --version`
2. Verify `videos/` directory exists
3. Check server logs for errors
4. Try reducing video quality in `config.py`

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```python
# In config.py, change the port
SERVER_CONFIG = {
    "port": 8001,  # Use different port
}
```

## 🔌 API Endpoints

### POST `/api/ask`
Ask a question and get answer + video

**Request**:
```json
{
  "question": "What is the Pythagorean theorem?",
  "context": "optional context"
}
```

**Response**:
```json
{
  "task_id": "abc123",
  "answer": "The Pythagorean theorem states...",
  "topic": "mathematics",
  "status": "processing"
}
```

### GET `/api/status/{task_id}`
Check video generation status

**Response**:
```json
{
  "task_id": "abc123",
  "status": "completed",
  "video_url": "/videos/abc123.mp4"
}
```

### GET `/api/health`
Check system health

**Response**:
```json
{
  "status": "healthy",
  "ollama_running": true,
  "model_available": true,
  "model": "mistral"
}
```

## 🚀 Performance Tips

1. **Use GPU**: If available, Manim will use GPU acceleration
2. **Lower Quality**: For faster videos, use `medium_quality` or `low_quality`
3. **Smaller Models**: Use `phi3` (3.8B) for faster responses
4. **Increase RAM**: 16GB+ recommended for smooth operation

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new animation templates
- Improve LLM prompts
- Enhance the UI/UX
- Fix bugs

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review server logs
3. Verify system requirements

## 🎓 Educational Use

This platform is designed for educational purposes. It can help students:
- Understand complex concepts visually
- Learn at their own pace
- Get instant explanations
- See mathematical concepts animated

Perfect for:
- Self-study
- Homework help
- Concept review
- Visual learning

---

**Built with ❤️ for education**

*Powered by Ollama, Manim, FastAPI, and Web Speech API*
