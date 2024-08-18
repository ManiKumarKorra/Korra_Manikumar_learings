import requests
import json



def get_admin_token_function():

  url = "https://magento2-demo.scandiweb.com/rest/V1/integration/admin/token"
  # url = "https://magento-demo.mageplaza.com/rest/V1/integration/admin/token"


  payload = json.dumps({
    "username": "scandiweb",
    "password": "admin1234"
    # "username": "mageplaza",
    # "password": "demo123"
  })
  headers = {
    'Content-Type': 'application/json',
    'Cookie': 'PHPSESSID=7170bemifmlhvfskgtbtdrr193'
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  
  print(response.text)
  bearer_token = response.text
  bearer_token = bearer_token.strip('"')
  formatted_bearer_token = f'Bearer {bearer_token}'

  return formatted_bearer_token




get_admin_token_function()

