import requests
import pandas as pd
import os
from bs4 import BeautifulSoup as bs

def printErr(e: Exception) -> None:
    print("ERROR :: ", e)

def getLinks(name: str, research_papers: str) -> list:
    """
    Takes name of the faculty member and title of their research papers and returns the links for publications of those research papers
    """
    try:
        links = []
        for paper in research_papers:
            query = f"{name} {paper}"
            url = f"https://www.google.com/search?q={query}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers)
            soup = bs(response.text, 'html.parser')
            search_results = soup.find_all('div', class_='yuRUbf')
            if search_results:
                first_link = search_results[0].find('a')['href']
                links.append(first_link)
            
        return links
    except Exception as e:
        printErr(e)
        return []
    
def getBodyScrape(links: list) -> list:
    """
    Takes list of links and returns abstract for each link
    """
    try:
        abstracts = []
        for link in links:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            req = requests.Session()
            response = req.get(link, headers=headers)
            soup = bs(response.text, 'html.parser')
            abstract = ' '.join(soup.stripped_strings)
            abstracts.append(abstract)
        return abstracts
    except Exception as e:
        printErr(e)
        return []
        
def getAbstract(content: list) -> list:
    # TODO: Use Ollama to generate summaries
    return []

def getProfile(path: str) -> list:
    """
    Takes path for excel sheet and returns faculty's profile of research papers
    """
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
    try:
        df = pd.read_excel(path)
    except Exception as e:
        printErr(e)
        return []
    
    try:
        faculty_list = df.iloc[1:, 2].tolist()
        name = df.iloc[1, 0]
        
        links = getLinks(name, faculty_list)
        if(links):
            bodyScrape = getBodyScrape(links)
            if(bodyScrape):
                abstracts = getAbstract(bodyScrape)
                if(abstracts):
                    return abstracts
                    print(abstracts)
                else:
                    raise Exception("LLAMA ERROR :: Couldn't generate summary")
            else:
                raise Exception("API ERROR :: Couldn't fetch body content from links")
        else:
            raise Exception("API ERROR :: Couldn't fetch links from google")
            
    except Exception as e:
        printErr(e)
        return []

getProfile("../../static/assets/demo.xlsx")