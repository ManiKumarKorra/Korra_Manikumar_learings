Rasa Open Source 

Rasa is a chatbot framework that, unlike Voiceflow or Dialogflow, does not have a graphical interface but offers great customization and uses NLU (Natural Language Understanding). 

Install Rasa 

Rasa doesnt  supports several Python versions, including 3.12.4, but you can use version 3.8 aetc . It's always a best practice to create a virtual environment in Python: 

PS F:\Learning\Rasa> py -3.8 -m venv myenv 
PS F:\Learning\Rasa> .\myenv\Scripts\activate 
 

Now, let's install Rasa. First, make sure your pip version is up to date: 

pip3 install -U pip 
 

To install Rasa Open Source: 

pip3 install rasa 
 

You can now create a new project with: 

rasa init 
 

Folder Structure 

data/nlu.yml 

This is where you create intents (an intent is basically the intention of the customer at that point in time). For example, if you want to create an intent where a customer wants to know the nutritional value of food, you would do it like this: 

- intent: nutritional_value 
  examples: | 
    - what is the nutritional value of [pizza](food) 
    - what are the calories in [chicken](food) 
    - how many calories are in [banana](food)? 
    - tell me the nutritional facts for [broccoli](food) 
    - what's the nutrition info for [salmon](food)? 
    - can you provide the nutritional information of [rice](food)? 
    - I'd like to know the nutrition content of [apple](food) 
    - how many carbs are in [pasta](food)? 
 

Vlaues enclosed in () a entity and values enclosed in []valueFor now, let's ignore the values enclosed in [] and (). 

After creating our intent called nutritional_value, we need to specify what to do when the user's intent matches nutritional_value. For that, we need to map it in stories.yml. 

stories.yml 

- story: nutritional path 
  steps: 
    - intent: nutritional_value 
    - action: action_extract_food 
 

We map this intent to a story. One story can have multiple intents and actions. For example: 

- story: happy path 
  steps: 
    - intent: greet 
    - action: utter_greet 
    - intent: mood_great 
    - action: utter_happy 
 

Going back to our nutritional_value example, we mapped it to the nutritional path story and an action called action_extract_food. To execute action_extract_food, we need to put an entry in domain.yml. 

domain.yml 

In domain.yml, we can map intents to static replies (like a welcome message) or actions. For instance, if a user says they want to know the nutritional value of eggs, Rasa knows the customer wants nutritional information about something but needs to extract the specific food item (in this case, eggs). 

We need to create entities. What are entities? In the sentence "I want to know the nutritional value of eggs," "eggs" is an entity of the type "food." So, we need to create an entity in domain.yml. 

entities: 
  - food 
 

actions.py 

We need to write the logic to extract the food entity from a sentence and get the nutritional value of that particular food using an API call. Here is how we do it: 

from typing import Any, Text, Dict, List 
from rasa_sdk import Action, Tracker 
from rasa_sdk.executor import CollectingDispatcher 
import requests 
 
class ActionExtractFood(Action): 
    def name(self) -> Text: 
        return "action_extract_food" 
 
    def api_call(self, query, headers): 
        response = requests.get(query, headers=headers) 
        return response.json() 
 
    def run(self, dispatcher: CollectingDispatcher,  
            tracker: Tracker,  
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
 
        entities = tracker.latest_message.get('entities', []) 
        food_entity = None 
 
        for entity in entities: 
            if entity.get('entity') == 'food': 
                food_entity = entity.get('value') 
                break 
 
        if food_entity: 
            query = f'https://api.api-ninjas.com/v1/nutrition?query={food_entity}' 
            headers = {"X-Api-Key": "kq3b/eNU4Ljxy7iR+/hJQA==jQZpWToMZiInWMXS"} 
            api_response = self.api_call(query, headers) 
 
            if api_response: 
                nutritional_info = api_response[0]    
                message = f"Nutritional information for {food_entity}: Calories - {nutritional_info}." 
                dispatcher.utter_message(text=message) 
            else: 
                dispatcher.utter_message(text="Sorry, I couldn't retrieve the nutritional information at the moment.") 
        else: 
            dispatcher.utter_message(text="Sorry, I couldn't extract the food entity.") 
 
        return [] 
 

endpoints.yml 

Uncomment the following: 

action_endpoint: 
  url: "http://localhost:5055/webhook" 
 

Training and Running Rasa 

After making these changes, Rasa NLU needs to be trained. Use this command in the CLI: 

rasa train 
 

Then, run your Rasa action server so that actions will work: 

rasa run actions 
 

You can interact with the Rasa chatbot in the CLI using: 

rasa shell 
 

Use 

 rasa shell nlu to debug. 

With these steps, you should have a functioning Rasa installation and a basic understanding of its folder structure and customization. 

 