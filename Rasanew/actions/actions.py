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
