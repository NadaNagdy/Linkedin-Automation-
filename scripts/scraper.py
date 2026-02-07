import requests
from bs4 import BeautifulSoup

def fetch_trends():
    trends = []
    
    # 1. سحب أخبار من TechCrunch Health
    try:
        tc_url = "https://techcrunch.com/category/health/"
        res = requests.get(tc_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = soup.find_all('h2', class_='loop-card__title', limit=3)
        for a in articles:
            trends.append(f"Tech (Health): {a.text.strip()}")
    except Exception as e:
        print(f"Error scraping TechCrunch: {e}")

    # 2. سحب عناوين من PubMed (أحدث الأبحاث)
    try:
        pubmed_url = "https://pubmed.ncbi.nlm.nih.gov/?term=public+health&sort=date"
        res = requests.get(pubmed_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = soup.find_all('a', class_='docsum-title', limit=3)
        for a in articles:
            trends.append(f"Research (PubMed): {a.text.strip()}")
    except Exception as e:
        print(f"Error scraping PubMed: {e}")

    return trends
