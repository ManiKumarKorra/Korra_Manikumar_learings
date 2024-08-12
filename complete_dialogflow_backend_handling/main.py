from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import logging
logging.basicConfig(level=logging.DEBUG)  


app = FastAPI()

@app.post("/")
async def handle_request(request: Request):

    payload = await request.json()
    intent = payload['queryResult']['intent']['displayName']
    # food_items = payload['queryResult']['parameters']['food_items']

    if intent == "nutritional_value":
        fulfillment_text =  handle_nutritional_value(payload, intent)
    elif intent == "human_handoff":
       
        fulfillment_text = "hey thete"
   
    else:
        fulfillment_text = "Intent not recognized."
    

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def handle_operator_request():

    fulfillment_text =  "connect with human agent "
    return fulfillment_text


def handle_nutritional_value(payload,intent):
    food_item = payload['queryResult']['parameters']['food_items']
    
    query = f'https://api.api-ninjas.com/v1/nutrition?query={food_item}'
    headers = {"X-Api-Key":"kq3b/eNU4Ljxy7iR+/hJQA==jQZpWToMZiInWMXS"}

    response = requests.get(query,headers= headers)

    if response.status_code == 200:

        nutritional_data = response.json()

        finalnutritional_value =""

        for data in nutritional_data:
            for j in data:
                finalnutritional_value+= f'{j} : {data[j]} '

        fulfillment_text = f"{intent} for {food_item}: {finalnutritional_value}"
         
    else:
        fulfillment_text= "invalid yar"
      
    return fulfillment_text

 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
