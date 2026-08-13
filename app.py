from flask import Flask, request, jsonify, render_template_string, redirect
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_FILE = "games.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            place_id TEXT PRIMARY KEY,
            game_name TEXT,
            game_link TEXT,
            players TEXT,
            last_player TEXT,
            last_executed TEXT,
            updated_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


def get_games():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row

    games = conn.execute("""
        SELECT * FROM games
        ORDER BY updated_at DESC
    """).fetchall()

    conn.close()

    return games


HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Roblox Games</title>

    <meta http-equiv="refresh" content="5">

    <style>
        body {
            margin: 0;
            padding: 30px;
            background: #111;
            color: white;
            font-family: Arial, sans-serif;
        }

        h1 {
            text-align: center;
        }

        .games {
            max-width: 1100px;
            margin: auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }

        .game {
            background: #1c1c1c;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 20px;
        }

        .game h2 {
            margin-top: 0;
        }

        .item {
            margin: 10px 0;
        }

        .label {
            color: #888;
            font-size: 13px;
        }

        a {
            color: #4da6ff;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        .delete {
            margin-top: 15px;
            background: #b83232;
            color: white;
            border: 0;
            padding: 9px 14px;
            border-radius: 6px;
            cursor: pointer;
        }

        .delete:hover {
            background: #d04444;
        }

        .empty {
            text-align: center;
            color: #888;
        }
    </style>
</head>

<body>

<h1>Roblox Games</h1>

<div class="games">

{% if games %}

    {% for game in games %}

    <div class="game">

        <h2>{{ game["game_name"] }}</h2>

        <div class="item">
            <div class="label">Place ID</div>
            {{ game["place_id"] }}
        </div>

        <div class="item">
            <div class="label">Players</div>
            {{ game["players"] }}
        </div>

        <div class="item">
            <div class="label">Last Player</div>
            {{ game["last_player"] }}
        </div>

        <div class="item">
            <div class="label">Last Executed</div>
            {{ game["last_executed"] }}
        </div>

        <div class="item">
            <div class="label">Last Update</div>
            {{ game["updated_at"] }}
        </div>

        <div class="item">
            <a href="{{ game["game_link"] }}" target="_blank">
                Open Roblox Game
            </a>
        </div>

        <form method="POST" action="/delete/{{ game["place_id"] }}">
            <button class="delete" type="submit">
                Delete Game
            </button>
        </form>

    </div>

    {% endfor %}

{% else %}

    <div class="empty">
        No games have been received yet.
    </div>

{% endif %}

</div>

</body>
</html>
"""


@app.route("/")
def home():
    games = get_games()

    return render_template_string(
        HTML,
        games=games
    )


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(silent=True) or {}

    embeds = data.get("embeds", [])

    if not embeds:
        return jsonify({
            "success": False,
            "error": "No embed received"
        }), 400

    embed = embeds[0]

    description = embed.get(
        "description",
        "Unknown"
    )

    game_name = description.replace(
        "Game Name: `", ""
    ).replace("`", "")

    place_id = ""
    game_link = ""
    players = "0"
    last_player = "Unknown"
    last_executed = "Unknown"

    fields = embed.get("fields", [])

    for field in fields:

        name = field.get("name", "")
        value = field.get("value", "")

        if "Who Executed" in name:
            last_player = value

        elif "What did the user execute" in name:
            last_executed = value

        elif "Place ID" in name:
            place_id = value.replace("`", "").strip()

        elif "Game Link" in name:
            game_link = value.strip()

        elif "Players" in name:
            players = value.replace("`", "").strip()

    if not place_id:
        return jsonify({
            "success": False,
            "error": "Missing PlaceId"
        }), 400

    if not game_link:
        game_link = (
            "https://www.roblox.com/games/"
            + place_id
        )

    now = datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    conn = sqlite3.connect(DB_FILE)

    conn.execute("""
        INSERT INTO games (
            place_id,
            game_name,
            game_link,
            players,
            last_player,
            last_executed,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(place_id)
        DO UPDATE SET
            game_name = excluded.game_name,
            game_link = excluded.game_link,
            players = excluded.players,
            last_player = excluded.last_player,
            last_executed = excluded.last_executed,
            updated_at = excluded.updated_at
    """, (
        place_id,
        game_name,
        game_link,
        players,
        last_player,
        last_executed,
        now
    ))

    conn.commit()
    conn.close()

    print(
        f"Game received: {game_name} | "
        f"PlaceId: {place_id} | "
        f"Players: {players}"
    )

    return jsonify({
        "success": True,
        "placeId": place_id
    })


@app.route("/delete/<place_id>", methods=["POST"])
def delete_game(place_id):

    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        "DELETE FROM games WHERE place_id = ?",
        (place_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
