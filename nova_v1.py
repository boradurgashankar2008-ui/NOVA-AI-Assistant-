from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import uvicorn
import threading
import webbrowser

# ============================================================
# NOVA V1
# Futuristic AI Interface
# Ollama + Gemma 3:1B
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
# NOVA -> OLLAMA
# ============================================================

def ask_ollama(message: str):

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are NOVA, a personal AI assistant. "
                    "Talk naturally with the user. "
                    "Answer questions clearly and accurately. "
                    "Solve problems step by step when useful. "
                    "Keep answers practical and understandable. "
                    "Do not claim to have performed actions you did not perform."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ],
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

        return data["message"]["content"].strip()

    except requests.exceptions.ConnectionError:

        return (
            "I cannot connect to Ollama. "
            "Please make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return "Ollama took too long to respond."

    except Exception as error:

        return f"NOVA error: {error}"


# ============================================================
# CHAT API
# ============================================================

@app.post("/api/chat")
def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:

        return {
            "success": False,
            "answer": "Please enter a message."
        }

    answer = ask_ollama(message)

    return {
        "success": True,
        "answer": answer
    }


# ============================================================
# STATUS API
# ============================================================

@app.get("/api/status")
def status():

    try:

        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )

        if response.ok:

            return {
                "connected": True,
                "model": OLLAMA_MODEL
            }

    except Exception:
        pass

    return {
        "connected": False,
        "model": OLLAMA_MODEL
    }


# ============================================================
# NOVA INTERFACE
# ============================================================

HTML_PAGE = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>NOVA V1</title>


<style>

/* =========================================================
   BASIC
========================================================= */

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
            #020913 42%,
            #01040a 100%
        );

    color: #e8f9ff;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    overflow-x: hidden;
}


/* =========================================================
   MAIN
========================================================= */

.nova-app {

    width: 100%;

    min-height: 100vh;

    display: flex;

    flex-direction: column;

    align-items: center;

    padding: 25px 15px 40px;
}


/* =========================================================
   TOP BAR
========================================================= */

.top-bar {

    width: min(1100px, 100%);

    display: flex;

    justify-content: space-between;

    align-items: center;

    padding: 12px 18px;

    border: 1px solid rgba(70, 200, 255, .25);

    background:
        rgba(3, 17, 31, .72);

    backdrop-filter: blur(12px);

    border-radius: 14px;

    box-shadow:
        0 0 25px rgba(0, 180, 255, .08);
}


.logo {

    font-size: 25px;

    font-weight: 700;

    letter-spacing: 7px;

    color: #e9fbff;

    text-shadow:
        0 0 10px #40dfff,
        0 0 30px rgba(0, 190, 255, .7);
}


.version {

    font-size: 11px;

    letter-spacing: 3px;

    color: #6f9aaa;
}


/* =========================================================
   STATUS
========================================================= */

.status {

    display: flex;

    align-items: center;

    gap: 8px;

    font-size: 11px;

    letter-spacing: 2px;

    color: #8ab5c5;
}


.status-dot {

    width: 9px;

    height: 9px;

    border-radius: 50%;

    background: #555;

}


.status-dot.online {

    background: #35eaff;

    box-shadow:
        0 0 8px #35eaff,
        0 0 18px #35eaff;
}


/* =========================================================
   HUD AREA
========================================================= */

.hud {

    position: relative;

    width: min(600px, 92vw);

    aspect-ratio: 1;

    margin-top: 25px;

    display: flex;

    align-items: center;

    justify-content: center;
}


/* =========================================================
   OUTER GLOW
========================================================= */

.hud::before {

    content: "";

    position: absolute;

    inset: 2%;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(0, 180, 255, .12),
            transparent 65%
        );

    filter: blur(12px);
}


/* =========================================================
   RINGS
========================================================= */

.ring {

    position: absolute;

    border-radius: 50%;

    pointer-events: none;
}


.ring-1 {

    inset: 0;

    border:
        2px solid rgba(80, 220, 255, .7);

    box-shadow:
        0 0 15px rgba(0, 210, 255, .35);

    animation:
        rotate-clockwise 30s linear infinite;
}


.ring-2 {

    inset: 5%;

    border:
        1px dashed rgba(70, 205, 255, .6);

    animation:
        rotate-counter 22s linear infinite;
}


.ring-3 {

    inset: 11%;

    border:
        3px solid rgba(60, 210, 255, .5);

    border-left-color: transparent;

    border-right-color: transparent;

    animation:
        rotate-clockwise 17s linear infinite;
}


.ring-4 {

    inset: 17%;

    border:
        1px solid rgba(90, 230, 255, .55);

    border-top-color: transparent;

    border-bottom-color: transparent;

    animation:
        rotate-counter 13s linear infinite;
}


/* =========================================================
   SEGMENTED RING
========================================================= */

.segment-ring {

    position: absolute;

    inset: 24%;

    border-radius: 50%;

    border:
        9px dotted rgba(70, 210, 255, .55);

    animation:
        rotate-clockwise 12s linear infinite;
}


/* =========================================================
   INNER RINGS
========================================================= */

.inner-ring {

    position: absolute;

    border-radius: 50%;

    border:
        1px solid rgba(100, 225, 255, .45);
}


.inner-1 {

    inset: 29%;
}


.inner-2 {

    inset: 34%;

    border-style: dashed;

    animation:
        rotate-counter 9s linear infinite;
}


/* =========================================================
   TECHNICAL TICKS
========================================================= */

.ticks {

    position: absolute;

    inset: 8%;

    border-radius: 50%;

    background:
        repeating-conic-gradient(
            from 0deg,
            rgba(100, 225, 255, .7) 0deg 1deg,
            transparent 1deg 7deg
        );

    -webkit-mask:
        radial-gradient(
            transparent 67%,
            #000 68%,
            #000 70%,
            transparent 71%
        );

    mask:
        radial-gradient(
            transparent 67%,
            #000 68%,
            #000 70%,
            transparent 71%
        );

    animation:
        rotate-counter 40s linear infinite;
}


/* =========================================================
   BINARY MARKINGS
========================================================= */

.binary {

    position: absolute;

    width: 100%;

    text-align: center;

    color:
        rgba(120, 225, 255, .45);

    font-size: 9px;

    letter-spacing: 5px;

    white-space: nowrap;

    pointer-events: none;
}


.binary-top {

    top: 14%;
}


.binary-bottom {

    bottom: 14%;
}


/* =========================================================
   SIDE MARKINGS
========================================================= */

.side-label {

    position: absolute;

    color: rgba(120, 225, 255, .55);

    font-size: 8px;

    letter-spacing: 2px;

    writing-mode: vertical-rl;

}


.side-left {

    left: 9%;

    top: 37%;
}


.side-right {

    right: 9%;

    top: 37%;

    transform:
        rotate(180deg);
}


/* =========================================================
   CENTER CORE
========================================================= */

.core {

    position: absolute;

    width: 37%;

    aspect-ratio: 1;

    border-radius: 50%;

    display: flex;

    align-items: center;

    justify-content: center;

    text-align: center;

    background:
        radial-gradient(
            circle,
            #092d4b 0%,
            #041525 55%,
            #020a12 100%
        );

    border:
        3px solid rgba(80, 225, 255, .9);

    box-shadow:

        0 0 10px #31dcff,

        0 0 35px rgba(0, 200, 255, .65),

        inset 0 0 35px rgba(0, 190, 255, .35);

    animation:
        core-pulse 3s ease-in-out infinite;
}


.core::before {

    content: "";

    position: absolute;

    inset: 8%;

    border-radius: 50%;

    border:
        1px solid rgba(130, 235, 255, .7);
}


.core::after {

    content: "";

    position: absolute;

    inset: -12%;

    border-radius: 50%;

    border:
        1px solid rgba(60, 210, 255, .3);

    border-left-color: transparent;

    border-right-color: transparent;

    animation:
        rotate-clockwise 8s linear infinite;
}


.core-content {

    position: relative;

    z-index: 3;
}


.nova-name {

    font-size:
        clamp(30px, 7vw, 55px);

    font-weight: 600;

    letter-spacing: 7px;

    color: white;

    text-shadow:

        0 0 7px white,

        0 0 20px #35dcff,

        0 0 45px #009dff;
}


.core-sub {

    margin-top: 9px;

    font-size: 9px;

    letter-spacing: 4px;

    color: #75bfd1;
}


/* =========================================================
   DECORATIVE DATA POINTS
========================================================= */

.data-point {

    position: absolute;

    width: 6px;

    height: 6px;

    border-radius: 50%;

    background: #7aeaff;

    box-shadow:
        0 0 10px #7aeaff;
}


.p1 { top: 21%; left: 31%; }
.p2 { top: 29%; right: 25%; }
.p3 { bottom: 25%; left: 25%; }
.p4 { bottom: 18%; right: 32%; }


/* =========================================================
   CHAT AREA
========================================================= */

.chat-panel {

    width: min(900px, 100%);

    margin-top: 15px;

    border:
        1px solid rgba(70, 200, 255, .22);

    background:
        rgba(3, 15, 27, .8);

    border-radius: 18px;

    overflow: hidden;

    box-shadow:
        0 0 35px rgba(0, 150, 255, .08);
}


.chat-header {

    padding: 15px 18px;

    border-bottom:
        1px solid rgba(70, 200, 255, .15);

    display: flex;

    justify-content: space-between;

    align-items: center;
}


.chat-title {

    font-size: 12px;

    letter-spacing: 3px;

    color: #80d9eb;
}


.chat-status {

    font-size: 10px;

    color: #608595;
}


.messages {

    height: 300px;

    overflow-y: auto;

    padding: 18px;

    display: flex;

    flex-direction: column;

    gap: 12px;
}


.message {

    max-width: 82%;

    padding: 12px 15px;

    border-radius: 12px;

    line-height: 1.5;

    font-size: 14px;

    white-space: pre-wrap;
}


.message.nova {

    align-self: flex-start;

    background:
        rgba(20, 100, 140, .16);

    border:
        1px solid rgba(70, 210, 255, .18);

    color: #d8f7ff;
}


.message.user {

    align-self: flex-end;

    background:
        rgba(70, 160, 200, .12);

    border:
        1px solid rgba(90, 200, 255, .2);

    color: white;
}


/* =========================================================
   INPUT
========================================================= */

.input-area {

    display: flex;

    gap: 10px;

    padding: 15px;

    border-top:
        1px solid rgba(70, 200, 255, .15);
}


.input-area input {

    flex: 1;

    min-width: 0;

    padding: 14px 16px;

    border-radius: 12px;

    border:
        1px solid rgba(80, 200, 255, .25);

    background:
        rgba(0, 8, 15, .8);

    color: white;

    outline: none;

    font-size: 15px;
}


.input-area input:focus {

    border-color:
        rgba(80, 225, 255, .7);

    box-shadow:
        0 0 15px rgba(0, 190, 255, .15);
}


.send-button {

    padding:
        0 24px;

    border: none;

    border-radius: 12px;

    background:
        #0c7fa6;

    color: white;

    font-weight: bold;

    letter-spacing: 1px;

    cursor: pointer;

    box-shadow:
        0 0 18px rgba(0, 180, 255, .25);
}


.send-button:hover {

    background:
        #0e9dcc;
}


/* =========================================================
   ANIMATIONS
========================================================= */

@keyframes rotate-clockwise {

    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}


@keyframes rotate-counter {

    from {
        transform: rotate(360deg);
    }

    to {
        transform: rotate(0deg);
    }
}


@keyframes core-pulse {

    0%, 100% {
        transform: scale(1);

        box-shadow:
            0 0 10px #31dcff,
            0 0 35px rgba(0, 200, 255, .65),
            inset 0 0 35px rgba(0, 190, 255, .35);
    }

    50% {
        transform: scale(1.025);

        box-shadow:
            0 0 15px #31dcff,
            0 0 55px rgba(0, 200, 255, .85),
            inset 0 0 45px rgba(0, 190, 255, .45);
    }
}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 600px) {

    .nova-app {
        padding-top: 12px;
    }

    .top-bar {
        padding: 10px 12px;
    }

    .logo {
        font-size: 20px;
        letter-spacing: 5px;
    }

    .version {
        display: none;
    }

    .hud {
        width: 96vw;
        margin-top: 12px;
    }

    .chat-panel {
        margin-top: 5px;
    }

    .messages {
        height: 260px;
    }

    .input-area {
        padding: 10px;
    }

    .send-button {
        padding: 0 16px;
    }
}

</style>

</head>


<body>

<div class="nova-app">


    <!-- TOP BAR -->

    <div class="top-bar">

        <div>

            <div class="logo">
                NOVA
            </div>

            <div class="version">
                PERSONAL AI CORE
            </div>

        </div>


        <div class="status">

            <span
                id="statusDot"
                class="status-dot">
            </span>

            <span id="statusText">
                CONNECTING
            </span>

        </div>

    </div>


    <!-- HUD -->

    <div class="hud">

        <div class="ring ring-1"></div>

        <div class="ring ring-2"></div>

        <div class="ring ring-3"></div>

        <div class="ring ring-4"></div>

        <div class="ticks"></div>

        <div class="segment-ring"></div>

        <div class="inner-ring inner-1"></div>

        <div class="inner-ring inner-2"></div>


        <div class="binary binary-top">
            01001 01110 01011 01001 00110 01010
        </div>

        <div class="binary binary-bottom">
            10110 00101 11001 01001 10101 00110
        </div>


        <div class="side-label side-left">
            NOVA // SYSTEM // CORE // ONLINE
        </div>

        <div class="side-label side-right">
            AI // LOCAL // OLLAMA // GEMMA
        </div>


        <div class="data-point p1"></div>
        <div class="data-point p2"></div>
        <div class="data-point p3"></div>
        <div class="data-point p4"></div>


        <!-- CORE -->

        <div class="core">

            <div class="core-content">

                <div class="nova-name">
                    NOVA
                </div>

                <div class="core-sub">
                    AI CORE
                </div>

            </div>

        </div>

    </div>


    <!-- CHAT -->

    <div class="chat-panel">

        <div class="chat-header">

            <div class="chat-title">
                NOVA // CONVERSATION
            </div>

            <div
                class="chat-status"
                id="modelStatus">
                GEMMA 3:1B
            </div>

        </div>


        <div
            class="messages"
            id="messages">

            <div class="message nova">

                Hello Boss.
                I am NOVA V1.

                I am ready to talk and solve your questions.

            </div>

        </div>


        <div class="input-area">

            <input
                id="messageInput"
                type="text"
                placeholder="Talk to NOVA..."
                autocomplete="off">

            <button
                id="sendButton"
                class="send-button"
                type="button">

                SEND

            </button>

        </div>

    </div>

</div>


<script>


const input =
    document.getElementById(
        "messageInput"
    );


const sendButton =
    document.getElementById(
        "sendButton"
    );


const messages =
    document.getElementById(
        "messages"
    );


const statusDot =
    document.getElementById(
        "statusDot"
    );


const statusText =
    document.getElementById(
        "statusText"
    );


const modelStatus =
    document.getElementById(
        "modelStatus"
    );


function addMessage(text, type) {

    const message =
        document.createElement("div");

    message.className =
        "message " + type;

    message.textContent =
        text;

    messages.appendChild(message);

    messages.scrollTop =
        messages.scrollHeight;
}


async function checkStatus() {

    try {

        const response =
            await fetch("/api/status");

        const data =
            await response.json();


        if (data.connected) {

            statusDot.classList.add("online");

            statusText.textContent =
                "OLLAMA ONLINE";

            modelStatus.textContent =
                data.model.toUpperCase();

        } else {

            statusDot.classList.remove("online");

            statusText.textContent =
                "OLLAMA OFFLINE";

        }

    } catch {

        statusDot.classList.remove("online");

        statusText.textContent =
            "SERVER ERROR";
    }
}


async function sendMessage() {

    const text =
        input.value.trim();


    if (!text) {

        return;
    }


    addMessage(
        text,
        "user"
    );


    input.value = "";

    sendButton.disabled = true;

    sendButton.textContent =
        "...";


    addMessage(
        "Thinking...",
        "nova"
    );


    const thinkingMessage =
        messages.lastElementChild;


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

                    body: JSON.stringify({
                        message: text
                    })
                }
            );


        const data =
            await response.json();


        thinkingMessage.remove();


        addMessage(
            data.answer,
            "nova"
        );


    } catch (error) {

        thinkingMessage.remove();


        addMessage(
            "I could not connect to the NOVA server.",
            "nova"
        );

    }


    sendButton.disabled = false;

    sendButton.textContent =
        "SEND";


    input.focus();

}


sendButton.addEventListener(
    "click",
    sendMessage
);


input.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter"
        ) {

            sendMessage();

        }

    }
);


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
    print("=" * 60)
    print("                    NOVA V1")
    print("=" * 60)
    print("          FUTURISTIC AI INTERFACE")
    print("=" * 60)
    print()
    print("Model :", OLLAMA_MODEL)
    print("Server: http://127.0.0.1:8000")
    print()
    print("Starting NOVA...")
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