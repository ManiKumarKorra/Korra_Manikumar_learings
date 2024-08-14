import requests
import json

url = "https://magento2-demo.scandiweb.com/rest/V1/integration/admin/token"

payload = json.dumps({
  "username": "scandiweb",
  "password": "admin1234"
})
headers = {
  'Content-Type': 'application/json',
  'Cookie': 'PHPSESSID=7170bemifmlhvfskgtbtdrr193'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
