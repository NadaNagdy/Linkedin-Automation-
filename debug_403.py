import requests

def test_url(url, name):
    print(f"Testing {name}: {url}")
    
    headers_list = [
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
             'Accept-Language': 'en-US,en;q=0.5',
             'Referer': 'https://www.google.com/'
        }
    ]

    for i, headers in enumerate(headers_list):
        print(f"  Attempt {i+1}...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"    Status: {response.status_code}")
            if response.status_code == 200:
                print("    ✅ Success!")
                return
        except Exception as e:
            print(f"    ❌ Error: {e}")

test_url("https://www.scholarshipsads.com/?s=medical", "ScholarshipsAds")
test_url("https://english.ahram.org.eg/Portal/54/0/Health.aspx", "Ahram Online")
