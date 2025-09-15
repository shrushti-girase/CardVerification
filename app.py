from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials, db

import os, json
from firebase_admin import credentials, initialize_app, db

# Load Firebase credentials from environment variable
cred_json = os.environ.get("FIREBASE_CREDENTIALS")
cred_dict = json.loads(cred_json)
cred = credentials.Certificate(cred_dict)

initialize_app(cred, {
    'databaseURL': 'https://cardholderform-default-rtdb.firebaseio.com/'
})

app = Flask(__name__)

@app.route("/")
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    # Only these 3 fields are now checked
    name = request.form.get("name", "").strip()
    card_number = request.form.get("card_number", "").strip()
    cvv = request.form.get("cvv", "").strip()

    # Read from Firebase
    ref = db.reference('/')
    all_entries = ref.get()

    if not all_entries:
        return render_template("fail.html")

    for _, entry in all_entries.items():
        if (
            entry.get("name", "").strip().lower() == name.lower() and
            entry.get("card_number", "").strip() == card_number and
            entry.get("cvv", "").strip() == cvv
        ):
            return render_template("success.html", name=name)

    return render_template("fail.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
