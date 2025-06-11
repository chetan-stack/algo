import requests
from bs4 import BeautifulSoup


# Function to extract data from multiple tables
def extract_all_tables(soup):
    all_table_data = []

    # Find all tables with the class 'ranges-table'
    tables = soup.find_all("table", class_="ranges-table")
    # Loop through each table
    for table in tables:
        table_data = {}

        # Extract the header (if it exists)
        header = table.find("th", colspan="2")
        table_data["header"] = header.get_text(strip=True) if header else "Unknown"

        # Extract rows
        rows = table.find_all("tr")[1:]  # Skip the first row (header row)
        table_content = {}

        # Extract data from each row
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:  # Ensure row has two columns
                period = cols[0].get_text(strip=True)
                value = cols[1].get_text(strip=True)
                table_content[period] = value

        table_data["content"] = table_content
        all_table_data.append(table_data)

    return all_table_data


def fetch_screener_data(url):
    """
    Fetches and extracts data from the Screener.in company page.

    Args:
        url (str): The Screener.in URL for a specific company.

    Returns:
        dict: A dictionary containing extracted data.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.90 Safari/537.36"
    }

    try:
        # Send a GET request
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": f"Failed to fetch the page. Status code: {response.status_code}"}

        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract key data (Example: Company name, market cap, etc.)
        data = {}

        # Example: Extracting company name
        company_name = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Unknown"
        data["company_name"] = company_name

        # Example: Extracting market cap (modify selector as per actual page structure)
        market_cap = soup.find("span", text="Market Cap").find_next("span").get_text(strip=True) if soup.find("span",
                                                                                                              text="Market Cap") else "Unknown"
        data["market_cap"] = market_cap

        ul_elements = soup.find_all("div", class_="company-ratios")
        # ul_elements = soup.find_all("ul")
        # Extract Pros and Cons sections
        procons = {}

        # Extract Pros and Cons sections
        pros_section = soup.find("div", class_="pros")
        cons_section = soup.find("div", class_="cons")

        # Extract Pros
        if pros_section:
            pros_list = [li.get_text(strip=True) for li in pros_section.find_all("li")]
            procons["pros"] = pros_list

        # Extract Cons
        if cons_section:
            cons_list = [li.get_text(strip=True) for li in cons_section.find_all("li")]
            procons["cons"] = cons_list

        ul_li_data = []
        for ul in ul_elements:
            ul_dict = {
                "ul_text": ul.get_text(strip=True),  # Entire <ul> text
                "li_items": [li.get_text(strip=True).replace('\u20b9', ' - ') for li in ul.find_all("li")]
                # List of <li> texts
            }
            ul_li_data.append(ul_dict)

        # Add more fields as needed
        # Example: P/E ratio, ROE, etc.
        cons = {
            'data': data,
            'procons': procons,
            'ul_li_data': ul_li_data,
            'table': extract_all_tables(soup)
        }
        return cons

    except Exception as e:
        return {"error": str(e)}


def generateformat(data):
    # Generate formatted string
    formatted_string = f"""
  Company Name : {data['data']['company_name']}

  ### Pros:
  - {chr(10).join(data['procons']['pros'])}

  ### Cons:
  - {chr(10).join(data['procons']['cons'])}

  ### Key Ratios:
  - {chr(10).join(data['ul_li_data'][0]['li_items'])}

  ### Growth Metrics:
  """
    for table in data['table']:
        formatted_string += f"\n{table['header']}:\n"
        for key, value in table['content'].items():
            formatted_string += f"- {key} {value}\n"

    print(formatted_string)
    return formatted_string


def main(symbol):
    # URL to scrape
    url = f"https://www.screener.in/company/{symbol}/consolidated/"
    # Fetch and display data
    data = fetch_screener_data(url)
    format = generateformat(data)
    # print(json.dumps(data, indent=4))
    print(format)
    return format

# print(main('TCS'))
