from googlesearch import search
import requests
from bs4 import BeautifulSoup
import time

def search_empresa(tipo_empresa, ubicacion_empresa):
    
    # datos a excluir
    exclude_terms = "-listado -ranking -top -mejores"
    query = f"{tipo_empresa} empresa en {ubicacion_empresa} {exclude_terms} email"
    
    try:
        results = list(search(query, num_results=30))
        time.sleep(3)
    except Exception as e:
        print(f"Search error: {e}")
        return []

    empresas = []
    for url in results:
        if any(domain in url.lower() for domain in ["rankings", "listados", "forbes", "wikipedia"]):
            continue
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # email
            email = None
            # hay emails en beatifull soup?
            for text in soup.stripped_strings:
                if '@' in text and '.' in text:
                    email = text.strip()
                    break
            
            if email:
                empresas.append({
                    "url": url,
                    "email": email
                })

        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

    return empresas

    