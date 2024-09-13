import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from fpdf import FPDF
 
import os
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
 
 
import requests
import os
 
from dotenv import load_dotenv
 
load_dotenv()
 
 
api_token = os.environ['confluence_api_token']
# print(api_token)
 
 
 
def get_confluence_data(api_token):
    # Confluence API details
    confluence_folder_url = 'https://aris-ziffity.atlassian.net/wiki/rest/api/content/2674819117/child/page?expand=body.view'
    email = 'manikumar.ramakrishna@ziffity.com'
   



    response = requests.get(
        confluence_folder_url,
        auth=HTTPBasicAuth(email, api_token)
    )
 
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        pages = []
 
        # Create the 'data' folder if it doesn't exist
        data_folder = "data"
        os.makedirs(data_folder, exist_ok=True)
 
        # Iterate through the pages and store each one as a text file
        for idx, page in enumerate(data.get('results', [])):
            page_title = page['title']
            page_content = page['body']['view']['value']
           
            # Parse the HTML content using BeautifulSoup to extract plain text
            soup = BeautifulSoup(page_content, 'html.parser')
            text = soup.get_text()
 
            # Add the page details to the pages list
            pages.append({
                'title': page_title,
                'content': text
            })
 
            # Save the page content as a text file
            file_path = os.path.join(data_folder, f"confluence_page_{idx}.txt")
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(f"Title: {page_title}\n\n{text}")
 
        return pages  # Return the pages as well for further use if needed
    else:
        return f"Failed to retrieve content. Status code: {response.status_code}"
 

content = get_confluence_data(api_token)

if isinstance(content, list):
    print("Confluence data successfully retrieved and stored in the 'data' folder.")
else:
    print(content)
 
 
# pdf = FPDF()
# pdf.add_page()
# pdf.set_font("Arial", size=12)
 
# # Add content to PDF
# pdf.multi_cell(0, 10, )
 
# # Save PDF to file
# pdf_output = "data/confluence_page.pdf"
# pdf.output(pdf_output)
 
# print(f"PDF created successfully and saved as {pdf_output}")
# # for i in data['results']:
   
#     for j in i:
#         if j == 'id':
#             print(f"this is id {i[j]}")
#             page_id = i[j]  # Extract the page id
#             confluence_page_url = f'https://aris-ziffity.atlassian.net/wiki/rest/api/content/{page_id}?expand=body.storage'  # Construct the page URL dynamically
           
#             response = requests.get(
#                 confluence_page_url,
#                 auth=HTTPBasicAuth(email, api_token)
#             )
 
#             # Check if the request was successful
#             if response.status_code == 200:
#                 page_data = response.json()
#                 print("Page Content:")
#                 print(page_data)  # You can access specific parts here
#                 # print(page_data.get('body', {}).get('storage', {}).get('value', ''))
#             else:
#                 print(f"Failed to retrieve content. Status code: {response.status_code}")
 
 
 
 
 
#  for result in data.get('results', []):
#         page_id = result.get('id')
#         print(f"Fetching content for Page ID: {page_id}")
#         fetch_page_content(page_id)