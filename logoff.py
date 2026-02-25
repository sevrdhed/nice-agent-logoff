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


token = get_bearer_token()
logoff_agent(token, "19858540")   # replace with a real agent ID