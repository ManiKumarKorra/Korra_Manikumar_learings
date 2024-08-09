 

Setting Up the Virtual Environment and Running the Crew AI Task to send response to voiceflow  

Introduction 

This guide provides step-by-step instructions to set up a virtual environment, install the required packages, and run a Crew AI task that processes queries against a PDF document using crewai_tools and send response to voice flow  

Prerequisites 

Python 3.x installed on your system 

Basic understanding of Python 

A PDF document (mydetails.pdf) to serve as the knowledge base 

An .env file with the OpenAI API key 

Voice flow agent  

Steps 

1. Create a Project Directory 

Create a directory for your project and navigate into it. 

mkdir crew_ai_pdf_query 
cd crew_ai_pdf_query 
 

2. Create a Virtual Environment 

Create a virtual environment to manage your project dependencies. 

python -m venv venv 
 

3. Activate the Virtual Environment 

Activate the virtual environment. 

On Windows: 

venv\Scripts\activate 
 

On macOS/Linux: 

source venv/bin/activate 
 

4. Create a requirements.txt File 

Create a requirements.txt file with the following content: 

Flask 
python-dotenv 
crewai 
crewai-tools 
langchain-huggingface 
 

5. Install the Required Packages 

Install the packages listed in requirements.txt. 

pip install -r requirements.txt 
 

6. Set Up the Project Files 

Create the necessary project files: 

.env (for environment variables) 

mydetails.pdf (the PDF file to be queried) 

summary.py (if required for additional processing) 

7. Create the .env File 

Create a .env file and add your OpenAI API key: 

OPENAI_API_KEY=your_openai_api_key 
 

8. Create the summary.py File 

Create a summary.py file with the following content: 

from flask import Flask, request, jsonify 
import os 
from dotenv import load_dotenv 
from crewai import Crew, Agent, Task 
from crewai_tools import PDFSearchTool 
import traceback 
 
# Load API key from .env file 
load_dotenv() 
api_key = os.getenv('OPENAI_API_KEY') 
 
# Initialize Flask app 
app = Flask(__name__) 
 
# Initialize the PDFSearchTool 
pdf_path = 'mydetails.pdf'  # Replace with your PDF file path 
tool = PDFSearchTool(pdf=pdf_path) 
 
# Define the function to handle the PDF query 
def handle_pdf_query(query: str): 
    """Use the PDFSearchTool to extract relevant information based on a query from a PDF.""" 
    answer = tool.query(query) 
    return answer 
 
# Define an agent to process the PDF 
pdf_agent = Agent( 
    role='PDF Query Processor', 
    goal='Retrieve information based on a query from a PDF using PDFSearchTool', 
    backstory='Specializes in semantic search within PDF documents', 
    verbose=True, 
    tools=[tool], 
    allow_delegation=False 
) 
 
# Define a task using the agent 
def pdf_query_task(query): 
    return Task( 
        description=f"Query PDF for: '{query}'", 
        expected_output="Relevant information to the query extracted from the PDF.", 
        execute=lambda: handle_pdf_query(query), 
        agent=pdf_agent 
    ) 
 
# Define the Flask route for Voiceflow integration 
@app.route('/query', methods=['POST']) 
def query_pdf(): 
    try: 
        data = request.get_json() 
        print("Received data:", data)  # Log incoming data 
        query = data.get('query') 
        print("Query:", query)  # Log the query 
 
        if not query: 
            return jsonify({"error": "No query provided"}), 400 
 
        # Setting up the crew with the task 
        task = pdf_query_task(query) 
        crew = Crew(agents=[pdf_agent], tasks=[task], verbose=2) 
 
        # Running the crew 
        crew.kickoff() 
 
        # Capture the result 
        result = task.output 
        print("Task result:", result)  # Log the result 
 
        # Ensure the result is serializable 
        if not isinstance(result, str): 
            result = str(result) 
 
        # Return the results 
        return jsonify({"result": result}) 
    except Exception as e: 
        print("An error occurred:", str(e)) 
        print(traceback.format_exc()) 
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500 
 
if __name__ == "__main__": 
    app.run(port=3000) 
 

9. Running the Application 

To run the Flask application, use the following command: 

python summary.py 
 

Your Flask app should now be running on http://localhost:3000. You can send POST requests to this endpoint to query the PDF document. 

 

10. Expose the Application to the Public using ngrok or Local Tunnel 

Install Local Tunnel 

npm install -g localtunnel 
 

Connect to the Tunnel Server 

lt --port 3000 
 

11. Configure the Voiceflow Agent 

Navigate to the developer section in Voiceflow. 

Go to the API configuration. 

Paste your URL from localtunnel in the API URL field, and select POST method followed by /query. 

Example: https://four-dogs-drum.loca.lt/query 

In the Body section, select raw and add the following JSON: 

json 

Copy code 

{ 
  "query": "{last_utterance}" 
} 
 

Now it should work. 

 