from flask import Flask, request, jsonify
import openai, os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return "OpenAI app running"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    q = data.get("question", "Hello")
    resp = openai.Completion.create(
        model="text-davinci-003",
        prompt=q,
        max_tokens=60
    )
    return jsonify({"answer": resp.choices[0].text.strip()})

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", default=5000, type=int)
    args = p.parse_args()
    app.run(host="0.0.0.0", port=args.port)
