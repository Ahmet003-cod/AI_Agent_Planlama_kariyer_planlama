import requests
import re
from urllib.parse import unquote, quote

def search_duckduckgo(query, max_results=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        session = requests.Session()
        session.headers.update(headers)
        # Initialize cookies by fetching base Lite page
        session.get("https://lite.duckduckgo.com/lite/", timeout=10)
        # Execute query post
        response = session.post("https://lite.duckduckgo.com/lite/", data={"q": query}, timeout=10)
        
        if response.status_code == 200:
            html = response.text
            matches = re.findall(r'href="([^"]+)"\s+class=\'result-link\'>(.*?)</a>', html)
            results = []
            seen = set()
            for raw_url, raw_title in matches:
                url_clean = unquote(raw_url)
                title_clean = re.sub(r'<[^>]+>', '', raw_title).strip()
                title_clean = title_clean.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
                
                if url_clean not in seen:
                    seen.add(url_clean)
                    if "duckduckgo.com" not in url_clean:
                        results.append({
                            "title": title_clean or f"{query} Kaynağı",
                            "url": url_clean,
                            "description": f"{query} konusu için yardımcı web adresi."
                        })
                if len(results) >= max_results:
                    break
            if results:
                return results
    except Exception as e:
        print(f"DDG search error: {e}")
    
    # Fallback to direct search engine query links
    return [
        {
            "title": f"YouTube: {query} Dersleri",
            "url": f"https://www.youtube.com/results?search_query={quote(query)}",
            "description": f"YouTube üzerinde '{query}' konusu için video eğitim arama sonuçları."
        },
        {
            "title": f"Google: {query} Belge ve Dokümantasyon",
            "url": f"https://www.google.com/search?q={quote(query)}",
            "description": f"Google üzerinde '{query}' konusu için dokümantasyon ve eğitim arama sonuçları."
        }
    ]
