from crewai import Crew
from dotenv import load_dotenv
from agents import web_researcher_agent, doppelganger_agent
from tasks import web_research_task, create_linkedin_post_task
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Load environment variables
load_dotenv()

# Initialize Crew with agents and tasks
crew = Crew(
    agents=[
        web_researcher_agent,
        doppelganger_agent
    ],
    tasks=[
        web_research_task,
        create_linkedin_post_task
    ]
)

# Kickoff the crew tasks and capture the result
result = crew.kickoff()

# Print the result
print("Here is the result: ")
print(result)

# Function to save the result as a PDF file
def save_result_as_pdf(result, file_path):
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 100, "Crew AI Task Result")
    text = c.beginText(100, height - 120)
    text.setFont("Helvetica", 10)
    
    for line in result.split('\n'):
        text.textLine(line)
    
    c.drawText(text)
    c.save()

# Define the file path
file_path = "crew_result.pdf"

# Save the result as a PDF
save_result_as_pdf(str(result), file_path)

print(f"Result saved as PDF file at: {file_path}")
