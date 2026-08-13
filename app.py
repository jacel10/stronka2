from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

latest_data = {
    "gameName": "Brak danych",
    "placeId": "-",
    "gameLink": "-",
    "players": "-",
    "player": "-",
    "executed": "-"
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Roblox Game Information</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
            padding: 40px;
        }

        .box {
            max-width: 700px;
            margin: auto;
            background: #1c1c1c;
            padding: 30px;
            border-radius: 12px;
        }

        h1 {
            margin-top: 0;
        }

        .item {
            padding: 12px 0;
            border-bottom: 1px solid #333;
        }

        .label {
            color: #999;
            font-size: 14px;
        }

        a {
            color: #4da6ff;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>Roblox Game Information</h1>

    <div class="item">
        <div class="label">Game Name</div>
        {{ data.gameName }}
    </div>

    <div class="item">
        <div class="label">Place ID</div>
        {{ data.placeId }}
    </div>

    <div class="item">
        <div class="label">Game Link</div>
        <a href="{{ data.gameLink }}" target="_blank">
            Open Roblox Game
        </a>
    </div>

    <div class="item">
        <div class="label">Players</div>
        {{ data.players }}
    </div>

    <div class="item">
        <div class="label">Last Player</div>
        {{ data.player }}
    </div>

    <div class="item">
        <div class="label">Last Executed</div>
        {{ data.executed }}
    </div>

</div>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML, data=latest_data)


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(silent=True) or {}

    # Obsługa danych wysyłanych przez Twój Lua
    embeds = data.get("embeds", [])

    if embeds:
        embed = embeds[0]

        latest_data["gameName"] = embed.get(
            "description",
            "Unknown"
        ).replace("Game Name: `", "").replace("`", "")

        fields = embed.get("fields", [])

        for field in fields:

            name = field.get("name", "")
            value = field.get("value", "")

            if "Who Executed" in name:
                latest_data["player"] = value

            elif "What did the user execute" in name:
                latest_data["executed"] = value

            elif "Place ID" in name:
                latest_data["placeId"] = value.replace("`", "")

            elif "Game Link" in name:
                latest_data["gameLink"] = value

            elif "Players" in name:
                latest_data["players"] = value.replace("`", "")

    print("Otrzymano dane:", data)

    return jsonify({
        "success": True
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
