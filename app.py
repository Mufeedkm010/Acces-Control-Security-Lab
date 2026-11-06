from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Access Control Security Lab</h1>
    <p>Flask application is running successfully.</p>
    <p>Next: IDOR and Broken Access Control testing.</p>
    """

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )