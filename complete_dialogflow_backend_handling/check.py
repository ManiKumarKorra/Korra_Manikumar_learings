import requests
import json

url = "https://magento2-demo.scandiweb.com/rest/V1/orders?searchCriteria[filterGroups][0][filters][0][field]=customer_id&searchCriteria[filterGroups][0][filters][0][value]=7&searchCriteria[filterGroups][0][filters][0][condition_type]=eq"

payload = json.dumps({
  "username": "scandiweb",
  "password": "admin1234"
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer eyJraWQiOiIxIiwiYWxnIjoiSFMyNTYifQ.eyJ1aWQiOjEsInV0eXBpZCI6MiwiaWF0IjoxNzI0MDU4MzI1LCJleHAiOjE3MjQwNjE5MjV9.Y6tEwDSj7rliwAp6fkqaeSAgMcHQdCFYTwskUIx0AMM',
  'Cookie': 'PHPSESSID=da15aa48e8cc2ff8c6c591f50846606b; mage-messages=%5B%7B%22type%22%3A%22error%22%2C%22text%22%3A%22Invalid%20Form%20Key.%20Please%20refresh%20the%20page.%22%7D%5D; private_content_version=1525e52799f79b31007fd7968f1d8845'
}
response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

# Parse the response text as JSON
# data = json.loads(response.text)
# # print(data)


# def fetch_product_details(data, product_id):
#     # Iterate through the orders in the items list
#     for order in data['items']:
#         # Iterate through the products in each order
#         for product in order['items']:
#             # Check if the product ID matches the given product ID
#             if product['product_id'] == product_id:
#                 # Fetch the product name and order status
#                 product_name = product['name']
#                 order_status = order['status']
#                 return product_name, order_status
#     return None, None  # Return None if product ID is not found

# # Example usage
# # product_id = 164
# product_id = 1562
# product_name, order_status = fetch_product_details(data, product_id)

# if product_name and order_status:
#     print(f"Product Name: {product_name}, Order Status: {order_status}")
# else:
#     print(f"Product with ID {product_id} not found.")



# # fullfillment = 'order item is  '
# # names = ''
# # status =''
# # for item in data["items"]:
# #   for sub_item in item["items"]:
# #     names += (sub_item['name'])
# #     fullfillment+=names + " "
# #   for j in  item:
# #     if j == 'status':
# #       status+=item[j]
# #       fullfillment+="and its status is " +  status + " "

# # print(names)
# # print(status)
# # print(fullfillment)
# # print(status)

# # status = ''

# # for item in data['items']:
# #     d =  data['items']
# #     for j in item:
    

# #       if j == 'status':
# #         print(item[j])

# # print(status)


# # print(data)