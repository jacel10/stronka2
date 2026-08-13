from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")

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

    print("=== Roblox Game ===")
    print("Game:", data.get("gameName"))
    print("Place ID:", data.get("placeId"))
    print("Players:", data.get("players"))
    print("Player:", data.get("player"))
    print("Executed:", data.get("executed"))

    if DISCORD_WEBHOOK:
        embed = {
            "title": "Nexora Execute Stuff",
            "description": f"Game Name: `{data.get('gameName', 'Unknown')}`",
            "color": 0,
            "fields": [
                {
                    "name": "Place ID",
                    "value": f"`{data.get('placeId', 'Unknown')}`",
                    "inline": True
                },
                {
                    "name": "Players",
                    "value": f"`{data.get('players', 0)}`",
                    "inline": True
                },
                {
                    "name": "Game Link",
                    "value": data.get("gameLink", "Unknown"),
                    "inline": False
                },
                {
                    "name": "Who Executed it?",
                    "value": data.get("player", "Unknown"),
                    "inline": True
                },
                {
                    "name": "What did the user execute?",
                    "value": data.get("executed", "Unknown"),
                    "inline": True
                }
            ]
        }

        response = requests.post(
            DISCORD_WEBHOOK,
            json={"embeds": [embed]},
            timeout=10
        )

        response.raise_for_status()

    return jsonify({
        "success": True
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
