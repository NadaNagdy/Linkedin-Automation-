import requests
from bs4 import BeautifulSoup

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br'
    }

url = "https://www.scholarshipsads.com/?s=computer+science"
try:
    response = requests.get(url, headers=get_headers(), timeout=15)
    print(f"Status Code: {response.status_code}")
    with open("debug_scholarships_search.html", "wb") as f:
        f.write(response.content)
    print("Saved to debug_scholarships_search.html")
except Exception as e:
    print(f"Error: {e}")
