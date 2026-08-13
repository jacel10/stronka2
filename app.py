from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Roblox backend działa!"

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json(silent=True) or {}

    place_id = data.get("placeId")

    if place_id is None:
        return jsonify({
            "success": False,
            "error": "Missing PlaceId"
        }), 400

    print("PlaceId:", place_id)

    return jsonify({
        "success": True,
        "placeId": place_id
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
