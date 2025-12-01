from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import pyaudio
import threading
import uvicorn

# Create a FastAPI app instance
app = FastAPI()

# --- HTML for the client page ---
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Real-Time Audio Stream UwU</title>
    </head>
    <body>
        <h1>Real-Time Audio Stream</h1>
        <p>Status: <span id="status">Idle</span></p>
        <button id="connectButton">Connect and Listen</button>
        <button id="disconnectButton" disabled>Disconnect</button>
        <script>
            let websocket;
            let audioContext;
            let audioQueue = [];
            let isPlaying = false;
            let nextStartTime = 0;
            const sampleRate = 44100;

            const statusElem = document.getElementById("status");
            const connectButton = document.getElementById("connectButton");
            const disconnectButton = document.getElementById("disconnectButton");

            connectButton.onclick = function(event) {
                // Initialize AudioContext on user gesture
                if (!audioContext) {
                    audioContext = new (window.AudioContext || window.webkitAudioContext)({sampleRate: sampleRate});
                }
                
                websocket = new WebSocket("ws://192.168.122.67:8000/ws/audio");
                statusElem.textContent = "Connecting...";

                websocket.onopen = function(event) {
                    statusElem.textContent = "Connected. Receiving audio...";
                    connectButton.disabled = true;
                    disconnectButton.disabled = false;
                };

                websocket.onclose = function(event) {
                    statusElem.textContent = "Disconnected.";
                    connectButton.disabled = false;
                    disconnectButton.disabled = true;
                    isPlaying = false;
                    audioQueue = [];
                };
                
                websocket.onerror = function(event) {
                    statusElem.textContent = "Error connecting.";
                    console.error("WebSocket error:", event);
                };

                websocket.onmessage = function(event) {
                    // event.data is a Blob containing the raw audio data
                    const reader = new FileReader();
                    reader.onload = function() {
                        const arrayBuffer = reader.result;
                        // The server sends Int16, so 2 bytes per sample
                        const int16Array = new Int16Array(arrayBuffer);
                        // Convert to Float32Array for Web Audio API (-1.0 to 1.0)
                        const float32Array = new Float32Array(int16Array.length);
                        for (let i = 0; i < int16Array.length; i++) {
                            float32Array[i] = int16Array[i] / 32768.0;
                        }
                        
                        const audioBuffer = audioContext.createBuffer(1, float32Array.length, sampleRate);
                        audioBuffer.copyToChannel(float32Array, 0);
                        
                        audioQueue.push(audioBuffer);
                        if (!isPlaying) {
                            isPlaying = true;
                            schedulePlayback();
                        }
                    };
                    reader.readAsArrayBuffer(event.data);
                };
            };
            
            disconnectButton.onclick = function(event) {
                if (websocket) {
                    websocket.close();
                }
            };

            function schedulePlayback() {
                if (audioQueue.length === 0) {
                    isPlaying = false;
                    return;
                }

                const buffer = audioQueue.shift();
                const source = audioContext.createBufferSource();
                source.buffer = buffer;
                source.connect(audioContext.destination);

                const currentTime = audioContext.currentTime;
                if (nextStartTime < currentTime) {
                    nextStartTime = currentTime;
                }
                
                source.start(nextStartTime);
                nextStartTime += buffer.duration;
                
                source.onended = schedulePlayback;
            }
        </script>
    </body>
</html>
"""

# --- PyAudio Parameters ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# --- Global variables for managing the audio stream ---
p_audio = None
stream = None
stream_thread = None
# Use a thread-safe event to signal the streaming loop
is_streaming = threading.Event()

def audio_streaming_task():
    """
    The main audio processing loop.
    This function runs in a separate thread.
    """
    global p_audio, stream
    print("* Stream thread started.")
    
    try:
        p_audio = pyaudio.PyAudio()
        stream = p_audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            output=True,
                            frames_per_buffer=CHUNK)

        while is_streaming.is_set():
            data = stream.read(CHUNK, exception_on_overflow=False)
            stream.write(data)

    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        if p_audio:
            p_audio.terminate()
        print("* Stream thread finished and cleaned up.")

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    p = None
    stream = None
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        
        while True:
            data = stream.read(CHUNK)
            await websocket.send_bytes(data)

    except WebSocketDisconnect:
        print("Client disconnected from WebSocket.")
    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        if p:
            p.terminate()
        print("WebSocket audio resources cleaned up.")

@app.get("/start")
async def start_streaming():
    """Starts the audio stream."""
    global stream_thread
    if is_streaming.is_set():
        raise HTTPException(status_code=400, detail="Audio stream is already running.")
    
    print("* Starting audio stream...")
    is_streaming.set()  # Set the event to signal the loop to run
    stream_thread = threading.Thread(target=audio_streaming_task)
    stream_thread.start()
    return {"status": "Audio stream started"}


@app.get("/stop")
async def stop_streaming():
    """Stops the audio stream."""
    global stream_thread
    if not is_streaming.is_set():
        raise HTTPException(status_code=400, detail="Audio stream is not running.")
        
    print("* Stopping audio stream...")
    is_streaming.clear()  # Clear the event to signal the loop to stop
    if stream_thread:
        stream_thread.join()  # Wait for the thread to complete
        stream_thread = None
    return {"status": "Audio stream stopped"}

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)

