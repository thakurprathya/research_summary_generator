import os
import requests
import ollama
from bs4 import BeautifulSoup as bs
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
search_key = os.getenv('GOOGLE_SEARCH_API_KEY').encode('utf-8')
engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID').encode('utf-8')
rapidapi_key = os.getenv('RAPID_API_KEY').encode('utf-8')
rapidapi_host = os.getenv('RAPID_API_HOST').encode('utf-8')
groq_key = os.getenv('GROQ_API_KEY')
model = "llama3.1:8b"

def get_publication_link(name: str, publication_title: str) -> str:
    try:
        print('getting publication link...')
        query = f"{name} {publication_title}"

        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            'key': search_key, 
            'cx': engine_id,
            'q': query
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        if "items" in results:
            first_link = results["items"][0]["link"]
            return first_link
        else:
            print("No search results found.")
            return ""
    except Exception as e:
        print(f"Error in get_publication_link: {str(e)}")
        return ""

def get_scrape_body(publication_link: str) -> str:
    try:
        print('getting scraped data...')
        url = "https://scrapingbee.p.rapidapi.com/"
        querystring = {"url":publication_link, "render_js":"true"}  # render_js: true for fetching through chrome headless browser
        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": rapidapi_host
        }
        response = requests.get(url, headers=headers, params=querystring)
        return response.json()
    except Exception as e:
        print(f"Error in getScrapeBody: {str(e)}")
        return ""

def parse_page_content(scrape_body: str) -> str:
    try:
        print('getting parsed body...')
        soup = bs(scrape_body, 'html.parser')
        
        # Remove all script and style elements
        for element in soup(['script', 'style', 'head', 'title', 'meta', '[document]']):
            element.decompose()

        text = soup.get_text() # Get text content
        lines = (line.strip() for line in text.splitlines()) # Break text into lines and remove leading/trailing whitespace
        chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # Remove empty lines and join into chunks
        text = ' '.join(chunk for chunk in chunks if chunk) # Join chunks with single space and remove empty chunks
        text = ' '.join(text.split()) # Remove extra whitespace

        return text
    except Exception as e:
        print(f"Error in parse_page_content: {str(e)}")
        return ""

def get_abstract_and_journal(publication_link: str) -> str:
    try:
        scrape_body = get_scrape_body(publication_link)
        content_body = parse_page_content(scrape_body)
        print('getting abstract...')
        # limiting content size for context window
        limit = 70000
        if len(content_body) > limit:
            content_body = content_body[:limit]
        
        client = Groq(api_key=groq_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a scientific summarizer. Your task is to create a concise and informative abstract for a research paper based on the following content scraped from a publication site. Focus on the main objectives, methods, key findings, and conclusions. The summary should be approximately 150-200 words long. The output must not contain any stylized formatting (like markdown) and must only provide a summary in one paragraph without any sort of introduction or ending. Here's the content to summarize."
                },
                {
                    "role": "user",
                    "content": content_body,
                }
            ],
            model="llama-3.1-8b-instant",
        )
        abstract = chat_completion.choices[0].message.content

        print('getting journal...')
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful title maker. You can read a summary of a research paper and give it an appropriate journal title. A journal title is used to give a proper definition of the field the research paper is written on. For example: 'Journal of Robotics'. You must provide only a very short title of journal in your output without any introduction or ending but only the journal. Here's the summary:"
                },
                {
                    "role": "user",
                    "content": abstract
                }
            ],
            model="llama3-8b-8192"
        )
        journal = chat_completion.choices[0].message.content

        return (abstract, journal)
    except Exception as e:
        print(f"Error in getAbstract: {str(e)}")
        return ("", "")

if __name__ == "__main__":
    print('working...')
    # Testing Publication Link
    # name = "Dr. Ashish Khanna"
    # title = "Blockchain and FL-Based Secure Architecture for Enhanced External Intrusion Detection in Smart Farming"
    # result = get_publication_link(name, title)
    # print(f"Found link: {result}")

    # Testing Scraping
    # url = "https://onlinelibrary.wiley.com/doi/10.1155/2021/5579148"
    # scrape_body = get_scrape_body(url)
    # with open('./services/functions/scrape_body.txt', 'w', encoding='utf-8') as file:
    #     file.write(scrape_body)

    # Testing Parsing
    # scrape_body = ""
    # with open('./services/functions/scrape_body.txt', 'r', encoding='utf-8') as file:
    #     scrape_body = file.read()
    # content = parse_page_content(scrape_body)
    # with open('./services/functions/content.txt', 'w', encoding='utf-8') as file:
    #     file.write(content)