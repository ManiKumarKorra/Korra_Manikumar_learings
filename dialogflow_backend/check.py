import requests
import json

url = "https://magento2-demo.scandiweb.com/rest/V1/orders?searchCriteria[filterGroups][0][filters][0][field]=customer_id&searchCriteria[filterGroups][0][filters][0][value]=3&searchCriteria[filterGroups][0][filters][0][condition_type]=eq"

payload = json.dumps({
  "username": "scandiweb",
  "password": "admin1234"
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer eyJraWQiOiIxIiwiYWxnIjoiSFMyNTYifQ.eyJ1aWQiOjEsInV0eXBpZCI6MiwiaWF0IjoxNzIzNTMwMTk2LCJleHAiOjE3MjM1MzM3OTZ9.41wbwFybKbyXIEHC6CGwkxPT56_aG2Hrvo5GTUHn7tE',
  'Cookie': 'PHPSESSID=da15aa48e8cc2ff8c6c591f50846606b; mage-messages=%5B%7B%22type%22%3A%22error%22%2C%22text%22%3A%22Invalid%20Form%20Key.%20Please%20refresh%20the%20page.%22%7D%5D; private_content_version=1525e52799f79b31007fd7968f1d8845'
}
response = requests.request("GET", url, headers=headers, data=payload)


# Parse the response text as JSON
data = json.loads(response.text)

# Extract names from the parsed JSON
names = []
for item in data["items"]:
    for sub_item in item["items"]:
        names.append(sub_item["name"])

# Print the names
for name in names:
    print(name)