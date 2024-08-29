from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Enable CORS for all origins (adjust as needed for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data model for the POST request
class QueryRequest(BaseModel):
    query: str

@app.get("/")
def get_index():
    return FileResponse('index.html')

@app.get("/styles.css")
async def get_styles():
    return FileResponse('styles.css')


@app.post('/upload')
async def handle_file(file: UploadFile = File(...)):
    upload_folder = "data"
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, file.filename)
    
    try:
        # Save the file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Re-index the data
        PERSIST_DIR = "./storage"
       

        
        documents = SimpleDirectoryReader("data").load_data()
        index = VectorStoreIndex.from_documents(documents)
        # store it for later
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        
        print("sucess")

        return {"filename": file.filename, "message": "File uploaded and indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

@app.post("/query")
def handle_query(request: QueryRequest):
    PERSIST_DIR = "./storage"
    
    if not os.path.exists(PERSIST_DIR):
        # Load the documents and create the index
        documents = SimpleDirectoryReader("data").load_data()
        index = VectorStoreIndex.from_documents(documents)
        # Store it for later
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        # Load the existing index
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)

    # Query the index
    query_engine = index.as_query_engine()
    response = query_engine.query(request.query)

    print(f"Received query: {request.query}")  # Debug statement
    print(f"Response: {response.response}")  # Debug statement

    return {"response": response.response}
