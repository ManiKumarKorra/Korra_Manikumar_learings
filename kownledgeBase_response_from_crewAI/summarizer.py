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
