from flask import Flask, jsonify
import time

app = Flask(__name__)

START_TIME = time.time()

@app.route("/")
def home():
    return "Bot is running 🚀"

@app.route("/ping")
def ping():
    uptime = round(time.time() - START_TIME, 2)
    return jsonify({
        "status": "alive",
        "message": "Pong 🏓",
        "uptime_seconds": uptime,
        "website": "Online ✅"
    })

@app.route("/dev")
def dev_info():
    return jsonify({
        "developer_name": "Dev",
        "telegram_username": "@ikbug",
        "location": "Rajasthan 🇮🇳",
        "role": "Bot Developer",
        "vibe": "Code > Sleep 😴💻"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
