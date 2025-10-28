from flask import Flask, render_template, request, Response, jsonify
import google.generativeai as genai
from gtts import gTTS
from playsound import playsound
import threading, queue, json, os, re, uuid, time

# ======================
# CONFIGURATION
# ======================
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)

MEMORY_FILE = "memory.json"
MAX_MEMORY_SIZE = 200

# ======================
# MEMORY FUNCTIONS
# ======================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)

def remember(memory, message, role):
    memory.append({"role": role, "content": message})
    save_memory(memory)

def summarize_memory(memory):
    if len(memory) <= MAX_MEMORY_SIZE:
        return memory
    old_context = "\n".join([f"{m['role']}: {m['content']}" for m in memory[:-MAX_MEMORY_SIZE//2]])
    summary_prompt = f"Summarize the following conversation briefly:\n\n{old_context}"
    try:
        summary = model.generate_content(summary_prompt).text.strip()
        memory = [{"role": "system", "content": f"Summary of earlier chats: {summary}"}] + memory[-MAX_MEMORY_SIZE//2:]
        save_memory(memory)
    except Exception as e:
        print(f"Error summarizing memory: {e}")
    return memory

# ======================
# TTS QUEUE SYSTEM
# ======================
tts_queue = queue.Queue()

def clean_text_for_tts(text):
    # Remove unwanted characters or symbols for better pronunciation
    return re.sub(r"[^a-zA-Z0-9\s.,!?']", "", text)

def tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:
            break
        clean_text = clean_text_for_tts(text)
        if clean_text.strip():
            tts_file = f"static/{uuid.uuid4()}.mp3"
            tts = gTTS(text=clean_text, lang='en')
            tts.save(tts_file)
            playsound(tts_file)
            os.remove(tts_file)
        tts_queue.task_done()

# Start background TTS thread
threading.Thread(target=tts_worker, daemon=True).start()

# ======================
# STREAMING RESPONSE
# ======================
def generate_stream(prompt):
    memory = load_memory()
    remember(memory, prompt, "user")

    system_prompt = (
        "You are Ultron AI, a friendly, intelligent local assistant running on the user's computer. "
        "You store chat memory locally in a file named 'memory.json'. "
        "You never upload user data to the internet."
    )
    context = "\n".join([f"{m['role']}: {m['content']}" for m in memory])
    full_prompt = f"{system_prompt}\n\n{context}\n\nUser: {prompt}\nUltron AI"

    try:
        stream = model.generate_content(full_prompt, stream=True)
        collected = ""

        for chunk in stream:
            if chunk.text:
                # Clean text: remove extra colons, [Done], or control characters
                piece = chunk.text.strip().lstrip(":").replace("[Done]", "").strip()
                collected += piece
                tts_queue.put(piece)
                yield piece
                time.sleep(0.02)

        remember(memory, collected.strip(), "Ultron AI")
        summarize_memory(memory)

    except Exception as e:
        yield f"Error: {str(e)}"

# ======================
# ROUTES
# ======================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat_stream", methods=["POST"])
def chat_stream():
    data = request.get_json()
    prompt = data.get("message", "")
    return Response(generate_stream(prompt), mimetype='text/plain')

if __name__ == "__main__":
    app.run(debug=True)
