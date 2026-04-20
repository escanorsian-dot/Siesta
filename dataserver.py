from flask import Flask
import webbrowser
import threading

app = Flask(__name__)

@app.route("/")
def dashboard():

    return """
    <html>
    <head>
    <title>Siesta Data</title>

    <style>
    body{
        background:black;
        color:white;
        font-family:Arial;
        text-align:center;
        padding-top:100px;
    }

    h1{
        font-size:50px;
        color:#00ffaa;
    }

    .card{
        margin:30px auto;
        width:300px;
        padding:20px;
        border-radius:10px;
        background:#111;
        box-shadow:0 0 20px #00ffaa;
    }

    </style>
    </head>

    <body>

    <h1>Siesta Data Dashboard</h1>

    <div class="card">
    <h2>Project Status</h2>
    <p>Running</p>
    </div>

    <div class="card">
    <h2>Assistant</h2>
    <p>Online</p>
    </div>

    </body>
    </html>
    """


def start_dashboard():

    webbrowser.open("http://127.0.0.1:5000")

    app.run(port=5000)