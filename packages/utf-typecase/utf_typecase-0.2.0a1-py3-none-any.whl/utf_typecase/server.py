# utf_typecase/server.py

from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

# Store characters submitted by token (in-memory)
character_store: dict[str, list[str]] = {}

# HTML template for SPA interface
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>utf-typecase</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        body { font-family: sans-serif; padding: 1em; }
        input, button { font-size: 1.2em; margin: 0.3em; }
        .grid { display: flex; flex-wrap: wrap; margin-top: 1em; }
        .char-btn {
            min-width: 60px;
            min-height: 60px;
            margin: 5px;
            font-size: 1.6em;
            text-align: center;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>utf-typecase</h1>
    <p>Enter UTF characters to generate input buttons:</p>
    <form id="charForm">
        <input type="text" id="chars" maxlength="100" required />
        <input type="text" id="token" placeholder="Your token" required />
        <button type="submit">Create Buttons</button>
    </form>

    <div class="grid" id="buttonGrid"></div>

    <script>
        // Automatically populate input fields
        const symbols = "—’→∞⏳★✅✓❌🌐🎯👉👋💡🔐🔧🚨🧠🧩🧪🧲🧼";  // default symbols
        document.getElementById("chars").value = symbols;
        document.getElementById("token").value = "dev";       // default token

        function generateButtons(chars, token) {
            const grid = document.getElementById("buttonGrid");
            grid.innerHTML = "";

            for (let c of chars) {
                const btn = document.createElement("button");
                btn.className = "char-btn";
                const hex = c.codePointAt(0).toString(16).toUpperCase().padStart(4, '0');
                btn.innerText = c + "\\nU+" + hex;
                btn.onclick = () => {
                    fetch("/send", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({char: c, token: token})
                    }).then(res => res.json()).then(data => {
                        if (!data.ok) alert("Failed: " + data.error);
                    });
                };
                grid.appendChild(btn);
            }
        }

        // Generate buttons automatically on page load
        window.addEventListener("load", () => {
            const chars = document.getElementById("chars").value;
            const token = document.getElementById("token").value;
            generateButtons(chars, token);
        });

        // Manual form submission
        document.getElementById("charForm").onsubmit = function(e) {
            e.preventDefault();
            const chars = document.getElementById("chars").value;
            const token = document.getElementById("token").value;
            generateButtons(chars, token);
        };
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_PAGE)


@app.route("/send", methods=["POST"])
def receive():
    data = request.get_json()
    char = data.get("char")
    token = data.get("token")

    if not re.fullmatch(r"\w{1,32}", token or ""):
        return jsonify(ok=False, error="Invalid token")

    if not isinstance(char, str) or len(char) != 1:
        return jsonify(ok=False, error="Invalid character")

    character_store.setdefault(token, []).append(char)
    print(f"[RECEIVED] '{char}' stored under token '{token}'")

    return jsonify(ok=True)


@app.route("/api/characters", methods=["GET"])
def get_characters():
    token = request.args.get("token", "")
    if not re.fullmatch(r"\w{1,32}", token):
        return jsonify(ok=False, error="Invalid token")

    chars = character_store.get(token)
    if not chars:
        msg = "No characters available for this token."
        response = jsonify(ok=True, characters=[], message=msg)
        return response

    # Return and remove the characters for this token
    character_store[token] = []
    return jsonify(ok=True, characters=chars)


def start_server(port=5000, host="127.0.0.1", debug=False, **kwargs):
    app.run(port=port, host=host, debug=debug, **kwargs)


# For quick testing: run with 'python src/utf_typecase/server.py'
if __name__ == "__main__":
    app.run(debug=True, port=5000)
