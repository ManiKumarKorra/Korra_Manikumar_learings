from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from google.cloud import dialogflow_v2 as dialogflow
import os
import logging

logging.basicConfig(level=logging.INFO)

class ConnectionManager:
    """Class defining socket events"""
    def __init__(self):
        """Init method, keeping track of connections"""
        self.active_connections: list[WebSocket] = []
        self.operators: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, role: str):
        """Connect event"""
        await websocket.accept()
        if role == "operator":
            self.operators.append(websocket)
        else:
            self.active_connections.append(websocket)
        logging.info(f"Connected: {role}")

    async def disconnect(self, websocket: WebSocket):
        """Disconnect event"""
        if websocket in self.operators:
            self.operators.remove(websocket)
        else:
            self.active_connections.remove(websocket)
        logging.info("Disconnected")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Direct message"""
        await websocket.send_text(message)
        logging.info(f"Sent personal message: {message}")

    async def broadcast(self, message: str, sender: WebSocket):
        """Broadcast message to all connections except the sender"""
        for connection in self.active_connections + self.operators:
            if connection != sender:
                await connection.send_text(message)
        await sender.send_text(message)  # Ensure the sender also receives the message
        logging.info(f"Broadcast message: {message}")

app = FastAPI()

manager = ConnectionManager()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'dialogflow_service_account.json'

DIALOGFLOW_PROJECT_ID = 'sarah-9dgy'
DIALOGFLOW_LANGUAGE_CODE = 'en'
dialogflow_client = dialogflow.SessionsClient()

@app.get("/customer")
async def get_customer():
    return FileResponse('customer.html')

@app.get("/operator")
async def get_operator():
    return FileResponse('operator.html')


@app.get("/styles.css")
async def get_styles():
    return FileResponse('styles.css')

@app.websocket("/communicate/{client_id}/{role}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, role: str):
    await manager.connect(websocket, role)
    session = dialogflow_client.session_path(DIALOGFLOW_PROJECT_ID, client_id)
    
    if role == "customer":
        # Send welcome message from Dialogflow
        await send_welcome_message(websocket, session)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if role == "customer":
                # Send message to Dialogflow
                await handle_customer_message(websocket, session, data, client_id)
            else:
                # Forward messages from operators to customers
                await manager.broadcast(f"Operator {client_id}: {data}", websocket)
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await manager.broadcast(f"{client_id} user has disconnected.", websocket)

async def send_welcome_message(websocket: WebSocket, session: str):
    """Send the welcome message from Dialogflow"""
    text_input = dialogflow.TextInput(text="Welcome", language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text_input)
    response = dialogflow_client.detect_intent(session=session, query_input=query_input)
    logging.info(response)
    await manager.send_personal_message(response.query_result.fulfillment_text, websocket)

async def handle_customer_message(websocket: WebSocket, session: str, data: str, client_id: int):
    """Handle messages from the customer"""
    text_input = dialogflow.TextInput(text=data, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text_input)
    response = dialogflow_client.detect_intent(session=session, query_input=query_input)
    logging.info(response)
    logging.info(response)

    await manager.send_personal_message(f"You: {data}", websocket)
    await manager.send_personal_message(response.query_result.fulfillment_text, websocket)
    
    logging.info(f"Intent detected: {response.query_result.intent.display_name}")
    if response.query_result.intent.display_name in ['Operator Request', 'chat_with_both']:
        await manager.send_personal_message("Connecting you with an operator...", websocket)
        await connect_with_human(websocket, client_id, "customer", session)

async def connect_with_human(websocket: WebSocket, client_id: int, role: str, session: str):
    await manager.send_personal_message("Connected with a human operator...", websocket)
    await manager.broadcast(f"Customer {client_id} connect with an operator.", websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            if role == "operator":
                message = f"Operator {client_id}: {data}"
                await manager.broadcast(message, websocket)
            else:
                message = f"Customer {client_id}: {data}"
                await manager.broadcast(message, websocket)
                
                # Check if the intent is to continue chatting with both
                text_input = dialogflow.TextInput(text=data, language_code=DIALOGFLOW_LANGUAGE_CODE)
                query_input = dialogflow.QueryInput(text=text_input)
                response = dialogflow_client.detect_intent(session=session, query_input=query_input)
                
                if response.query_result.intent.display_name != 'chat_with_both':
                    break
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await manager.broadcast(f"{client_id} user has disconnected.", websocket)
