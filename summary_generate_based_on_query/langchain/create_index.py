import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
import logging


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")
os.environ['OPENAI_API_KEY'] = openai_api_key

# Logging setup for tracking progress
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

#
class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=True)
    
    def embed_query(self, text):
        return self.model.encode([text])[0]

# Path to the data folder
folder_path = "data"

docs = []

logging.info(f"Loading documents from {folder_path}...")
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    

    if filename.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
        docs.extend(loader.load())
        logging.info(f"Loaded PDF: {filename}")
        
    
    elif filename.endswith('.txt'):
        loader = TextLoader(file_path)
        docs.extend(loader.load())
        logging.info(f"Loaded text file: {filename}")


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
logging.info("Splitting documents into chunks...")
documents = text_splitter.split_documents(docs)


logging.info(f"Total number of chunks: {len(documents)}")


embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


logging.info("Creating FAISS index from document embeddings...")
faiss_index = FAISS.from_documents(documents, embedding_model)

# Save FAISS index locally
faiss_index.save_local("faiss_index")
logging.info("Indexing completed and saved successfully.")