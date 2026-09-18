const video = document.getElementById('webcam-video');
const canvas = document.getElementById('output-canvas');
const ctx = canvas.getContext('2d');
const captureCanvas = document.getElementById('capture-canvas');
const captureCtx = captureCanvas.getContext('2d');

const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');

let currentFilter = '';
let isStreaming = false;
let animationId;
let processingFrame = false;

// Buttons
const btnCapture = document.getElementById('btn-capture');
const btnRecord = document.getElementById('btn-record');
const filterBtns = document.querySelectorAll('.filter-btn');
const galleryGrid = document.getElementById('gallery-grid');
const recIndicator = document.getElementById('recording-indicator');

// Recording
let mediaRecorder;
let recordedChunks = [];
let isRecording = false;
let recordStream;

// Setup Webcam
async function setupCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 },
            audio: false 
        });
        
        video.srcObject = stream;
        
        return new Promise((resolve) => {
            video.onloadedmetadata = () => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                captureCanvas.width = video.videoWidth;
                captureCanvas.height = video.videoHeight;
                
                statusDot.classList.add('ready');
                statusText.innerText = "Camera Ready";
                
                // Set up recording stream from the visible canvas
                // 30 fps capture rate
                recordStream = canvas.captureStream(30); 
                
                resolve(video);
            };
        });
    } catch (err) {
        statusText.innerText = "Camera Access Denied/Error";
        console.error("Error accessing webcam: ", err);
        alert("Please allow camera access to use FaceFilter AI.");
    }
}

// Process Frames
async function processFrameLoop() {
    if (!isStreaming) return;

    if (!processingFrame) {
        processingFrame = true;
        
        // Draw current video frame to hidden canvas
        captureCtx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);
        
        // Get base64 jpeg (adjust quality for performance)
        const imageData = captureCanvas.toDataURL('image/jpeg', 0.7);
        
        try {
            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image: imageData,
                    filter: currentFilter
                })
            });
            
            const data = await response.json();
            
            if (data.image) {
                // Draw processed image to visible canvas
                const img = new Image();
                img.onload = () => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    processingFrame = false;
                };
                img.src = data.image;
            } else {
                processingFrame = false;
            }
        } catch (err) {
            console.error("Error processing frame: ", err);
            processingFrame = false;
        }
    }
    
    animationId = requestAnimationFrame(processFrameLoop);
}

// Initialize
async function init() {
    await setupCamera();
    video.play();
    isStreaming = true;
    processFrameLoop();
}

// Set Filter
function setFilter(filterName) {
    currentFilter = filterName;
    
    // Update UI
    filterBtns.forEach(btn => {
        if (btn.dataset.filter === filterName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// Event Listeners for Filter Buttons
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        setFilter(btn.dataset.filter);
    });
});

// Photo Capture
function capturePhoto() {
    const dataUrl = canvas.toDataURL('image/png');
    
    // Create download link
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = `FaceFilter_Capture_${Date.now()}.png`;
    a.click();
    
    // Add to gallery
    const img = document.createElement('img');
    img.src = dataUrl;
    
    const div = document.createElement('div');
    div.className = 'gallery-item';
    div.appendChild(img);
    
    // Allow clicking gallery item to download again or view
    div.addEventListener('click', () => {
        a.click();
    });
    
    galleryGrid.prepend(div);
}

btnCapture.addEventListener('click', capturePhoto);

// Video Recording
function toggleRecording() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

function startRecording() {
    recordedChunks = [];
    
    try {
        // Try webm with vp9 first
        let options = { mimeType: 'video/webm;codecs=vp9' };
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options = { mimeType: 'video/webm;codecs=vp8' };
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options = { mimeType: 'video/webm' };
            }
        }
        
        mediaRecorder = new MediaRecorder(recordStream, options);
    } catch (e) {
        console.error('Exception while creating MediaRecorder:', e);
        return;
    }

    mediaRecorder.onstop = (event) => {
        const blob = new Blob(recordedChunks, {
            type: 'video/webm'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        document.body.appendChild(a);
        a.style = 'display: none';
        a.href = url;
        a.download = `FaceFilter_Video_${Date.now()}.webm`;
        a.click();
        window.URL.revokeObjectURL(url);
    };

    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            recordedChunks.push(event.data);
        }
    };

    mediaRecorder.start();
    isRecording = true;
    
    // Update UI
    btnRecord.classList.add('recording');
    btnRecord.innerHTML = '<span>⏹</span> Stop (R)';
    recIndicator.classList.remove('hidden');
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    isRecording = false;
    
    // Update UI
    btnRecord.classList.remove('recording');
    btnRecord.innerHTML = '<span>⏺</span> Record (R)';
    recIndicator.classList.add('hidden');
}

btnRecord.addEventListener('click', toggleRecording);

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    // Ignore if typing in an input field (though we don't have any, good practice)
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    switch(e.key) {
        case '1': setFilter('dog'); break;
        case '2': setFilter('sunglasses'); break;
        case '3': setFilter('crown'); break;
        case '4': setFilter('rainbow'); break;
        case '5': setFilter('neon'); break;
        case '6': setFilter('vintage'); break;
        case '7': setFilter('cyberpunk'); break;
        case '8': setFilter('sketch'); break;
        case '9': setFilter('pixelate'); break;
        case '0': setFilter('mirror'); break;
        case ' ': 
            e.preventDefault(); // Prevent page scroll
            capturePhoto(); 
            break;
        case 'r':
        case 'R':
            toggleRecording();
            break;
        case 'Escape':
            if (isRecording) stopRecording();
            setFilter('');
            break;
    }
});

// Start App
window.addEventListener('load', init);
