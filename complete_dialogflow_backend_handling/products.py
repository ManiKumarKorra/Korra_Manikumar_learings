import requests
import json

def get_product_details():
    # URL to fetch products with specified page size and current page
    url = "https://magento2-demo.scandiweb.com/rest/V1/products?searchCriteria[pageSize]=4&searchCriteria[currentPage]=1"

    # Headers including the authorization token
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJraWQiOiIxIiwiYWxnIjoiSFMyNTYifQ.eyJ1aWQiOjEsInV0eXBpZCI6MiwiaWF0IjoxNzIzODEzNzI5LCJleHAiOjE3MjM4MTczMjl9.tZu7h-jjuMCK06t0-eOz-MVMNLRqgOrmiEvurUnERik',
    }

    # Send the GET request to the Magento API
    response = requests.get(url, headers=headers)
    products = response.json()

    # Extract the first product's name and image
    if products['items']:
        first_product = products['items'][0]
        name = first_product['name']
        image = first_product['media_gallery_entries'][0]['file'] if first_product['media_gallery_entries'] else None

        # Prepare the fulfillment response for Dialogflow
        fulfillment_response = {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [f"Product Name: {name}\nImage URL: https://magento2-demo.scandiweb.com/pub/media/catalog/product{image}"]
                    }
                }
            ]
        }

        return json.dumps(fulfillment_response, indent=2)

    return "No products found."

# Example usage
print(get_product_details())
