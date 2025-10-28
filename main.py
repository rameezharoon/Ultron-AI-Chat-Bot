import google.generativeai as genai
import os
import json
import uuid
import re

# ======================
# CONFIGURATION
# ======================
genai.configure(api_key="AIzaSyDgeCk_emxB_MSfkz9fddXcrg5oHripfao")
model = genai.GenerativeModel("gemini-2.5-flash")

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
    print("\n🧩 Summarizing old memory...\n")

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
# STREAMING CHAT FUNCTION
# ======================
def stream_chat(memory, prompt):
    system_prompt = (
        "You are Ultron AI, a local personal assistant running on the user's computer. "
        "You store chat memory locally in a file named 'memory.json'. "
        "You never upload user data to the internet."
    )

    context_text = "\n".join([f"{m['role']}: {m['content']}" for m in memory])
    full_prompt = f"{system_prompt}\n\nConversation so far:\n{context_text}\n\nUser: {prompt}\nAI:"

    # Start streaming
    response_stream = model.generate_content(
        full_prompt,
        stream=True
    )

    final_response = ""

    print("Ultron AI: ", end="", flush=True)
    for chunk in response_stream:
        if chunk.text:
            print(chunk.text, end="", flush=True)
            final_response += chunk.text

    print()  # new line
    return final_response.strip()


# ======================
# MAIN LOOP
# ======================
if __name__ == "__main__":
    print("🤖 Ultron AI Design by Rameez Haroon\n")

    memory = load_memory()

    greeting_text = "Hello! I am Ultron AI. How can I help you today?"
    print("Ultron AI:", greeting_text)
    remember(memory, greeting_text, "assistant")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["quit", "exit", "bye"]:
            goodbye_text = "Goodbye! I'll remember everything for next time."
            print("Ultron AI:", goodbye_text)
            remember(memory, goodbye_text, "assistant")
            break

        try:
            remember(memory, user_input, "user")

            response = stream_chat(memory, user_input)
            remember(memory, response, "assistant")

            memory = summarize_memory(memory)

        except Exception as e:
            error_text = f"Sorry, an error occurred -> {e}"
            print("Ultron AI:", error_text)
