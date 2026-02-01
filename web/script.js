const videoElement = document.getElementById('input_video');
const canvasElement = document.getElementById('output_canvas');
const canvasCtx = canvasElement.getContext('2d');

const earBar = document.getElementById('ear-bar');
const earValue = document.getElementById('ear-value');
const systemStatus = document.getElementById('system-status');
const warningBox = document.getElementById('drowsiness-warning');
const alertOverlay = document.getElementById('alert-overlay');
const startScreen = document.getElementById('start-screen');
const startBtn = document.getElementById('start-btn');

// EAR Thresholds
const EAR_THRESHOLD = 0.25;
const EAR_CONSEC_FRAMES = 20; // Approx 1-2 seconds dependent on FPS

let counter = 0;
let isDrowsy = false;
let alertPlaying = false;

// Audio Synthesis
const synth = window.speechSynthesis;
let warningUtterance = new SpeechSynthesisUtterance("Kamu ngantuk Khalifa! Segera tidur ya");
warningUtterance.lang = 'id-ID';
warningUtterance.rate = 1.0;

// Indices for Eye Landmarks in Face Mesh
// Left Eye
const LEFT_EYE = [362, 385, 387, 263, 373, 380];
// Right Eye
const RIGHT_EYE = [33, 160, 158, 133, 153, 144];

function euclideanDistance(p1, p2) {
    const x = p2.x - p1.x;
    const y = p2.y - p1.y;
    // z is often ignored for simple aspect ratio but MediaPipe provides it
    return Math.sqrt(x*x + y*y);
}

function calculateEAR(eyeLandmarks, w, h) {
    // eyeLandmarks is array of NormalizedLandmark
    // Indices in FaceMesh:
    // P1: 1 (top 1) - P5: 5 (bottom 1) -> 385, 373 (Left)
    // P2: 2 (top 2) - P4: 4 (bottom 2) -> 387, 380 (Left)
    // P0: 0 (left)  - P3: 3 (right)    -> 362, 263 (Left)
    
    // Mapping our simple indices [0..5] to the points logic
    const p1 = eyeLandmarks[1];
    const p5 = eyeLandmarks[5];
    const p2 = eyeLandmarks[2];
    const p4 = eyeLandmarks[4];
    const p0 = eyeLandmarks[0];
    const p3 = eyeLandmarks[3];

    const A = euclideanDistance(p1, p5);
    const B = euclideanDistance(p2, p4);
    const C = euclideanDistance(p0, p3);

    const ear = (A + B) / (2.0 * C);
    return ear;
}

function onResults(results) {
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    // Draw video not needed since we have <video> behind, but if we wanted to process:
    // canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

    if (results.multiFaceLandmarks) {
        for (const landmarks of results.multiFaceLandmarks) {
            
            // Extract Eye Points
            const leftEyePoints = LEFT_EYE.map(index => landmarks[index]);
            const rightEyePoints = RIGHT_EYE.map(index => landmarks[index]);

            const leftEAR = calculateEAR(leftEyePoints);
            const rightEAR = calculateEAR(rightEyePoints);

            const avgEAR = (leftEAR + rightEAR) / 2.0;
            
            updateHUD(avgEAR);
            detectDrowsiness(avgEAR);
        }
    }
    canvasCtx.restore();
}

function updateHUD(ear) {
    earValue.innerText = ear.toFixed(2);
    
    // Bar Height (scale roughly 0.0 to 0.4)
    let fillPercent = (ear / 0.4) * 100;
    if (fillPercent > 100) fillPercent = 100;
    if (fillPercent < 0) fillPercent = 0;
    
    earBar.style.height = `${fillPercent}%`;

    // Color Logic
    if (ear < EAR_THRESHOLD) {
        earBar.style.backgroundColor = "var(--danger-color)";
    } else {
        earBar.style.backgroundColor = "var(--primary-color)";
    }
}

function detectDrowsiness(ear) {
    if (ear < EAR_THRESHOLD) {
        counter++;
    } else {
        counter = 0;
        isDrowsy = false;
        alertPlaying = false;
        
        // Reset UI
        warningBox.classList.add('hidden');
        alertOverlay.classList.remove('alert-active');
        systemStatus.innerText = "ACTIVE - EYES OPEN";
        systemStatus.style.color = "var(--primary-color)";
    }

    if (counter >= EAR_CONSEC_FRAMES) {
        isDrowsy = true;
        systemStatus.innerText = "WARNING - DROWSY";
        systemStatus.style.color = "var(--danger-color)";
        
        // Trigger Alerts
        warningBox.classList.remove('hidden');
        alertOverlay.classList.add('alert-active');

        if (!alertPlaying) {
            synth.speak(warningUtterance);
            alertPlaying = true;
            // Throttle voice slightly to prevent overlap spam
            warningUtterance.onend = () => {
                if (isDrowsy) {
                   // Optional: Simple delay before re-speaking could be added here
                   setTimeout(() => { alertPlaying = false; }, 1000); 
                } else {
                    alertPlaying = false;
                }
            }
        }
    }
}

const faceMesh = new FaceMesh({locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
}});

faceMesh.setOptions({
    maxNumFaces: 1,
    refineLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});

faceMesh.onResults(onResults);

const camera = new Camera(videoElement, {
    onFrame: async () => {
        await faceMesh.send({image: videoElement});
    },
    width: 1280,
    height: 720
});

startBtn.addEventListener('click', () => {
    startScreen.style.display = 'none';
    systemStatus.innerText = "STARTING CAMERA...";
    camera.start();
    
    // Initialize Audio Context if needed (browser policy)
    synth.cancel(); // Clear queue
});
