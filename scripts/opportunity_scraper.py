import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_headers():
    # Rotate user agents to avoid detection
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/'
    }

def scrape_wuzzuf_jobs(query="medical", category="Job"):
    """Scrapes jobs/internships from Wuzzuf."""
    url = f"https://wuzzuf.net/search/jobs/?q={query.replace(' ', '+')}&a=hpb"
    print(f"Scraping Wuzzuf ({category}): {url}")
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        jobs = []
        job_cards = soup.find_all('div', class_='css-ghe2tq')
        
        if not job_cards:
            job_cards = soup.select('div.e1v1l3u10') 

        for card in job_cards:
            title_elem = card.select_one('h2 a')
            company_elem = card.select_one('div.css-1k5ee52 a') 
            location_elem = card.select_one('span.css-16x61xq')
            date_elem = card.select_one('div.css-eg55jf') 
            
            if title_elem:
                title = title_elem.text.strip()
                link = title_elem['href']
                company = company_elem.text.strip().rstrip(' -') if company_elem else "N/A"
                location = location_elem.text.strip() if location_elem else "N/A"
                date_posted = date_elem.text.strip() if date_elem else datetime.now().strftime("%Y-%m-%d")

                full_link = link if link.startswith('http') else f"https://wuzzuf.net{link}"
                
                # Check for "Just now", "Today", or "1 hour ago" to prioritize new items
                is_fresh = any(x in date_posted.lower() for x in ["now", "hour", "today", "minute"])
                
                jobs.append({
                    'title': f"[{category}] {title}", 
                    'company': company,
                    'location': location,
                    'link': full_link,
                    'date_posted': date_posted,
                    'source': 'Wuzzuf',
                    'is_fresh': is_fresh
                })
                
        logging.info(f"Scraped {len(jobs)} {category} from Wuzzuf")
        return jobs
    except Exception as e:
        logging.error(f"Error scraping Wuzzuf ({category}): {str(e)}")
        return []

def scrape_reliefweb_jobs(query="health", category="Job"):
    """Scrapes jobs/internships from ReliefWeb."""
    url = f"https://reliefweb.int/jobs?search={query.replace(' ', '+')}"
    print(f"Scraping ReliefWeb ({category}): {url}")
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        jobs = []
        job_cards = soup.select('article.rw-river-article')
        
        for card in job_cards:
            title_elem = card.select_one('.rw-river-article__title a')
            org_elem = card.select_one('.rw-entity-meta__tag-value--source a')
            location_elem = card.select_one('.rw-entity-country-slug a') 
            date_elem = card.select_one('.rw-entity-meta__tag-value--posted time')
            
            if title_elem:
                title = title_elem.text.strip()
                link = title_elem['href']
                company = org_elem.text.strip() if org_elem else "N/A"
                location = location_elem.text.strip() if location_elem else "N/A"
                date_posted = date_elem.text.strip() if date_elem else datetime.now().strftime("%Y-%m-%d")

                jobs.append({
                    'title': f"[{category}] {title}", 
                    'company': company,
                    'location': location,
                    'link': link,
                    'date_posted': date_posted,
                    'source': 'ReliefWeb',
                    'is_fresh': True # ReliefWeb sorts by date usually
                })
        
        logging.info(f"Scraped {len(jobs)} {category} from ReliefWeb")
        return jobs
    except Exception as e:
        logging.error(f"Error scraping ReliefWeb ({category}): {str(e)}")
        return []

def scrape_scholarships(query="medical"):
    """Scrapes scholarships from ScholarshipsAds."""
    url = f"https://www.scholarshipsads.com/?s={query.replace(' ', '+')}" 
    print(f"Scraping ScholarshipsAds: {url}")
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        scholarships = []
        cards = soup.select('div.card-scholarships')
        
        for card in cards:
            title_elem = card.select_one('h5.card-title a')
            date_elem = card.select_one('span.card-date')
            
            if title_elem:
                title = title_elem.text.strip()
                link = title_elem['href']
                date_posted = date_elem.text.strip() if date_elem else datetime.now().strftime("%Y-%m-%d")
                
                scholarships.append({
                    'title': f"[Scholarship] {title}",
                    'company': "ScholarshipsAds", 
                    'location': "See Details",
                    'link': link,
                    'date_posted': date_posted,
                    'source': 'ScholarshipsAds',
                    'is_fresh': True
                })
                
        logging.info(f"Scraped {len(scholarships)} scholarships from ScholarshipsAds")
        return scholarships
    except Exception as e:
        logging.error(f"Error scraping ScholarshipsAds: {str(e)}")
        return []

def scrape_ahram_health(url="https://english.ahram.org.eg/Portal/54/0/Health.aspx"):
    """Scrapes health news from Ahram Online."""
    print(f"Scraping Ahram Online: {url}")
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        news = []
        
        links = soup.find_all('a', href=True)
        count = 0
        for a in links:
            if count >= 5: break
            href = a['href']
            text = a.text.strip()
            
            if len(text) > 20 and "/News/" in href and "Health" not in text: 
                if not href.startswith("http"):
                    href = "https://english.ahram.org.eg" + href
                
                if not any(n['link'] == href for n in news):
                    news.append({
                        'title': f"[News] {text}",
                        'company': "Ahram Online",
                        'location': "Egypt",
                        'link': href,
                        'date_posted': datetime.now().strftime("%Y-%m-%d"),
                        'source': 'Ahram Online',
                        'is_fresh': False # Can't determine freshness easily
                    })
                    count += 1
        return news
    except Exception as e:
        logging.error(f"Error scraping Ahram Online: {str(e)}")
        return []

def scrape_internships(query="internship"):
    """Scrapes internships from various sources."""
    print(f"🔎 Scraping Internships with query: {query}")
    internships = []
    
    internships.extend(scrape_wuzzuf_jobs(query, category="Internship"))
    internships.extend(scrape_reliefweb_jobs(query, category="Internship"))
    
    return internships

def scrape_opportunities(queries=None):
    if queries is None:
        queries = {} 
        
    all_opportunities = []
    
    # Jobs (Wuzzuf)
    q_wuzzuf = queries.get('wuzzuf')
    if q_wuzzuf:
         all_opportunities.extend(scrape_wuzzuf_jobs(q_wuzzuf, category="Job"))
    else:
         all_opportunities.extend(scrape_wuzzuf_jobs(category="Job"))

    # Jobs (ReliefWeb)
    q_relief = queries.get('reliefweb')
    if q_relief:
        all_opportunities.extend(scrape_reliefweb_jobs(q_relief, category="Job"))
    else:
        all_opportunities.extend(scrape_reliefweb_jobs(category="Job"))

    # Scholarships
    q_scholar = queries.get('scholarships')
    if q_scholar:
        all_opportunities.extend(scrape_scholarships(q_scholar))
    else:
        all_opportunities.extend(scrape_scholarships())

    # Internships
    q_intern = queries.get('internships')
    if q_intern:
        all_opportunities.extend(scrape_internships(q_intern))
    else:
        all_opportunities.extend(scrape_internships("medical internship"))

    # Ahram
    q_ahram = queries.get('ahram_category_url')
    if q_ahram:
        all_opportunities.extend(scrape_ahram_health(q_ahram))
    else:
        all_opportunities.extend(scrape_ahram_health())
    
    return all_opportunities
