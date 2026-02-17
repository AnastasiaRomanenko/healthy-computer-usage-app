let currentStream = null;

async function startCamera(videoElement) {
    try {
        if (currentStream) return;

        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        currentStream = stream;
        videoElement.srcObject = stream;
    } catch (err) {
        console.error("Camera error:", err);
        alert("Camera access denied. Please enable camera permissions.");
    }
}

function stopCamera() {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
    }
}

function setupCameraSection(videoId, canvasId, buttonId, fileName) {
    const video = document.getElementById(videoId);
    const canvas = document.getElementById(canvasId);
    const button = document.getElementById(buttonId);

    if (!video || !canvas || !button) return;

    button.addEventListener('click', () => {
        if (!currentStream) {
            alert("Camera not active — open the scan section first.");
            return;
        }

        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        context.translate(canvas.width, 0);
        context.scale(-1, 1);
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL('image/png');
        const base64Data = imageData.replace(/^data:image\/png;base64,/, '');
        const filePath = window.fileAPI.saveImage(base64Data, fileName);

        alert(`Image "${fileName}" saved at:\n${filePath}`);
    });
}

function handleSectionChange() {
    const activeSection = document.querySelector('section.active');

    stopCamera();

    if (!activeSection) return;

    if (activeSection.id === 'relaxed_face') {
        startCamera(document.getElementById('camera-relaxed'));
    } else if (activeSection.id === 'calibrate_distance') {
        startCamera(document.getElementById('camera-distance'));
    }
}

const observer = new MutationObserver(() => handleSectionChange());
observer.observe(document.body, {
    attributes: true,
    subtree: true,
    attributeFilter: ['class']
});

document.addEventListener('DOMContentLoaded', () => {
    setupCameraSection('camera-relaxed', 'canvas-relaxed', 'capture-relaxed', 'backend/assets/relaxed_face');
    setupCameraSection('camera-distance', 'canvas-distance', 'capture-distance', 'backend/assets/calibrate_distance');
});