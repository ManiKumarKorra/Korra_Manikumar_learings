import requests
import json


url = "https://magento2-demo.scandiweb.com/rest/V1/products?searchCriteria[pageSize]=2&searchCriteria[currentPage]=4"

    # Headers including the authorization token
# Headers including the authorization token
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJraWQiOiIxIiwiYWxnIjoiSFMyNTYifQ.eyJ1aWQiOjEsInV0eXBpZCI6MiwiaWF0IjoxNzIzOTY4MTM4LCJleHAiOjE3MjM5NzE3Mzh9.378P79zaMTBd1ago7s9wZ6yhRWq_5XcvlKZOlmYQHII',
}

# Send the GET request to the Magento API
response = requests.request("GET", url, headers=headers)
products = response.json()

# Extracting the product name and image
product_details = []
for item in products['items']:
    name = item['name']
    image = item['media_gallery_entries'][0]['file'] if item['media_gallery_entries'] else None
    product_details.append({"name": name, "image": image})

# Prepare the fulfillment response for Dialogflow
fulfillment_response = {
    "fulfillmentMessages": [
        {
            "text": {
                "text": [f"Product Name: {product['name']}\nImage URL: https://magento2-demo.scandiweb.com/pub/media/catalog/product{product['image']}"]
            }
        } for product in product_details
    ]
}

# Print the fulfillment response in JSON format
print(json.dumps(fulfillment_response, indent=2))
