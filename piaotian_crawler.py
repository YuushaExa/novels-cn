# -*- coding: utf-8 -*-
import json
import os
import re
import time
import logging
from lncrawl.core.crawler import Crawler
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

class PiaoTianCrawler(Crawler):
    base_url = [
        "https://www.piaotian.com",
        "https://www.ptwxz.com",
        "https://www.piaotia.com",
    ]
    
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.piaotia.com",
        "Referer": "https://www.piaotia.com/modules/article/search.php",
    }

    def __init__(self):
        super().__init__()
        self.home_url = self.base_url[2]  # Default to piaotia.com

    def search_novel(self, query):
        encoded_query = urllib.parse.quote(query.encode("gbk"))
        search = urllib.parse.quote(" 搜 索 ".encode("gbk"))
        data = f"searchtype=articlename&searchkey={encoded_query}&Submit={search}"
        
        self.headers["Origin"] = self.home_url
        self.headers["Referer"] = f"{self.home_url}/modules/article/search.php"

        logger.info(f"Searching for: {query}")
        response = self.post_response(
            f"{self.home_url}/modules/article/search.php",
            headers=self.headers,
            data=data,
        )
        soup = self.make_soup(response, "gbk")

        results = []
        if response.url.startswith(f"{self.home_url}/bookinfo/"):
            # Single result case
            title = soup.select_one("div#content table table table h1").text.strip()
            author = soup.select('div#content table tr td[width]')[2].text
            author = author.replace(u'\xa0', "").replace("作 者：", "").strip()
            results.append({
                "title": title,
                "url": response.url,
                "author": author,
                "source": self.home_url
            })
        else:
            # Multiple results case
            for row in soup.select("div#content table tr")[1:]:
                cells = row.select("td")
                if len(cells) >= 3:
                    results.append({
                        "title": cells[0].text.strip(),
                        "url": cells[0].select_one("a")["href"],
                        "author": cells[2].text.strip(),
                        "source": self.home_url
                    })
        return results

    def get_novel_details(self, url):
        """Get full novel details including chapters"""
        self.novel_url = url
        self.read_novel_info()
        
        return {
            "title": self.novel_title,
            "author": self.novel_author,
            "cover": self.novel_cover,
            "chapter_count": len(self.chapters),
            "chapters": [{
                "id": chap["id"],
                "title": chap["title"],
                "url": chap["url"]
            } for chap in self.chapters[:10]]  # First 10 chapters only
        }

def save_results(query, data, folder="results"):
    """Save data to JSON file with query-based filename"""
    os.makedirs(folder, exist_ok=True)
    safe_name = sanitize_filename(query)
    filename = f"{folder}/{safe_name}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved results to {filename}")
    return filename

def main():
    import sys
    queries = ["斗破苍穹", "凡人修仙传"]  # Default queries
    
    # Use command-line arguments if provided
    if len(sys.argv) > 1:
        queries = sys.argv[1:]
    
    crawler = PiaoTianCrawler()
    
    for query in queries:
        try:
            logger.info(f"Processing query: {query}")
            
            # 1. Perform search
            results = crawler.search_novel(query)
            if not results:
                logger.warning(f"No results found for: {query}")
                continue
                
            # 2. Save search results
            search_results_file = save_results(
                f"{query}_search_results",
                {"query": query, "results": results}
            )
            
            # 3. Get details for first result
            first_result = results[0]
            details = crawler.get_novel_details(first_result["url"])
            details_file = save_results(
                f"{query}_{sanitize_filename(first_result['title'])}_details",
                details
            )
            
            # 4. Add delay between requests
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"Failed to process {query}: {str(e)}")
            continue

if __name__ == "__main__":
    main()
