import requests
import json

url = "https://magento2-demo.scandiweb.com/rest/V1/integration/customer/token"

payload = json.dumps({
  "username": "manikumar.ramakrishna@ziffity.com",
  "password": "SATHYArama@7"
})
headers = {
  'Content-Type': 'application/json',
  'Cookie': 'PHPSESSID=7170bemifmlhvfskgtbtdrr193'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
