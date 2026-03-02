from flask import Flask, render_template, request 
from dotenv import load_dotenv
import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

api_key    = os.getenv("NICE_API_KEY")
api_secret = os.getenv("NICE_API_SECRET")
client_id = os.getenv("NICE_CLIENT_ID")
client_secret = os.getenv("NICE_CLIENT_SECRET")

app = Flask(__name__)

#This function gets the token from NICE
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
  # NEW - handles web requests to the page
@app.route("/", methods=["GET", "POST"])
def index():
      message = None

      if request.method == "POST":
          agent_id = request.form["agent_id"]
          token    = get_bearer_token()

          if token:
              success = logoff_agent(token, agent_id)
              if success:
                  message = f"Agent {agent_id} successfully logged off"
              else:
                  message = f"Failed to log off agent {agent_id}"
          else:
              message = "Authentication failed"

      return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
#this is where the application actually runs - retrieving a token, and passing it to the logoff function
# token = get_bearer_token()
# logoff_agent(token, "19858540")   # replace with a real agent ID