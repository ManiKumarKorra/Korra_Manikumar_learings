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




# Define the SentenceTransformerEmbeddings class
class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=True)
    
    def embed_query(self, text):
        return self.model.encode([text])[0]

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")
os.environ['OPENAI_API_KEY'] = openai_api_key

# Load the FAISS index from disk using the same SentenceTransformerEmbeddings model
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)

# Initialize the language model (use gpt-3.5-turbo for faster response time)
llm = ChatOpenAI(model="gpt-3.5-turbo")

# Define the prompt template
prompt = ChatPromptTemplate.from_template(""" 
just return the context as it is only correct grammer error. 
 AND dont hulicante the answer if there is no content  then just say i dont have information
<context>
{context}
</context>
Question: {input}""")

# Create the document chain
document_chain = create_stuff_documents_chain(llm, prompt)

# Setup the retriever
retriever = db.as_retriever()

# Create the retrieval chain
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# Get the input from the user
user_input = input("Please enter your query: ")

# Execute the chain with the user's input
response = retrieval_chain.invoke({"input": user_input})

# Print the final answer
print(response['answer'])
