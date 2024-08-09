from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import dialogflow_v2 as dialogflow
import os

class ConnectionManager:
    """Class defining socket events"""
    def __init__(self):
        """init method, keeping track of connections"""
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """connect event"""
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        """disconnect event"""
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Direct Message"""
        await websocket.send_text(message)

    async def broadcast(self, message: str, sender: WebSocket):
        """Broadcast message to all connections except the sender"""
        for connection in self.active_connections:
            if connection != sender:
                await connection.send_text(message)

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

@app.websocket("/communicate/{client_id}/{role}")
async def websocket_endpoint(websocket: WebSocket,client_id :int,role:str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if role == "operator":
                message = f"{client_id} operator : {data}"
            else :
                message  = f"{client_id} customer : {data}"
            await manager.send_personal_message(f"you : {data}", websocket)
            await manager.broadcast(message, websocket)

            
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await manager.broadcast(f"{client_id} , user has disconnected.", websocket)


async def send_message_to_operator(data, websocket):
    await manager.broadcast()

    
    
    

