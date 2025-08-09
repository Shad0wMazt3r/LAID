import webbrowser
import urllib.request
import urllib.parse
import json

class BrowserService:
    def __init__(self):
        self.ddg_url = "https://api.duckduckgo.com"
    
    def open_browser(self, url):
        try:
            webbrowser.open(url)
            return {"success": True, "message": f"Opened {url} in browser"}
        except Exception as e:
            return {"error": f"Failed to open browser: {str(e)}"}
    
    def search(self, query):
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = f"{self.ddg_url}/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            
            req = urllib.request.Request(search_url)
            req.add_header('User-Agent', 'LAID-Search/1.0')
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
            
            results = []
            # Get instant answer if available
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', query),
                    'url': data.get('AbstractURL', ''),
                    'content': data.get('Abstract', '')[:300] + '...'
                })
            
            # Add related topics
            for topic in data.get('RelatedTopics', [])[:4]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('Text', '')[:50] + '...',
                        'url': topic.get('FirstURL', ''),
                        'content': topic.get('Text', '')[:200] + '...'
                    })
            
            # Debug: if no results, show what we got
            if not results:
                debug_info = f"No results found. API returned keys: {list(data.keys())}"
                if data.get('Answer'):
                    results.append({
                        'title': 'Direct Answer',
                        'url': '',
                        'content': data.get('Answer', '')
                    })
                else:
                    results.append({
                        'title': 'Debug Info',
                        'url': '',
                        'content': debug_info
                    })
            
            return {"results": results, "query": query}
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}