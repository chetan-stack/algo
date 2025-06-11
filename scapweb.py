import requests
from bs4 import BeautifulSoup
import json

# URL of the page to scrape
url = 'https://www.screener.in/company/RELIANCE/consolidated/'

# Fetch the HTML content of the page
response = requests.get(url)
html_content = response.text

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Function to extract text content based on ID
def extract_text_by_id(soup, element_id):
    element = soup.find(id=element_id)
    if element:
        return element.get_text(strip=True)  # Extracts the plain text, removes extra spaces
    else:
        return f"Element with ID {element_id} not found."

# Function to extract text content based on class
def extract_text_by_class(soup, class_name):
    elements = soup.find_all(class_=class_name)
    if elements:
        return [element.get_text(strip=True) for element in elements]  # List of plain text
    else:
        return f"Elements with class {class_name} not found."

# Example: Extract text by ID and Class
id_text = extract_text_by_id(soup, 'top')  # Replace 'yourId' with the actual ID
class_text = extract_text_by_class(soup, 'card card-large')  # Replace 'yourClass' with the actual class

# Organize extracted data into a dictionary
data = {
    "id_text": id_text,
    "class_text": class_text
}

# Save the extracted text content to a JSON file
with open('extracted_text.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Print the extracted data (optional)
print(json.dumps(data, indent=4))
