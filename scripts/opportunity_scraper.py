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

def is_health_related(title, company=""):
    """Checks if a job title or company is health/medical/pharma related."""
    text = f"{title} {company}".lower()
    keywords = [
        'medic', 'health', 'clinic', 'pharma', 'doctor', 'nurse', 'nursing',
        'hospital', 'biotech', 'patient', 'dental', 'dentist', 'nutrition', 'diet',
        'lab', 'laboratory', 'pathology', 'radiology', 'therapy', 'therapist',
        'epidemiolog', 'surgery', 'surgical', 'care', 'cardio', 'pediatric',
        'oncology', 'biomedic', 'healthcare', 'sanofi', 'eva pharma', 'novartis',
        'andalous', 'pfizer', 'astrazeneca', 'gsk', 'roche', 'bayer', 'abbott',
        'hikma', 'amoun', 'eiphico', 'sedico', 'saudi german', 'cleopatra', 'dar al fouad',
        'who', 'msf', 'unicef', 'unfpa', 'biochem', 'chemist', 'physician',
        'pharmacovigilance', 'qppv', 'regulatory affairs', 'clinical research', 'cra'
    ]
    return any(k in text for k in keywords)

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
                company = company_elem.text.strip().rstrip(' -') if company_elem else "N/A"
                
                # Strict health check to avoid off-topic jobs like accounting clerk
                if not is_health_related(title, company):
                    continue

                link = title_elem['href']
                location = location_elem.text.strip() if location_elem else "N/A"
                date_posted = date_elem.text.strip() if date_elem else datetime.now().strftime("%Y-%m-%d")

                full_link = link if link.startswith('http') else f"https://wuzzuf.net{link}"
                
                # Check for freshness (today, hours, days ago, or this month)
                is_fresh = any(x in date_posted.lower() for x in ["now", "hour", "today", "minute", "day", "days", "2026-10", "oct"])
                
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
    """Scrapes jobs/internships from ReliefWeb prioritizing Egypt and Remote."""
    jobs = []
    urls = [
        f"https://reliefweb.int/jobs?search={query.replace(' ', '+')}&country=82",
        f"https://reliefweb.int/jobs?search={query.replace(' ', '+')}&telework=1"
    ]
    for url in urls:
        print(f"Scraping ReliefWeb ({category}): {url}")
        try:
            response = requests.get(url, headers=get_headers(), timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.select('article.rw-river-article')
            for card in job_cards[:8]:
                title_elem = card.select_one('.rw-river-article__title a')
                org_elem = card.select_one('.rw-entity-meta__tag-value--source a')
                location_elem = card.select_one('.rw-entity-country-slug a') 
                date_elem = card.select_one('.rw-entity-meta__tag-value--posted time')
                
                if title_elem:
                    title = title_elem.text.strip()
                    link = title_elem['href']
                    company = org_elem.text.strip() if org_elem else "N/A"
                    location = location_elem.text.strip() if location_elem else ("Egypt" if "country=82" in url else "Remote")
                    if "telework=1" in url and "remote" not in location.lower():
                        location = f"{location} (Remote)" if location != "N/A" else "Remote"
                    date_posted = date_elem.text.strip() if date_elem else datetime.now().strftime("%Y-%m-%d")

                    is_fresh = any(x in date_posted.lower() for x in ["oct", "2026", "now", "today", "hour", "day"])

                    jobs.append({
                        'title': f"[{category}] {title}", 
                        'company': company,
                        'location': location,
                        'link': link,
                        'date_posted': date_posted,
                        'source': 'ReliefWeb',
                        'is_fresh': is_fresh
                    })
        except Exception as e:
            logging.error(f"Error scraping ReliefWeb ({category}): {str(e)}")
    
    logging.info(f"Scraped {len(jobs)} {category} from ReliefWeb")
    return jobs

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

def scrape_internships(query="medical internship"):
    """Scrapes internships from various sources."""
    print(f"🔎 Scraping Internships prioritizing Egypt and Remote...")
    internships = []
    
    for q in ["medical internship", "pharmacy internship", "health internship"]:
        internships.extend(scrape_wuzzuf_jobs(q, category="Internship"))
    internships.extend(scrape_reliefweb_jobs("internship", category="Internship"))
    
    return internships

def scrape_medical_conferences():
    """Scrapes medical conferences from multiple sources (AllConferenceAlert Egypt & Global, and WHO)."""
    conferences = []
    headers = get_headers()
    
    # 1. Egypt Medical & Health Conferences (AllConferenceAlert)
    try:
        url_egypt = "https://www.allconferencealert.com/egypt/health-and-medicine.html"
        print(f"Scraping Egypt Conferences: {url_egypt}")
        res_egypt = requests.get(url_egypt, headers=headers, timeout=15)
        if res_egypt.status_code == 200:
            soup = BeautifulSoup(res_egypt.text, 'html.parser')
            for it in soup.find_all('div', class_='cp-item-main'):
                a = it.find('a', href=True)
                if not a: continue
                title = a.text.strip()
                link = a['href']
                lines = [l.strip() for l in it.get_text('\n', strip=True).split('\n') if l.strip()]
                city = "Egypt"
                organizer = "Medical Conference Committee"
                dates = ""
                for l in lines[1:]:
                    if any(c in l.lower() for c in ['cairo', 'giza', 'alexandria', 'elmohndseen', 'sharm', 'hurghada', 'luxor', 'mansoura', 'tanta']):
                        city = f"{l}, Egypt"
                    elif any(m in l.lower() for m in ['nov', 'dec', 'jan', 'feb', 'mar', '2026', '2027']):
                        dates = l
                    elif len(l) > 3 and not l.startswith('·') and l != lines[1]:
                        organizer = l
                conferences.append({
                    'title': f"[Conference] {title}",
                    'company': organizer,
                    'location': f"{city} ({dates})" if dates else city,
                    'link': link,
                    'date_posted': datetime.now().strftime("%Y-%m-%d"),
                    'source': 'ConferenceAlerts',
                    'is_fresh': True
                })
            logging.info(f"Scraped {len(conferences)} Egypt conferences from AllConferenceAlert")
    except Exception as e:
        logging.error(f"Error scraping Egypt conferences: {str(e)}")

    # 2. International Health & Medicine Conferences (AllConferenceAlert)
    try:
        url_global = "https://www.allconferencealert.com/health-and-medicine.html"
        print(f"Scraping Global Conferences: {url_global}")
        res_global = requests.get(url_global, headers=headers, timeout=15)
        if res_global.status_code == 200:
            soup_g = BeautifulSoup(res_global.text, 'html.parser')
            for a in soup_g.find_all('a', href=True):
                if '/conference/' in a['href'] and len(a.text.strip()) > 15:
                    link = a['href']
                    if any(c['link'] == link for c in conferences):
                        continue
                    parent = a.find_parent('tr') or a.find_parent('div')
                    text = parent.get_text(' | ', strip=True) if parent else a.text.strip()
                    parts = [p.strip() for p in text.split('|') if p.strip()]
                    location = "International / Virtual"
                    organizer = "International Health Forum"
                    for p in parts[1:]:
                        if any(c in p for c in [', USA', ', UK', ', Germany', ', France', ', Canada', ', Australia', ', UAE', ', Poland', ', Spain']):
                            location = p
                        elif len(p) > 3 and not any(m in p.lower() for m in ['nov', 'dec', '2026']):
                            organizer = p
                    conferences.append({
                        'title': f"[Conference] {a.text.strip()}",
                        'company': organizer,
                        'location': location,
                        'link': link,
                        'date_posted': datetime.now().strftime("%Y-%m-%d"),
                        'source': 'ConferenceAlerts',
                        'is_fresh': True
                    })
    except Exception as e:
        logging.error(f"Error scraping global conferences: {str(e)}")

    # 3. WHO Events & Global Consultations
    url_who = "https://www.who.int/news-room/events"
    print(f"Scraping WHO Events (Conferences): {url_who}")
    for attempt in range(2):
        try:
            response = requests.get(url_who, headers=headers, timeout=25)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/news-room/events/detail/' in href:
                    title = a.text.strip().replace('\n', ' ')
                    import re
                    title = re.sub(' +', ' ', title)
                    if len(title) > 10 and not any(c['link'].endswith(href) for c in conferences):
                        full_link = href if href.startswith('http') else f"https://www.who.int{href}"
                        conferences.append({
                            'title': f"[Conference] {title}",
                            'company': "World Health Organization (WHO)",
                            'location': "Global/Virtual",
                            'link': full_link,
                            'date_posted': datetime.now().strftime("%Y-%m-%d"),
                            'source': 'WHO',
                            'is_fresh': True
                        })
            break
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed scraping WHO Events: {str(e)}")

    logging.info(f"Total medical conferences scraped across all sources: {len(conferences)}")
    return conferences

def scrape_opportunities(queries=None):
    if queries is None:
        queries = {} 
        
    all_opportunities = []
    
    # 1. Jobs from Wuzzuf (Egypt medical, clinical research, pharmacist, public health)
    wuzzuf_queries = ['medical', 'clinical research', 'pharmacist', 'public health']
    for q in wuzzuf_queries:
        all_opportunities.extend(scrape_wuzzuf_jobs(q, category="Job"))

    # 2. Jobs from ReliefWeb (Egypt & Remote)
    q_relief = queries.get('reliefweb', 'health')
    all_opportunities.extend(scrape_reliefweb_jobs(q_relief, category="Job"))

    # 3. Scholarships
    q_scholar = queries.get('scholarships', 'medical')
    all_opportunities.extend(scrape_scholarships(q_scholar))

    # 4. Internships (Egypt & Remote)
    all_opportunities.extend(scrape_internships())

    # 5. Ahram
    q_ahram = queries.get('ahram_category_url')
    if q_ahram:
        all_opportunities.extend(scrape_ahram_health(q_ahram))
    else:
        all_opportunities.extend(scrape_ahram_health())
    
    # Deduplicate by link
    seen_links = set()
    unique_opps = []
    for item in all_opportunities:
        link = item.get('link')
        if link and link not in seen_links:
            seen_links.add(link)
            unique_opps.append(item)
            
    return unique_opps
