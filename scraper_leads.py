from googlesearch import search
from bs4 import BeautifulSoup
import requests
from utils import guess_email_from_name, clean_name, ai_guess_email, validate_lead_role

def fallback_scrape_leads(company, role, company_domain, country, example_email):
    
    query = f'site:{country}.linkedin.com/in "{company} {role}"'

    print(query)

    try:
        results = list(search(query, num_results=5))
                
        # Agente para revisar la paginaa scrapear [Obligatorio]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Referer': 'https://www.google.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        # Cookies [obligatorios usar cuentas falsas]
        cookies = {
            'li_at': 'AQEDATbH9KwBZfiIAAABlf1rcLMAAAGWIXf0s1YAo7MZBCsOWkg6lHnqxbcdafsEQCgouEEOOBojUI_FHOiccBI-LbmzQqjCXiAt8jeebEtelkhH6hMjXxFbxuiQufcBxmu4cbKrQWmneWbgqRtaUolf',
            'JSESSIONID': 'ajax:3024118489598864858',
            'bcookie': 'v=2&42a8cf0f-492d-4523-8564-d9241978a62e',
            'bscookie': 'v=1&20250125183325c97b3437-8476-404c-8f04-0dbbf81e5806AQHrfVp4CRvcO2ssf0EKIv0SR_AqCNaW',
            'liap': 'true',
            'li_theme': 'light',
            'li_sugr': 'cdd44ab5-df82-451b-916d-15c655d587f4',
            'lang': 'v=2&lang=es-es',
            'timezone': 'America/Cancun',
            'lidc': 'b=OB64:s=O:r=O:a=O:p=O:g=3487:u=443:x=1:i=1744310935:t=1744386430:v=2:sig=AQHGQe5lgjeuzqCt0DWD2AC5ggSoL9Tp'
        }

        response = requests.get(results[0], headers=headers, cookies=cookies , timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

    except Exception as e:
        print(f"Search error: {e}")
        return []

    leads = []
    for url in results:
        raw_name = url.split("/in/")[-1].replace("-", " ").split("/")[0].strip()
        name_guess = clean_name(raw_name)

        if not name_guess:
            continue

        clean_domain = company_domain.lower().strip()

        for ending in ['.com', '.mx', '.mx.com']:
            if clean_domain.endswith(ending):
                clean_domain = clean_domain[:-len(ending)]
                break
        
        domain_ending = '.mx' if 'mx' in company_domain.lower() else '.com'
        domain = f"{clean_domain}{domain_ending}"
        
        all_emails = []
        email_options_normal = guess_email_from_name(name_guess, domain)
        email_options_ai = ai_guess_email(name_guess, domain, company, example_email)
        is_role_valid = validate_lead_role(soup, role, name_guess, company)
        print(f"name: {name_guess}, role: {role}, is_role_valid: {is_role_valid}")

        all_emails.extend(email_options_normal)
        
        if isinstance(email_options_ai, str):
            all_emails.append(email_options_ai)
        elif isinstance(email_options_ai, list) and email_options_ai:
            all_emails.extend(email_options_ai)

        leads.append({
            "Nombre": name_guess,
            "Compania": company,
            "LinkedIn": url,
            "Email Probables": ", ".join(str(email) for email in all_emails if email),
        })

    return leads
