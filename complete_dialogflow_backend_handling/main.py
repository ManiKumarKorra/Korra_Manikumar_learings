from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import logging
import json
import human_handoff
import get_admin_token


logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

@app.post("/")
async def handle_request(request: Request):
    try:
        payload = await request.json()
        intent = payload['queryResult']['intent']['displayName']
        
        if intent == "nutritional_value":
            fulfillment_text = handle_nutritional_value(payload)
        elif intent == "Operator_Request":
            fulfillment_text =human_handoff.handle_human_handoff(payload)
        elif intent == 'order_list':
            fulfillment_text = order_details(payload)
        elif intent == 'Show_Products':
            return  get_product_fulfillment()
            # fulfillment_text =  "working webhooks"

        else:
            fulfillment_text = "Intent not recognized."
        
        return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })
    except KeyError as e:
        logging.error(f"KeyError: {e}")
        return JSONResponse(content={
            "fulfillmentText": "Invalid request payload."
        })
    except Exception as e:
        logging.error(f"Exception: {e}")
        return JSONResponse(content={
            "fulfillmentText": "An error occurred."
        })

def order_details(payload):
    product_id = payload['queryResult']['parameters']['number']
    url = "https://magento2-demo.scandiweb.com/rest/V1/orders?searchCriteria[filterGroups][0][filters][0][field]=customer_id&searchCriteria[filterGroups][0][filters][0][value]=2&searchCriteria[filterGroups][0][filters][0][condition_type]=eq"

    payload = json.dumps({
    "username": "scandiweb",
    "password": "admin1234"
    })

    bearer_token = get_admin_token.get_admin_token_function()
 


    headers = {
    'Content-Type': 'application/json',
    
    'Authorization': bearer_token ,
    'Cookie': 'PHPSESSID=da15aa48e8cc2ff8c6c591f50846606b; mage-messages=%5B%7B%22type%22%3A%22error%22%2C%22text%22%3A%22Invalid%20Form%20Key.%20Please%20refresh%20the%20page.%22%7D%5D; private_content_version=1525e52799f79b31007fd7968f1d8845'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    data = json.loads(response.text)
    # print(data)

    def fetch_product_details(data, product_id):
    # Iterate through the orders in the items list
        for order in data['items']:
            # Iterate through the products in each order
            for product in order['items']:
                # Check if the product ID matches the given product ID
                if product['product_id'] == product_id:
                    # Fetch the product name and order status
                    product_name = product['name']
                    order_status = order['status']
                    return product_name, order_status
        return None, None  # Return None if product ID is not found

    # Example usage
    # product_id = 164
    # product_id = 1554
    product_name, order_status = fetch_product_details(data, product_id)

    if product_name and order_status:
        fulfillmentText =  f"Product Name: {product_name}, Order Status: {order_status}"
        print(f"Product Name: {product_name}, Order Status: {order_status}")
    else:
        fulfillmentText = f"Product with ID {product_id} not found."
        print(f"Product with ID {product_id} not found.")
    
    return fulfillmentText
        


    # fulfillment_text = 'order item is  '
    # names = ''
    # status =''
    # for item in data["items"]:
    #     for sub_item in item["items"]:
    #         names += (sub_item['name'])
    #         fulfillment_text+=names + " "
    #     for j in  item:
    #         if j == 'status':
    #             status+=item[j]
    #             fulfillment_text+="and its status is " +  status + " "
                
    #     return fulfillment_text
    # else:
    #     logging.error(f"Order details request failed with status code {response.status_code}")
    #     return "Failed to retrieve order details."

def handle_nutritional_value(payload):
    try:
        food_item = payload['queryResult']['parameters']['food_items']
    except KeyError:
        logging.error("food_items parameter missing.")
        return "Food item not provided."

    
    query = f'https://api.api-ninjas.com/v1/nutrition?query={food_item}'
    headers = {"X-Api-Key":"kq3b/eNU4Ljxy7iR+/hJQA==jQZpWToMZiInWMXS"}

    response = requests.get(query, headers=headers)

    if response.status_code == 200:
        nutritional_data = response.json()
        final_nutritional_value = ""

        for data in nutritional_data:
            for key, value in data.items():
                final_nutritional_value += f'{key}: {value} '

        return f"Nutritional value for {food_item}: {final_nutritional_value}"
    else:
        logging.error(f"Nutritional value request failed with status code {response.status_code}")
        return "Failed to retrieve nutritional information."

import json
def get_product_fulfillment():
    # Prepare the simplified fulfillment response for Dialogflow
    bearer_token = get_admin_token.get_admin_token_function()


    url = "https://magento2-demo.scandiweb.com/rest/V1/products?searchCriteria[pageSize]=3&searchCriteria[currentPage]=4"


    # Headers including the authorization token
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearer_token,
    }

    # Send the GET request to the Magento API
    response = requests.get(url, headers=headers)
    products = response.json()

    # Extracting the product details
    product_details = []
    for item in products['items']:
        name = item['name']
        image = item['media_gallery_entries'][0]['file'] if item['media_gallery_entries'] else None
        image_url = f"https://magento2-demo.scandiweb.com/pub/media/catalog/product{image}" if image else "https://via.placeholder.com/150"
        product_details.append({"name": name, "image_url": image_url})

    # Prepare the richContent array with all product details
    rich_content = []
    for product in product_details:
        rich_content.append([
            {
                "type": "info",
                "title": product["name"],
            },
            {
                "type": "image",
                "rawUrl": product["image_url"],
                "accessibilityText": f"Image of {product['name']}"
            }
        ])

    # Prepare the response payload for Dialogflow
    response = {
        "fulfillmentMessages": [
            {
                "payload": {
                    "richContent": rich_content
                }
            }
        ]
    }

    # Return the JSON response
    return JSONResponse(content=response)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)