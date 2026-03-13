from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime
import requests
import urllib3
import csv
import io
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

api_key       = os.getenv("NICE_API_KEY")
api_secret    = os.getenv("NICE_API_SECRET")
client_id     = os.getenv("NICE_CLIENT_ID")
client_secret = os.getenv("NICE_CLIENT_SECRET")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///logoff.db"
db = SQLAlchemy(app)

class LogEntry(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    agent_id  = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status    = db.Column(db.String, nullable=False)
    message   = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()

#This authentication function gets the token from NICE
def get_bearer_token():
    url = "https://cxone.niceincontact.com/auth/token"

    headers = {
          "Content-Type": "application/x-www-form-urlencoded"
      }

    payload = {
          "grant_type": "password",
          "username":   api_key,
          "password":   api_secret,
          "client_id":  client_id,
          "client_secret":  client_secret
      }

    response = requests.post(url, headers=headers, data=payload, verify=False)

    if response.status_code == 200:
          token = response.json()["access_token"]
          return token
    else:
          print("Auth failed:", response.status_code, response.text)
          return None
    
#This is the single agent logoff function.
def logoff_agent(token, agent_id):
      url = f"https://api-b32.nice-incontact.com/incontactapi/services/v33.0/agents/{agent_id}/logout"

      headers = {
          "Authorization": f"Bearer {token}",
          "Accept":        "application/json"
      }

      response = requests.post(url, headers=headers, verify=False)

      if response.status_code == 202:
          print(f"Agent {agent_id} successfully logged off")
          return True
      else:
          print("Logoff failed:", response.status_code, response.text)
          return False
# Handles web requests to the page
@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    if request.method == "POST":
        agent_ids = []

        # get IDs from the CSV file if one was uploaded
        csv_file = request.files.get("csv_file")
        if csv_file and csv_file.filename != "":
            stream = io.StringIO(csv_file.stream.read().decode("utf-8"))
            reader = csv.reader(stream)
            for row in reader:
                for cell in row:
                    cell = cell.strip()
                    if cell:
                        agent_ids.append(cell)

        # get IDs from the text input if provided
        text_input = request.form.get("agent_ids", "").strip()
        if text_input:
            for agent_id in text_input.split(","):
                agent_id = agent_id.strip()
                if agent_id:
                    agent_ids.append(agent_id)

        if agent_ids:
            token = get_bearer_token()
            if token:
                for agent_id in agent_ids:
                    success = logoff_agent(token, agent_id)
                    if success:
                        message = f"Agent {agent_id} successfully logged off"
                        status  = "success"
                    else:
                        message = f"Failed to log off agent {agent_id}"
                        status  = "failed"

                    db.session.add(LogEntry(agent_id=agent_id, status=status, message=message))
                    results.append({"success": success, "message": message})

                db.session.commit()
            else:
                results.append({"success": False, "message": "Authentication failed"})
        else:
            results.append({"success": False, "message": "No agent IDs provided"})

    return render_template("index.html", results=results)

# Handles the log viewer page
@app.route("/logs")
def logs():
    entries = LogEntry.query.order_by(LogEntry.timestamp.desc()).all()
    return render_template("logs.html", entries=entries)


if __name__ == "__main__":
    app.run(debug=True)
