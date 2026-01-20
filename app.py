from flask import Flask, request
from datetime import datetime
import os

app = Flask(__name__)

# =========================
# CONFIG
# =========================
SUSPICIOUS_WORDS = [
    "login", "verify", "update", "secure", "account",
    "bank", "paypal", "password", "bonus", "free"
]

# simple in-memory stats
STATS = {
    "total_checks": 0,
    "today": datetime.now().date()
}

# =========================
# LOGGING
# =========================
def log_check(url, score, label, reasons):
    with open("checks.log", "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"{url} | {score} | {label} | "
            f"{', '.join(reasons) if reasons else 'Κανένα εύρημα'}\n"
        )

# =========================
# CORE LOGIC
# =========================
def analyze_url(url):
    score = 100
    reasons = []

    if url.startswith("http://"):
        score -= 30
        reasons.append("Χρήση HTTP αντί για HTTPS")

    for word in SUSPICIOUS_WORDS:
        if word in url.lower():
            score -= 10
            reasons.append(f"Ύποπτη λέξη στο URL: {word}")

    if url.count(".") > 3:
        score -= 10
        reasons.append("Πολλά subdomains")

    if score >= 80:
        label = "ΑΣΦΑΛΕΣ"
        color = "green"
    elif score >= 50:
        label = "ΡΙΨΟΚΙΝΔΥΝΟ"
        color = "orange"
    else:
        label = "ΕΠΙΚΙΝΔΥΝΟ"
        color = "red"

    return score, label, color, reasons

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return f"""
    <html>
    <head>
        <title>CheckLink</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial; padding:20px; max-width:600px; margin:auto; }}
            input {{ width:100%; padding:10px; }}
            button {{ padding:10px 20px; margin-top:10px; }}
            .box {{ border:1px solid #ddd; padding:15px; margin-top:20px; }}
        </style>
    </head>
    <body>
        <h2>🔍 CheckLink</h2>
        <p>Έλεγξε αν ένα link είναι ασφαλές πριν το ανοίξεις.</p>

        <form action="/check">
            <input name="u" placeholder="Βάλε link εδώ">
            <button>Έλεγχος</button>
        </form>

        <p style="margin-top:20px;color:#777;">
            🔢 Συνολικοί έλεγχοι σήμερα: {STATS["total_checks"]}
        </p>
    </body>
    </html>
    """

@app.route("/check")
def check():
    url = request.args.get("u")
    if not url:
        return "Δεν δόθηκε link"

    today = datetime.now().date()
    if STATS["today"] != today:
        STATS["today"] = today
        STATS["total_checks"] = 0

    STATS["total_checks"] += 1

    score, label, color, reasons = analyze_url(url)
    log_check(url, score, label, reasons)

    if not reasons:
        reasons_html = "<li>Δεν εντοπίστηκαν ύποπτα στοιχεία</li>"
    else:
        reasons_html = "".join(f"<li>{r}</li>" for r in reasons)

    return f"""
    <html>
    <head>
        <title>Αποτέλεσμα</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial; padding:20px; max-width:600px; margin:auto; }}
            .score {{ font-size:22px; font-weight:bold; color:{color}; }}
            .box {{ border:1px solid #ddd; padding:15px; margin-top:20px; }}
            button {{ padding:10px 20px; }}
        </style>
    </head>
    <body>

        <h2>Αποτέλεσμα Ελέγχου</h2>

        <div class="box">
            <p><b>Link:</b> {url}</p>
            <p class="score">{label} ({score}/100)</p>
            <ul>{reasons_html}</ul>
            <a href="{url}" target="_blank">👉 Συνέχεια στο link</a>
        </div>

        <div class="box">
            <h3>Έλεγχος νέου link</h3>
            <form action="/check">
                <input name="u" placeholder="Βάλε νέο link">
                <button>Έλεγχος</button>
            </form>
        </div>

        <p style="margin-top:20px;color:#777;">
            🔢 Έλεγχοι σήμερα: {STATS["total_checks"]}
        </p>

    </body>
    </html>
    """

