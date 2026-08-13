from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Roblox backend działa!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid JSON"
        }), 400

    print("Otrzymano dane:")
    print(data)

    return jsonify({
        "success": True
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
