from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import uvicorn
import threading
import webbrowser
import pyttsx3


# ============================================================
# NOVA V1 CONFIGURATION
# ============================================================

APP_NAME = "NOVA"
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "gemma3:1b"

app = FastAPI(title="NOVA V1")


# ============================================================
# CHAT REQUEST
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# NOVA VOICE + FRIENDLY PERSONALITY
# ============================================================

VOICE_NAME = "Microsoft Zira Desktop"
VOICE_RATE = 175
VOICE_VOLUME = 1.0
VOICE_ENABLED = True

tts_lock = threading.Lock()
conversation_history = []


# ============================================================
# TEXT TO SPEECH
# ============================================================

def speak_text(text: str):
    """Speak NOVA's response using Microsoft Zira."""

    if not VOICE_ENABLED or not text:
        return

    def worker():
        with tts_lock:
            engine = None

            try:
                engine = pyttsx3.init("sapi5")

                selected_voice = None

                for voice in engine.getProperty("voices"):
                    voice_name = getattr(voice, "name", "") or ""
                    voice_id = getattr(voice, "id", "") or ""

                    if (
                        VOICE_NAME.lower() in voice_name.lower()
                        or "zira" in voice_name.lower()
                        or "zira" in voice_id.lower()
                    ):
                        selected_voice = voice_id
                        break

                if selected_voice:
                    engine.setProperty("voice", selected_voice)

                engine.setProperty("rate", VOICE_RATE)
                engine.setProperty("volume", VOICE_VOLUME)

                engine.say(text)
                engine.runAndWait()

            except Exception as e:
                print("NOVA Voice Error:", e)

            finally:
                try:
                    if engine:
                        engine.stop()
                except Exception:
                    pass

    threading.Thread(target=worker, daemon=True).start()


# ============================================================
# OLLAMA AI
# ============================================================

def ask_ollama(message: str) -> str:

    system_prompt = """
You are NOVA, a friendly personal AI assistant.

Your personality:
- Friendly
- Natural
- Intelligent
- Helpful
- Calm
- Slightly humorous when appropriate
- Speak like a helpful close friend
- Keep answers clear and easy to understand
- Call the user "Boss" naturally, but do not overuse it
- Do not repeatedly say "As an AI"
- Do not pretend that you performed an action when you did not
- For simple questions, give simple answers
- For difficult questions, explain step by step
- For technical questions, give practical solutions

You are running locally through Ollama.
"""

    # Build conversation for Ollama
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # Add previous conversation
    messages.extend(conversation_history[-20:])

    # Add current user message
    messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        answer = data["message"]["content"].strip()

        # Save conversation only after successful response
        conversation_history.append(
            {
                "role": "user",
                "content": message
            }
        )

        conversation_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        # Speak NOVA's answer
        speak_text(answer)

        return answer

    except requests.exceptions.ConnectionError:
        return (
            "Boss, I cannot connect to Ollama right now. "
            "Please make sure Ollama is running."
        )

    except requests.exceptions.Timeout:
        return (
            "Boss, Ollama took too long to respond. "
            "Please try again."
        )

    except Exception as e:
        print("Ollama Error:", e)

        return (
            "Boss, something went wrong while I was processing "
            "that request."
        )


# ============================================================
# CHAT API
# ============================================================

@app.post("/api/chat")
def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:
        return {
            "success": False,
            "answer": "Boss, please type something for me."
        }

    answer = ask_ollama(message)

    return {
        "success": True,
        "answer": answer
    }


# ============================================================
# OLLAMA STATUS
# ============================================================

@app.get("/api/status")
def status():

    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )

        if response.status_code == 200:

            models = response.json().get("models", [])

            model_names = [
                model.get("name", "")
                for model in models
            ]

            model_available = any(
                OLLAMA_MODEL in name
                for name in model_names
            )

            return {
                "online": True,
                "model": OLLAMA_MODEL,
                "model_available": model_available
            }

    except Exception:
        pass

    return {
        "online": False,
        "model": OLLAMA_MODEL,
        "model_available": False
    }


# ============================================================
# FUTURISTIC NOVA INTERFACE
# ============================================================

HTML_PAGE = """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>NOVA V1</title>

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    min-height: 100vh;

    background:
        radial-gradient(
            circle at center,
            #071d35 0%,
            #020914 45%,
            #00040a 100%
        );

    color: #55dfff;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    overflow-x: hidden;
}


/* =========================================================
   TOP BAR
   ========================================================= */

.topbar {

    height: 65px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 0 30px;

    border-bottom:
        1px solid rgba(0, 210, 255, 0.25);

    background:
        rgba(0, 10, 25, 0.7);

    box-shadow:
        0 0 20px rgba(0, 180, 255, 0.12);

}

.logo {

    font-size: 26px;

    font-weight: bold;

    letter-spacing: 6px;

    text-shadow:
        0 0 10px #00d9ff,
        0 0 25px #00d9ff;
}

.subtitle {

    font-size: 11px;

    letter-spacing: 3px;

    color: #619db6;

}

.status {

    display: flex;

    align-items: center;

    gap: 9px;

    font-size: 12px;

    letter-spacing: 2px;

}

.status-dot {

    width: 9px;

    height: 9px;

    border-radius: 50%;

    background: #ff3030;

    box-shadow: 0 0 10px #ff3030;

}

.status-dot.online {

    background: #00ffb3;

    box-shadow: 0 0 12px #00ffb3;

}


/* =========================================================
   MAIN HUD
   ========================================================= */

.main {

    min-height:
        calc(100vh - 65px);

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    padding: 30px;

}


/* =========================================================
   HUD CORE
   ========================================================= */

.hud {

    width: min(560px, 90vw);

    height: min(560px, 90vw);

    position: relative;

    display: flex;

    align-items: center;

    justify-content: center;

}


/* Outer ring */

.ring {

    position: absolute;

    border-radius: 50%;

    border: 1px solid rgba(0, 210, 255, 0.35);

    box-shadow:
        0 0 15px rgba(0, 190, 255, 0.08);

}

.ring1 {

    width: 100%;

    height: 100%;

    animation:
        rotate 25s linear infinite;

}

.ring2 {

    width: 88%;

    height: 88%;

    border-style: dashed;

    animation:
        rotateReverse 18s linear infinite;

}

.ring3 {

    width: 72%;

    height: 72%;

    border-color:
        rgba(0, 225, 255, 0.55);

    animation:
        rotate 12s linear infinite;

}

.ring4 {

    width: 58%;

    height: 58%;

    border-style: dashed;

    animation:
        rotateReverse 9s linear infinite;

}


/* Segmented ring */

.segment {

    position: absolute;

    width: 80%;

    height: 80%;

    border-radius: 50%;

    border-top:
        4px solid #00dfff;

    border-right:
        4px solid transparent;

    border-bottom:
        4px solid #0088aa;

    border-left:
        4px solid transparent;

    animation:
        rotate 7s linear infinite;

}


/* Center */

.core {

    width: 190px;

    height: 190px;

    border-radius: 50%;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    background:
        radial-gradient(
            circle,
            rgba(0, 220, 255, 0.25),
            rgba(0, 30, 55, 0.95) 65%,
            #00101d 100%
        );

    border:
        2px solid rgba(0, 220, 255, 0.8);

    box-shadow:

        0 0 25px rgba(0, 210, 255, 0.5),

        inset 0 0 35px rgba(0, 180, 255, 0.25);

    z-index: 10;

    animation:
        pulse 3s ease-in-out infinite;

}

.core-title {

    font-size: 31px;

    font-weight: bold;

    letter-spacing: 8px;

    margin-left: 8px;

    text-shadow:
        0 0 10px #00eaff,
        0 0 30px #00aaff;

}

.core-sub {

    font-size: 10px;

    letter-spacing: 4px;

    margin-top: 9px;

    color: #7bc9df;

}


/* =========================================================
   DECORATIVE MARKINGS
   ========================================================= */

.tech {

    position: absolute;

    font-size: 9px;

    letter-spacing: 3px;

    color: rgba(80, 200, 230, 0.65);

}

.tech1 {

    top: 8%;

    left: 20%;

}

.tech2 {

    bottom: 12%;

    right: 17%;

}

.tech3 {

    top: 45%;

    left: 1%;

}

.tech4 {

    top: 47%;

    right: 1%;

}


/* =========================================================
   CHAT
   ========================================================= */

.chat-panel {

    width: min(850px, 94vw);

    margin-top: 20px;

    padding: 15px;

    border:
        1px solid rgba(0, 200, 255, 0.3);

    background:
        rgba(0, 12, 25, 0.75);

    box-shadow:
        0 0 25px rgba(0, 170, 255, 0.08);

    backdrop-filter:
        blur(10px);

}

.chat {

    height: 130px;

    overflow-y: auto;

    padding: 10px;

    font-size: 14px;

    line-height: 1.6;

}

.nova-message {

    color: #70e8ff;

}

.user-message {

    color: #ffffff;

    margin-top: 8px;

}

.input-row {

    display: flex;

    gap: 10px;

    margin-top: 10px;

}

input {

    flex: 1;

    padding: 13px;

    background:
        rgba(0, 20, 35, 0.9);

    border:
        1px solid rgba(0, 200, 255, 0.4);

    color: white;

    outline: none;

    font-size: 14px;

}

input:focus {

    border-color:
        #00dfff;

    box-shadow:
        0 0 10px rgba(0, 220, 255, 0.25);

}

button {

    padding: 0 25px;

    border: 1px solid #00dfff;

    background:
        rgba(0, 180, 230, 0.15);

    color: #72eaff;

    cursor: pointer;

    font-weight: bold;

    letter-spacing: 2px;

}

button:hover {

    background:
        rgba(0, 210, 255, 0.3);

    box-shadow:
        0 0 15px rgba(0, 220, 255, 0.4);

}


/* =========================================================
   ANIMATIONS
   ========================================================= */

@keyframes rotate {

    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }

}

@keyframes rotateReverse {

    from {
        transform: rotate(360deg);
    }

    to {
        transform: rotate(0deg);
    }

}

@keyframes pulse {

    0%,
    100% {

        transform: scale(1);

        box-shadow:
            0 0 25px rgba(0, 210, 255, 0.5),
            inset 0 0 35px rgba(0, 180, 255, 0.25);

    }

    50% {

        transform: scale(1.04);

        box-shadow:
            0 0 45px rgba(0, 230, 255, 0.75),
            inset 0 0 45px rgba(0, 200, 255, 0.35);

    }

}


/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 600px) {

    .topbar {

        padding: 0 15px;

    }

    .subtitle {

        display: none;

    }

    .logo {

        font-size: 21px;

    }

    .hud {

        width: 90vw;

        height: 90vw;

    }

    .core {

        width: 140px;

        height: 140px;

    }

    .core-title {

        font-size: 23px;

    }

    .chat-panel {

        margin-top: 10px;

    }

}

</style>

</head>


<body>


<div class="topbar">

    <div>

        <div class="logo">
            NOVA
        </div>

        <div class="subtitle">
            PERSONAL AI CORE
        </div>

    </div>


    <div class="status">

        <div
            id="statusDot"
            class="status-dot">
        </div>

        <span id="statusText">
            OFFLINE
        </span>

    </div>

</div>


<div class="main">


    <div class="hud">

        <div class="ring ring1"></div>

        <div class="ring ring2"></div>

        <div class="ring ring3"></div>

        <div class="ring ring4"></div>

        <div class="segment"></div>


        <div class="tech tech1">
            0101 1100 1010
        </div>

        <div class="tech tech2">
            SYSTEM // ONLINE
        </div>

        <div class="tech tech3">
            ◇ ◇ ◇ ◇
        </div>

        <div class="tech tech4">
            01 10 01
        </div>


        <div class="core">

            <div class="core-title">
                NOVA
            </div>

            <div class="core-sub">
                AI CORE
            </div>

        </div>

    </div>


    <div class="chat-panel">

        <div
            id="chat"
            class="chat">

            <div class="nova-message">
                <b>NOVA:</b>
                Hello Boss. I'm ready. Talk to me.
            </div>

        </div>


        <div class="input-row">

            <input
                id="message"
                type="text"
                placeholder="Talk to NOVA..."
                autocomplete="off"
            >

            <button
                onclick="sendMessage()">
                SEND
            </button>

        </div>

    </div>

</div>


<script>


const input =
    document.getElementById("message");

const chat =
    document.getElementById("chat");

const statusDot =
    document.getElementById("statusDot");

const statusText =
    document.getElementById("statusText");


function addMessage(sender, text, className) {

    const div =
        document.createElement("div");

    div.className = className;

    div.innerHTML =
        "<b>" +
        sender +
        ":</b> " +
        escapeHtml(text);

    chat.appendChild(div);

    chat.scrollTop =
        chat.scrollHeight;

}


function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;

}


async function sendMessage() {

    const message =
        input.value.trim();

    if (!message) {
        return;
    }


    addMessage(
        "YOU",
        message,
        "user-message"
    );

    input.value = "";


    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message: message
                        })
                }
            );


        const data =
            await response.json();


        if (data.success) {

            addMessage(
                "NOVA",
                data.answer,
                "nova-message"
            );

        } else {

            addMessage(
                "NOVA",
                "Sorry Boss, I couldn't process that.",
                "nova-message"
            );

        }


    } catch (error) {

        addMessage(
            "NOVA",
            "Boss, I can't connect to my local server.",
            "nova-message"
        );

    }

}


input.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            sendMessage();

        }

    }
);


async function checkStatus() {

    try {

        const response =
            await fetch("/api/status");

        const data =
            await response.json();


        if (data.online) {

            statusDot.classList.add("online");

            statusText.textContent =
                "ONLINE";

        } else {

            statusDot.classList.remove("online");

            statusText.textContent =
                "OFFLINE";

        }

    } catch (error) {

        statusDot.classList.remove("online");

        statusText.textContent =
            "OFFLINE";

    }

}


checkStatus();

setInterval(
    checkStatus,
    5000
);


</script>


</body>

</html>
"""


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return HTML_PAGE


# ============================================================
# OPEN BROWSER
# ============================================================

def open_browser():

    webbrowser.open(
        "http://127.0.0.1:8000"
    )


# ============================================================
# START NOVA
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 55)
    print("                    NOVA V1")
    print("=" * 55)
    print(" FUTURISTIC LOCAL AI INTERFACE")
    print(f" Model : {OLLAMA_MODEL}")
    print(" Ollama: Local")
    print(" Voice : Microsoft Zira Desktop")
    print(" Web   : http://127.0.0.1:8000")
    print("=" * 55)
    print()
    print("NOVA: Starting interface...")
    print()

    threading.Timer(
        1.5,
        open_browser
    ).start()

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )