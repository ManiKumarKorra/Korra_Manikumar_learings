from flask import Flask, request, jsonify
from google.cloud import dialogflow_v2 as dialogflow
import threading
import queue

app = Flask(__name__)

project_id = 'your-dialogflow-project-id'  # Replace with your Dialogflow project ID
session_id = 'current-user-id'  # This should be unique for each user session
language_code = 'en'

# Queue to handle communication between user and human agent
user_to_agent_queue = queue.Queue()
agent_to_user_queue = queue.Queue()

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req['queryResult']['intent']['displayName']
    
    if intent_name == 'handoff to human':
        # Respond to Dialogflow to confirm handoff
        fulfillment_text = "Connecting with a human agent..."
        
        # Notify the human agent through the queue
        user_message = req['queryResult']['queryText']
        user_to_agent_queue.put(user_message)
        
        # Wait for the agent to respond (this can be improved to handle timeouts or retries)
        agent_response = agent_to_user_queue.get()
        
        return jsonify({'fulfillmentText': agent_response})

    else:
        # Handle other intents by default
        message = req['queryResult']['queryText']
        user_to_agent_queue.put(message)
        
        # Wait for the agent to respond
        agent_response = agent_to_user_queue.get()
        
        return jsonify({'fulfillmentText': agent_response})

def agent_input():
    while True:
        user_message = user_to_agent_queue.get()
        print(f"User: {user_message}")
        agent_message = input("Agent: ")
        agent_to_user_queue.put(agent_message)

if __name__ == '__main__':
    # Start the agent input thread
    agent_thread = threading.Thread(target=agent_input, daemon=True)
    agent_thread.start()
    app.run(debug=True, port=5000)  # You can specify a different port if needed
