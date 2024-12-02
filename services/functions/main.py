import os
import requests
import ollama
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

load_dotenv()
search_key = os.getenv('GOOGLE_SEARCH_API_KEY').encode('utf-8')
engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID').encode('utf-8')
model = "llama3.1:8b"

def get_publication_link(name: str, publication_title: str) -> str:
    try:
        query = f"""
        {name} {publication_title} 
        (site:scholar.google.com OR 
        site:academia.edu OR 
        site:arxiv.org OR 
        site:sciencedirect.com OR 
        site:ieee.org OR 
        site:pubmed.ncbi.nlm.nih.gov OR
        site:dblp.org OR
        site:m.x-mol.net OR
        site:researchgate.net)"""
        
        query = " ".join(query.split())
        print(f"Query: {query}")

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = requests.Session()
        response = req.get(publication_link, headers=headers)
        soup = bs(response.text, 'html.parser')
        scraped_text = ' '.join(soup.stripped_strings)
        return scraped_text
    except Exception as e:
        print(f"Error in getScrapeBody: {str(e)}")
        return ""

def get_abstract(publication_link: str) -> str:
    try:
        body_content = get_scrape_body(publication_link)

        prompt = (
            "You are a scientific summarizer. Your task is to create a concise and informative abstract for a research paper "
            "based on the following content scraped from a publication site. Focus on the main objectives, methods, key findings, "
            "and conclusions. The summary should be approximately 150-200 words long. Here's the content to summarize:\n\n"
        )
        full_prompt = prompt + body_content

        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': full_prompt}]
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error in getAbstract: {str(e)}")
        return ""

if __name__ == "__main__":
    name = "Dr. Ashish Khanna"
    title = "Enhancing fault detection and predictive maintenance of rotating machinery with Fiber Bragg Grating sensor and machine learning techniques"
    result = get_publication_link(name, title)
    print(f"Found link: {result}")