import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def scrape_google_news(search_text):
    geo_location = "IN"
    host_language = "en"
    """
    Scrape Google News based on the search query provided by the user.

    Args:
        search_text (str): The search query to find news articles.

    Returns:
        list: A list of dictionaries containing the news data.
    """
    # Replace spaces with "+" for URL encoding
    search_query = search_text.replace(" ", "+")
    url = f"https://news.google.com/search?q={search_query}&gl={geo_location}&hl={host_language}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract news articles
    articles = []
    for i, item in enumerate(soup.find_all("article")):
        if i >= 10:  # Limit to 10 items
            break
        try:

            title = item.find("div").get_text() if item.find("div") else "No Title"
            link = item.find("a")["href"] if item.find("a") else "No Link"
            link = f"https://news.google.com{link[1:]}" if link.startswith('.') else link
            source = item.find("time")["datetime"] if item.find("time") else "Unknown"
            articles.append({
                "headline": title,
                "url": link,
                "source": (
                    datetime.strptime(source, "%Y-%m-%dT%H:%M:%SZ").strftime("%d-%b-%Y %H:%M:%S")
                    if source
                    else "Unknown"
                )
            })

        except Exception as e:
            print(f"Error processing article: {e}")
            continue

    return articles


def save_to_json(data, filename="news_search_results.json"):
    """
    Save the extracted data to a JSON file.

    Args:
        data (dict): The data to save in JSON format.
        filename (str): The name of the output file.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}.")


if __name__ == "__main__":
    # Prompt user for search text
    search_text = input("Enter your search text: ")

    # Scrape news based on the search query
    print(f"Fetching news articles for: {search_text}...")
    news_data = scrape_google_news(search_text)

    # Check if any data was fetched
    if news_data:
        save_to_json({"news": news_data})
        print(json.dumps(news_data, indent=4))
        print(f"News articles for '{search_text}' successfully saved!")
    else:
        print("No news articles found or an error occurred.")
