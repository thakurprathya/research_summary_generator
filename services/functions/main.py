import requests
import ollama
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup as bs

# Define the llama model to be used for summary generation
model = "llama3.1:8b"

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
    
def getBodyScrape(links: list[str]) -> list[str]:
    """
    Takes list of links and returns text content for each link using Selenium with Chrome.
    """
    try:
        options = Options()
        options.headless = True
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        driver = webdriver.Chrome(options=options)

        content = []
        for link in links:
            driver.get(link)
            soup = bs(driver.page_source, 'html.parser')
            text = ' '.join(soup.stripped_strings)
            content.append(text)

        driver.quit()
        return content
    except Exception as e:
        print(f"Error: {e}")
        return []
        
def getAbstract(sites: list) -> list:
    abstracts = []
    prompt = "You are a scientific summarizer. Your task is to create a concise and informative abstract for a research paper based on the following content scraped from a publication site. Focus on the main objectives, methods, key findings, and conclusions. The summary should be approximately 150-200 words long. Here's the content to summarize:\n\n"
    
    for data in sites:
        response = ollama.chat(model=model, messages=[{
                'role': 'user',
                'content': prompt+data
            }])
        ollamaResponse = response['message']['content']
        abstracts.append(ollamaResponse)
        with open("output_summary.txt", "a+", encoding="utf-8") as f:
            f.write(ollamaResponse)
    return abstracts

def getProfile(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Takes in pandas dataframe and returns faculty's profile of research papers as dataframe
    """
    try:
        name = df.iloc[1:, 0].tolist()
        year = df.iloc[1:, 1].tolist()
        title = df.iloc[1:, 2].tolist()
        
        links = getLinks(name, title)
        if(links):
            bodyScrape = getBodyScrape(links)
            if(bodyScrape):
                abstracts = getAbstract(bodyScrape)
                if(abstracts):
                    dfOutput = pd.DataFrame({
                        "name": [name] * len(title),
                        "year": year,
                        "title": title,
                        "link": links,
                        "abstract": abstracts
                    })
                    uniqueId = str(int(time.time()))
                    dfOutput.to_excel(f'{uniqueId}.xlsx', index=False)
                    return dfOutput
                else:
                    raise Exception("LLAMA ERROR :: Couldn't generate summary")
            else:
                raise Exception("API ERROR :: Couldn't fetch body content from links")
        else:
            raise Exception("API ERROR :: Couldn't fetch links from google")
            
    except Exception as e:
        printErr(e)
        return None

if __name__ == '__main__':
    path = "../../static/assets/demo.xlsx"
    df = pd.read_excel(path)
    getProfile(df)