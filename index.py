from app import create_app
from flask import jsonify

app = create_app()

@app.route("/")
def home():
    return "API Flask - Kallpa Backend"

@app.route("/health")
def health():
    return jsonify({
        "status": "OK",
        "message": "Kallpa Backend is running",
        "timestamp": "2026-02-05"
    }), 200

if __name__ == "__main__":
   app.run(port=5000)


