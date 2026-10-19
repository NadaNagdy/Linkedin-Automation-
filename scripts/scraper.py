import requests
from bs4 import BeautifulSoup

def fetch_trends():
    trends = []
    
    # 1. سحب أخبار من TechCrunch Health
    try:
        tc_url = "https://techcrunch.com/category/biotech-health/"
        res = requests.get(tc_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = soup.find_all('h3', class_='loop-card__title', limit=3)
        for a in articles:
            title = a.text.strip()
            link_tag = a.find('a')
            link = link_tag['href'] if link_tag else tc_url
            trends.append({"title": f"Tech (Health): {title}", "url": link})
    except Exception as e:
        print(f"Error scraping TechCrunch: {e}")

    # 2. سحب أبحاث من PubMed عبر NCBI E-utilities API
    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        term = "public health[Title/Abstract] OR digital health[Title/Abstract] OR artificial intelligence medicine[Title/Abstract]"
        params = {
            "db": "pubmed",
            "term": term,
            "sort": "pub_date",
            "retmax": 5,
            "retmode": "json"
        }
        s_res = requests.get(search_url, params=params, timeout=10)
        id_list = s_res.json().get("esearchresult", {}).get("idlist", [])
        
        if id_list:
            import xml.etree.ElementTree as ET
            efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            eparams = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "xml"
            }
            eres = requests.get(efetch_url, params=eparams, timeout=10)
            root = ET.fromstring(eres.text)
            
            for p_article in root.iter("PubmedArticle"):
                pmid_el = p_article.find(".//PMID")
                pmid = pmid_el.text if pmid_el is not None else ""
                
                title_el = p_article.find(".//ArticleTitle")
                title = title_el.text if title_el is not None else ""
                if title:
                    title = title.strip().rstrip(".")
                    
                journal_el = p_article.find(".//Journal/Title")
                journal = journal_el.text if journal_el is not None else "Medical Journal"
                
                abstract_texts = p_article.findall(".//AbstractText")
                abstract = " ".join([a.text for a in abstract_texts if a.text is not None])
                
                link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                
                if title and pmid:
                    trends.append({
                        "title": f"Research (PubMed): {title}",
                        "url": link,
                        "source": "PubMed",
                        "company": journal,
                        "description": abstract
                    })
    except Exception as e:
        print(f"Error scraping PubMed: {e}")

    return trends
