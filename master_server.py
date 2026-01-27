from flask import Flask, request, jsonify, render_template, send_from_directory
import os

app = Flask(__name__)

# Store recent predictions for history display
recent_predictions = []
MAX_HISTORY = 20

@app.route("/")
def index():
    """Serve the frontend dashboard"""
    return send_from_directory('.', 'dashboard.html')

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    process_count = data.get("process_count", 0)
    cpu_usage = data.get("cpu_usage", 0)

    # --- Simple ML-inspired stress score ---
    # (you can say this is logistic-style scoring)
    stress_score = (0.6 * (cpu_usage / 100)) + (0.4 * (process_count / 300))

    if stress_score > 0.8:
        mode = "CRITICAL"
        nice = 15
    elif stress_score > 0.6:
        mode = "POWER_SAVE"
        nice = 10
    elif stress_score > 0.4:
        mode = "MODERATE"
        nice = 5
    else:
        mode = "BALANCED"
        nice = 0

    prediction = {
        "mode": mode,
        "nice": nice,
        "stress_score": round(stress_score, 3),
        "process_count": process_count,
        "cpu_usage": cpu_usage
    }

    # Store in history
    recent_predictions.append(prediction)
    if len(recent_predictions) > MAX_HISTORY:
        recent_predictions.pop(0)

    print(
        f"Received: processes={process_count}, cpu={cpu_usage:.1f}% "
        f"→ {mode} (nice={nice})"
    )

    return jsonify(prediction)

@app.route("/history", methods=["GET"])
def get_history():
    """Get recent prediction history for frontend display"""
    return jsonify(recent_predictions)

@app.route("/status", methods=["GET"])
def get_status():
    """Get current server status"""
    if recent_predictions:
        latest = recent_predictions[-1]
    else:
        latest = {
            "mode": "UNKNOWN",
            "nice": 0,
            "stress_score": 0,
            "process_count": 0,
            "cpu_usage": 0
        }
    
    return jsonify({
        "status": "online",
        "latest_prediction": latest,
        "total_predictions": len(recent_predictions)
    })

if __name__ == "__main__":
    print("🚀 AI Battery Saver Master Server Starting...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔌 API Endpoint: http://localhost:5000/predict")
    app.run(host="0.0.0.0", port=5000, debug=True)

