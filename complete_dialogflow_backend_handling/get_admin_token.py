import requests
import json

url = "https://demo-magento-2.auroracreation.com/rest/V1/integration/admin/token"

payload = json.dumps({
  "username": "demo_admin",
  "password": "demo_admin123"
})
headers = {
  'Content-Type': 'application/json',
  'Cookie': 'PHPSESSID=7170bemifmlhvfskgtbtdrr193'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
