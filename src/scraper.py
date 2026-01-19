from typing import List,Tuple
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re


def parse_star_tag(text:str) -> int:
        if not text:
             return 0
        stars = text.strip().lower().replace(',',"")
        try: 
           if 'k' in stars:
              stars = int(float(stars.replace("k",""))*1000)
              return stars   
           return int(float(stars))                    
        except Exception :
            stars_ = re.search(r"([\d\.]+)(k?)",stars)
            if stars_:
                num_part = stars_.group(1)
                suff_part = stars_.group(2)
                val = float(num_part)
                if suff_part=='k':
                    return int(val*1000)
                return int(val)
            return 0 

class GitHubScraper:
    def __init__(self,url:str,headers:dict = None):
        self.url = url
        self.headers = headers or {"User-Agent" : "Mozilla/5.0"}

    def scrape_trending(self) -> List[Tuple]:
        resp = requests.get(self.url,headers=self.headers,timeout=15)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch {self.url} : {resp.status_code}")
        soup = BeautifulSoup(resp.text,"html.parser")
        items = soup.find_all("article",class_="Box-row")
        repo_list=list()
        for item in tqdm(items,desc="Scraping repos"):
            a = item.find("h2")
            if a and a.find("a"):
                href = a.find("a").get("href","").strip()
                repo_name = href.strip("/").lstrip("/")
                # repo_name = href.replace("/"," ")
            else:
                repo_name = item.get_text(strip=True).split()[0]
        #  Star count
            star_tag = item.find("a",href=re.compile(r"/stargazers$"))
            stars = parse_star_tag(star_tag.get_text(strip=True)) if star_tag else 0
            repo_list.append((repo_name,stars))
        return repo_list
            