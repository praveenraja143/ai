// Educational AI Platform - Frontend JavaScript
// Handles user interactions, voice input, and API communication

// API Configuration
const API_BASE = window.location.origin;
const API_ENDPOINTS = {
    ask: `${API_BASE}/api/ask`,
    status: `${API_BASE}/api/status`,
    health: `${API_BASE}/api/health`
};

// DOM Elements
const questionInput = document.getElementById('questionInput');
const voiceBtn = document.getElementById('voiceBtn');
const submitBtn = document.getElementById('submitBtn');
const voiceVisualizer = document.getElementById('voiceVisualizer');
const responseSection = document.getElementById('responseSection');
const loadingState = document.getElementById('loadingState');
const answerDisplay = document.getElementById('answerDisplay');
const answerContent = document.getElementById('answerContent');
const topicBadge = document.getElementById('topicBadge');
const videoSection = document.getElementById('videoSection');
const videoStatus = document.getElementById('videoStatus');
const videoPlayer = document.getElementById('videoPlayer');
const videoSource = document.getElementById('videoSource');
const systemStatus = document.getElementById('systemStatus');
const exampleCards = document.querySelectorAll('.example-card');

// State
let isListening = false;
let recognition = null;
let currentTaskId = null;
let statusCheckInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeSpeechRecognition();
    checkSystemHealth();
    setupEventListeners();
});

// Speech Recognition Setup
function initializeSpeechRecognition() {
    // Check if browser supports Web Speech API
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.warn('Speech recognition not supported');
        voiceBtn.disabled = true;
        voiceBtn.querySelector('.voice-status').textContent = 'Not supported';
        return;
    }

    // Initialize recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    // Event handlers
    recognition.onstart = () => {
        isListening = true;
        voiceBtn.classList.add('listening');
        voiceVisualizer.classList.remove('hidden');
        voiceBtn.querySelector('.voice-status').textContent = 'Listening...';
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        questionInput.value = transcript;
        stopListening();
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        stopListening();
        showNotification('Voice input error. Please try again.', 'error');
    };

    recognition.onend = () => {
        stopListening();
    };
}

// Voice Input Controls
function startListening() {
    if (!recognition) {
        showNotification('Voice input not available', 'error');
        return;
    }

    try {
        recognition.start();
    } catch (error) {
        console.error('Failed to start recognition:', error);
    }
}

function stopListening() {
    isListening = false;
    voiceBtn.classList.remove('listening');
    voiceVisualizer.classList.add('hidden');
    voiceBtn.querySelector('.voice-status').textContent = 'Click to speak';

    if (recognition) {
        recognition.stop();
    }
}

// Event Listeners
function setupEventListeners() {
    // Voice button
    voiceBtn.addEventListener('click', () => {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    });

    // Submit button
    submitBtn.addEventListener('click', handleSubmit);

    // Enter key in textarea (Ctrl+Enter to submit)
    questionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            handleSubmit();
        }
    });

    // Example cards
    exampleCards.forEach(card => {
        card.addEventListener('click', () => {
            const question = card.dataset.question;
            questionInput.value = question;
            handleSubmit();
        });
    });
}

// Main Submit Handler
async function handleSubmit() {
    const question = questionInput.value.trim();

    if (!question) {
        showNotification('Please enter a question', 'warning');
        return;
    }

    // Show loading state
    responseSection.classList.remove('hidden');
    loadingState.classList.remove('hidden');
    answerDisplay.classList.add('hidden');
    videoSection.classList.add('hidden');

    // Disable submit button
    submitBtn.disabled = true;
    submitBtn.querySelector('span').textContent = 'Processing...';

    try {
        // Send question to API
        const response = await fetch(API_ENDPOINTS.ask, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            throw new Error('Failed to get response from server');
        }

        const data = await response.json();

        // Store task ID
        currentTaskId = data.task_id;

        // Hide loading, show answer
        loadingState.classList.add('hidden');
        displayAnswer(data.answer, data.topic);

        // Start checking for video
        startVideoStatusCheck();

    } catch (error) {
        console.error('Error:', error);
        loadingState.classList.add('hidden');
        showNotification('Failed to get answer. Please check if the server is running.', 'error');
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.querySelector('span').textContent = 'Ask Question';
    }
}

// Display Answer
function displayAnswer(answer, topic) {
    answerContent.textContent = answer;
    topicBadge.textContent = topic || 'General';
    answerDisplay.classList.remove('hidden');
}

// Video Status Checking
function startVideoStatusCheck() {
    if (!currentTaskId) return;

    // Show video section with loading state
    videoSection.classList.remove('hidden');
    videoStatus.classList.remove('hidden');
    videoPlayer.classList.add('hidden');

    // Check status every 2 seconds
    statusCheckInterval = setInterval(checkVideoStatus, 2000);

    // Also check immediately
    checkVideoStatus();
}

async function checkVideoStatus() {
    if (!currentTaskId) return;

    try {
        const response = await fetch(`${API_ENDPOINTS.status}/${currentTaskId}`);

        if (!response.ok) {
            throw new Error('Failed to check status');
        }

        const data = await response.json();

        if (data.status === 'completed' && data.video_url) {
            // Video is ready!
            clearInterval(statusCheckInterval);
            displayVideo(data.video_url);
        } else if (data.status === 'failed') {
            // Video generation failed
            clearInterval(statusCheckInterval);
            videoStatus.innerHTML = `
                <span style="color: var(--warning)">⚠️ Video generation failed</span>
            `;
        }
        // Otherwise, keep checking (status is "processing")

    } catch (error) {
        console.error('Error checking video status:', error);
        clearInterval(statusCheckInterval);
    }
}

// Display Video
function displayVideo(videoUrl) {
    videoStatus.classList.add('hidden');
    videoSource.src = videoUrl;
    videoPlayer.load();
    videoPlayer.classList.remove('hidden');

    // Auto-play with a slight delay
    setTimeout(() => {
        videoPlayer.play().catch(err => {
            console.log('Auto-play prevented:', err);
        });
    }, 500);
}

// System Health Check
async function checkSystemHealth() {
    try {
        const response = await fetch(API_ENDPOINTS.health);
        const data = await response.json();

        const statusDot = systemStatus.querySelector('.status-dot');
        const statusText = systemStatus.querySelector('.status-text');

        if (data.status === 'healthy') {
            statusDot.classList.add('online');
            statusText.textContent = `System Ready • ${data.model}`;
        } else {
            statusText.textContent = 'System Degraded';
            if (!data.ollama_running) {
                statusText.textContent += ' • Ollama not running';
            } else if (!data.model_available) {
                statusText.textContent += ' • Model not available';
            }
        }
    } catch (error) {
        console.error('Health check failed:', error);
        const statusText = systemStatus.querySelector('.status-text');
        statusText.textContent = 'Server Offline';
    }
}

// Notification System
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Style
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '1rem 1.5rem',
        background: type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#10b981',
        color: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
        zIndex: 1000,
        animation: 'slideInRight 0.3s ease',
        fontWeight: '500'
    });

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add notification animations to document
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Periodic health check (every 30 seconds)
setInterval(checkSystemHealth, 30000);
