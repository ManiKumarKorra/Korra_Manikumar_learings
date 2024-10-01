from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
import os
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings  # Correct import
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form, HTTPException, Request, Response
from passlib.context import CryptContext
import mysql.connector
import uuid
from typing import Optional
from datetime import datetime, timedelta


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

os.environ['OPENAI_API_KEY'] = openai_api_key


class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=True)
    
    def embed_query(self, text):
        return self.model.encode([text])[0]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin123",
        database="rag"
    )

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_session():
    return str(uuid.uuid4())

def get_user_from_session(session_id: str):
    session = sessions.get(session_id)
    print(f"Checking session for ID: {session_id}, found session: {session}")
    print(session["user"]["role"])
    
    if session and session['expiry'] > datetime.now():
        return session['user']
    return None


@app.get("/")
def get_index():
    return FileResponse('register.html')

@app.get("/login")
def get_login():
    return FileResponse('login.html')

@app.post("/register")
async def register(
    fname: str = Form(...),
    lname: str = Form(...),
    role: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    hashed_password = hash_password(password)

    # SQL command to insert data into the table
    insert_sql = """
    INSERT INTO registration (fname, lname, role, email, password)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (fname, lname, role, email, hashed_password)

    try:
        cursor.execute(insert_sql, values)
        connection.commit()
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        cursor.close()
        connection.close()

    return {"status": "Registration successful"}

@app.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    response: Response = Response()
):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Execute the query to get the user with the given email
        query = "SELECT * FROM registration WHERE email = %s"
        cursor.execute(query, (email,))
        
        # Fetch the user from the database
        user = cursor.fetchone()

        if user is None or not verify_password(password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        session_id = create_session()
        sessions[session_id] = {
            'user': user,
            'expiry': datetime.now() + timedelta(hours=1)  # Session expires in 1 hour
        }

        response = RedirectResponse(url="/index", status_code=303)
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        
        return response

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    
    finally:
        # Always close the cursor and connection to avoid resource leaks
        cursor.close()
        connection.close()




@app.get("/profile")
async def get_profile(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_user_from_session(session_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {"user": user}

@app.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    
    if session_id in sessions:
        del sessions[session_id]
    
    response.delete_cookie(key="session_id")
    
    return RedirectResponse(url="/login", status_code=303)



import traceback

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def handle_query(request: QueryRequest, req: Request):
    try:
        session_id = req.cookies.get("session_id")
        
        if session_id is None:
            raise HTTPException(status_code=401, detail="Session ID not found. Please log in.")
        
        user = get_user_from_session(session_id)

        if user is None:
            raise HTTPException(status_code=401, detail="Session expired or invalid. Please log in.")
        
        user_role = user['role']
        user_fname = user['fname']
        user_lname = user['lname']
        user_id = user['id']
        
        print(f"User info: ID={user_id}, Role={user_role}, Name={user_fname} {user_lname}")

        embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        db = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)

        if db is None:
            print("Error loading FAISS index.")
            raise HTTPException(status_code=500, detail="Failed to load FAISS index.")

        llm = ChatOpenAI(model="gpt-3.5-turbo")

        # Define the prompt template
        prompt = ChatPromptTemplate.from_template("""
        You are an intelligent assistant providing responses to users based on their role. The user's role is {user_role}.
        
        - If the user is a **developer**, they have access to all technical information but not HR-related topics.
        - If the user is in **HR**, they have access to HR policies and guidelines but not technical details like llms , xgoast etc.
            if there is no context for the input dont not kindly Hallucinat anything just say i dont have enough information.. only provide with what there is context.
        
        Context:
        {context}

        Question: {input}

        Based on the user's role ({user_role}) and the relevance of the context to the question, provide an appropriate response.
        """)

        # Create the document chain and retrieval chain
        document_chain = create_stuff_documents_chain(llm, prompt) #im using langchain to load llm and prompt 
        retriever = db.as_retriever() #my retriver is fiass retirver 
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        # Log the query and user role before invoking the chain
        print(f"User role: {user_role}, Query: {request.query}")

        # Execute the chain with the user's input and role
        response = retrieval_chain.invoke({
            "input": request.query, 
            "user_role": user_role  
        })

        print(f"Retrieval chain response: {response}")

        bot_resposnse = response['answer']
        user_query = request.query

        connection = get_db_connection()
        mycursor = connection.cursor()

        print(f"Inserting: id={user_id}, fname={user_fname}, lname={user_lname}, role={user_role}, query={user_query}, response={bot_resposnse}")

        sql = "INSERT INTO user_data1 (id, fname, lname, role, user_query, bot_resposnse) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (user_id, user_fname, user_lname, user_role, user_query, bot_resposnse)
        mycursor.execute(sql, val)
        connection.commit()

        return {"response": bot_resposnse}

    except Exception as e:
        # Log the error and full traceback for better debugging
        print(f"Error occurred: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


from fastapi.templating import Jinja2Templates
from fastapi import Request, Response, HTTPException

templates = Jinja2Templates(directory="templates")

@app.get("/index")
async def get_index(request: Request):
    session_id = request.cookies.get("session_id")
    
    user = get_user_from_session(session_id)

    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    
    connection = get_db_connection()
    mycursor = connection.cursor()
    user_id = user['id']
    mycursor.execute("SELECT user_query, bot_resposnse FROM user_data1 WHERE id = %s LIMIT 3", (user_id,))

    myresult = mycursor.fetchall()


    return templates.TemplateResponse("index.html", {"request": request, "username": user['fname'], "role": user['role'], "conversation": myresult})


@app.get("/styles.css")
async def get_styles():
    return FileResponse('styles.css')


