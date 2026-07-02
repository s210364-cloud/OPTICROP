from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# ---- Load trained artifacts ----
with open("crop_recommendation_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# Feature order must match training
FEATURE_ORDER = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


@app.route("/")
def home():
    return render_template("opticrop_landing.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return render_template("opticrop_predict.html")

    try:
        # Pull the 7 fields from the submitted form, in the correct order
        values = [float(request.form[field]) for field in FEATURE_ORDER]
        features = np.array(values).reshape(1, -1)

        # Scale using the same scaler fit during training
        features_scaled = scaler.transform(features)

        # Predict crop
        prediction = model.predict(features_scaled)[0]

        # Confidence score, if the model supports predict_proba
        if hasattr(model, "predict_proba"):
            probability = round(np.max(model.predict_proba(features_scaled)) * 100, 2)
        else:
            probability = "N/A"

        return render_template("opticrop_result.html", prediction=prediction, probability=probability)

    except (KeyError, ValueError) as e:
        return render_template("opticrop_predict.html", error=f"Invalid input: {e}")


if __name__ == "__main__":
    app.run(debug=True)
