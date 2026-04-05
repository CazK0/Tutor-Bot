import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# The Tutor (for chatting)
tutor_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="You are a Python tutor. Help the user learn Python. Never write the full code solution, only guide them."
)
chat = tutor_model.start_chat(history=[])

# The Task Generator (Standard Mode + JSON Lock)
task_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="You are a Python test generator. Create a short, beginner-friendly Python coding task. Return ONLY a raw JSON object with exactly these keys: 'title', 'task', and 'starter_code'. Do not use markdown blocks.",
    generation_config={"response_mime_type": "application/json"}
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat_route():
    user_message = request.json.get("message")
    response = chat.send_message(user_message)
    return jsonify({"response": response.text})


@app.route("/generate_task", methods=["GET"])
def generate_task():
    try:
        response = task_model.generate_content("Give me a new random beginner Python task.")
        task_data = json.loads(response.text)
        return jsonify(task_data)

    except Exception as e:
        print(f"CRASH REPORT: {e}")
        return jsonify({
            "title": "Assignment Error",
            "task": "The AI hiccuped. Please try again.",
            "starter_code": ""
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
