from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

def get_slides():
    try:
        # Try to find slides.json in the root
        path = os.path.join(os.path.dirname(__file__), '..', 'slides.json')
        if not os.path.exists(path):
            path = 'slides.json' # Fallback
        
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def dashboard():
    slides = get_slides()
    
    slides_html = ""
    if isinstance(slides, dict) and "error" not in slides:
        for key, value in slides.items():
            slides_html += f"<li><b>Slide {key}:</b> {value}</li>"
    else:
        slides_html = f"<p>Error loading slides: {slides.get('error', 'Unknown error')}</p>"

    return f"""
    <html>
    <head>
    <title>Siesta Data</title>
    <style>
    body{{
        background:black;
        color:white;
        font-family:Arial;
        text-align:center;
        padding:50px;
    }}
    h1{{
        font-size:50px;
        color:#00ffaa;
    }}
    .card{{
        margin:30px auto;
        max-width:600px;
        padding:20px;
        border-radius:10px;
        background:#111;
        box-shadow:0 0 20px #00ffaa;
        text-align:left;
    }}
    h2{{ color:#00ffaa; border-bottom:1px solid #333; padding-bottom:10px; }}
    ul{{ list-style:none; padding:0; }}
    li{{ margin-bottom:15px; line-height:1.5; }}
    b{{ color:#00ffaa; }}
    </style>
    </head>
    <body>
    <h1>Siesta Data Dashboard</h1>
    <div class="card">
    <h2>Project Status</h2>
    <p>Running: Online</p>
    </div>
    <div class="card">
    <h2>Slides Content</h2>
    <ul>
    {slides_html}
    </ul>
    </div>
    </body>
    </html>
    """

@app.route("/api/slides")
def api_slides():
    return jsonify(get_slides())

if __name__ == "__main__":
    app.run(port=5000)
