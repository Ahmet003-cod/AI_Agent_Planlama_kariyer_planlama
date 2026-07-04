import requests
import re
from urllib.parse import quote

def search_youtube_video(query):
    """
    YouTube araması yapar ve JSON veri yapısından ilk eşleşen videonun doğrudan linkini ve başlığını döner.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = f"https://www.youtube.com/results?search_query={quote(query)}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Extract video IDs
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)
            # Extract playlist IDs as fallback/alternative
            playlist_ids = re.findall(r'"playlistId":"([a-zA-Z0-9_-]+)"', response.text)
            # Extract titles
            titles = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"\}\]', response.text)
            
            # Remove duplicates
            video_ids = list(dict.fromkeys(video_ids))
            playlist_ids = list(dict.fromkeys(playlist_ids))
            
            # If a playlist is found, it might be a better resource, but direct video is also great.
            # Let's prefer the first video link if available.
            if video_ids:
                vid = video_ids[0]
                title = titles[0] if titles else f"{query} Dersleri"
                # Clean title runs characters
                title = title.replace("\\u0026", "&").replace("\\u0027", "'").replace('\\"', '"')
                return {
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={vid}"
                }
            elif playlist_ids:
                pid = playlist_ids[0]
                return {
                    "title": f"YouTube Oynatma Listesi: {query}",
                    "url": f"https://www.youtube.com/playlist?list={pid}"
                }
    except Exception as e:
        print(f"YouTube search crawl error: {e}")
        
    # Fallback to search query results page if crawling fails
    return {
        "title": f"YouTube: {query} Dersleri",
        "url": f"https://www.youtube.com/results?search_query={quote(query)}"
    }
