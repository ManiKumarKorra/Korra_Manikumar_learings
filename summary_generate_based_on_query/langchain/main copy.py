from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings  # Correct import

# Load environment variables
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

os.environ['OPENAI_API_KEY'] = openai_api_key

# Define the SentenceTransformerEmbeddings class
class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=True)
    
    def embed_query(self, text):
        return self.model.encode([text])[0]

# FastAPI app initialization
app = FastAPI()

# Enable CORS for all origins (adjust as needed for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the input model for the query
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def handle_query(request: QueryRequest):
    try:
        # Load the FAISS index and SentenceTransformer model
        embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        db = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)

        # Initialize the language model (use gpt-3.5-turbo for faster response time)
        llm = ChatOpenAI(model="gpt-3.5-turbo")

        # Define the prompt template
        prompt = ChatPromptTemplate.from_template(""" 
        Please provide a factually accurate response based only on the information provided in the context. Do not speculate or provide information that is not included in the context. If the context does not contain the necessary information to answer the question, respond with "I don't have enough information to answer."

        Context:
        {context}

        Question: {input}""")

        # Create the document chain
        document_chain = create_stuff_documents_chain(llm, prompt)

        # Setup the retriever
        retriever = db.as_retriever()

        # Create the retrieval chain
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        # Execute the chain with the user's input
        response = retrieval_chain.invoke({"input": request.query})

        # Return the response back to the frontend
        return {"response": response['answer']}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def get_index():
    return FileResponse('index.html')

@app.get("/styles.css")
async def get_styles():
    return FileResponse('styles.css')