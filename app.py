from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

SUSPICIOUS_WORDS = [
    "login", "verify", "update", "secure", "account",
    "bank", "paypal", "password", "bonus", "free"
]

STATS = {
    "total_checks": 0,
    "today": datetime.now().date()
}

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

@app.route("/")
def home():
    return f"""
    <h2>🔍 CheckLink</h2>
    <form action="/check">
        <input name="u" placeholder="Βάλε link εδώ">
        <button>Έλεγχος</button>
    </form>
    <p>Συνολικοί έλεγχοι: {STATS["total_checks"]}</p>
    """

@app.route("/check")
def check():
    url = request.args.get("u")
    if not url:
        return "Δεν δόθηκε link"

    STATS["total_checks"] += 1

    score, label, color, reasons = analyze_url(url)
    reasons_html = "".join(f"<li>{r}</li>" for r in reasons) or "<li>Δεν βρέθηκαν ύποπτα στοιχεία</li>"

    return f"""
    <h2>{label} ({score}/100)</h2>
    <ul>{reasons_html}</ul>
    <a href="/">Νέος έλεγχος</a>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
