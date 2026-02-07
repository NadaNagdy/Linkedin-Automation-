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
            title = a.text.strip()
            link_tag = a.find('a')
            link = link_tag['href'] if link_tag else tc_url
            trends.append({"title": f"Tech (Health): {title}", "url": link})
    except Exception as e:
        print(f"Error scraping TechCrunch: {e}")

    # 2. سحب عناوين من PubMed (أحدث الأبحاث)
    try:
        base_url = "https://pubmed.ncbi.nlm.nih.gov"
        pubmed_url = f"{base_url}/?term=public+health&sort=date"
        res = requests.get(pubmed_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = soup.find_all('a', class_='docsum-title', limit=3)
        for a in articles:
            title = a.text.strip()
            link = f"{base_url}{a['href']}"
            trends.append({"title": f"Research (PubMed): {title}", "url": link})
    except Exception as e:
        print(f"Error scraping PubMed: {e}")

    return trends
