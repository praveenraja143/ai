import streamlit as st
import google.generativeai as genai
import os
import time
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="EduAI - Educational Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    st.markdown("""
        <style>
        .stchat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .user-message {
            background-color: #e6f3ff;
        }
        .assistant-message {
            background-color: #f0f2f6;
        }
        .video-container {
            margin-top: 1rem;
            border-radius: 0.5rem;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

load_css()

# Sidebar configuration
with st.sidebar:
    st.title("🎓 EduAI Settings")
    
    # API Key Management
    api_key = st.text_input("Gemini API Key", type="password", help="Get your key from Google AI Studio")
    if not api_key:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("API Key loaded from secrets")
        else:
            st.warning("Please enter your API Key to continue")
            st.markdown("[Get API Key](https://makersuite.google.com/app/apikey)")
    
    # Model Selection
    model_name = st.selectbox(
        "Select Model",
        ["gemini-pro", "gemini-1.5-flash"]
    )
    
    # Video Settings
    st.divider()
    st.subheader("Video Settings")
    generate_video_toggle = st.toggle("Generate Explainer Video", value=True)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This AI assistant explains complex topics and generates animated videos to help you learn.")

# Main content
st.title("🎓 Educational AI Assistant")
st.caption("Powered by Google Gemini & Manim")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "video_queue" not in st.session_state:
    st.session_state.video_queue = []

# Configure Gemini
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
else:
    st.info("Please set your Gemini API Key in the sidebar or secrets.")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("video"):
            st.video(message["video"])

# Helper to generate video
def create_educational_video(text, topic):
    """
    Generate a video based on the explanation
    """
    try:
        from video_pipeline.video_generator import generate_video
        from video_pipeline.script_generator import generate_script
        
        # Create a unique ID
        import uuid
        video_id = str(uuid.uuid4())[:8]
        
        # Progress bar
        progress_bar = st.progress(0, text="Analyzing content for video...")
        
        # 1. Generate Script
        progress_bar.progress(20, text="Writing script...")
        # Simple script generation if the complex one fails or is too slow
        script_scenes = [f"{topic}\n\n{text[:500]}"] 
        
        # 2. Generate Video
        progress_bar.progress(40, text="Rendering animation...")
        video_path = generate_video(script_scenes, video_id)
        
        progress_bar.progress(100, text="Video ready!")
        time.sleep(1)
        progress_bar.empty()
        
        return video_path
        
    except Exception as e:
        st.error(f"Video generation failed: {str(e)}")
        return None

# Chat input
if prompt := st.chat_input("Ask a question (e.g., 'Explain Newton's Laws')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Create a specific educational prompt
            system_prompt = """
            You are an expert educational tutor. 
            Explain the following concept clearly and concisely.
            Use simple language, examples, and analogies.
            Format with Markdown.
            """
            
            response = model.generate_content(f"{system_prompt}\n\nQuestion: {prompt}")
            full_response = response.text
            
            message_placeholder.markdown(full_response)
            
            video_path = None
            if generate_video_toggle:
                with st.spinner("Creating explainer video..."):
                    # Extract a topic title
                    topic_response = model.generate_content(f"Give a short 3-5 word title for this text: {prompt}")
                    topic = topic_response.text.strip()
                    
                    video_path = create_educational_video(full_response, topic)
                    if video_path and os.path.exists(video_path):
                        st.video(video_path)
            
            # Save assistant message
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response,
                "video": video_path if video_path and os.path.exists(video_path) else None
            })
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

