from googlesearch import search
from utils import guess_email_from_name, clean_name, ai_guess_email
import time
import logging
from typing import List, Dict, Optional

def fallback_scrape_leads(company: str, role: str, company_domain: str, country: str) -> List[Dict[str, str]]:

    query = f'site:{country}.linkedin.com/in "{company}" "{role}"'
    try:
        # Modified search parameters with error handling
        results = []
        search_results = search(query, num_results=30, advanced=True)
        
        if not search_results:
            logging.warning(f"No results found for query: {query}")
            return []
            
        for url in search_results:
            if not isinstance(url, str) or not url.strip():
                continue
            if "/in/" not in url:
                continue
            results.append(url.strip())
            time.sleep(5)  # Rate limiting
            
    except Exception as e:
        logging.error(f"Search error: {e}")
        return []

    leads = []
    for url in results:
        try:
            # Extract and validate name
            raw_name = url.split("/in/")[-1].replace("-", " ").split("/")[0].strip()
            name_guess = clean_name(raw_name)

            if not name_guess:
                continue

            # Clean and format domain properly
            clean_domain = company_domain.lower().strip()
            # Remove common domain endings if present
            for ending in ['.com', '.mx', '.mx.com']:
                if clean_domain.endswith(ending):
                    clean_domain = clean_domain[:-len(ending)]
                    break
            
            # Determine proper domain ending (.com or .mx)
            domain_ending = '.mx' if 'mx' in company_domain.lower() else '.com'
            domain = f"{clean_domain}{domain_ending}"
            
            # Generate emails using the provided domain
            all_emails = []
            email_options_normal = guess_email_from_name(name_guess, domain)
            email_options_ai = ai_guess_email(name_guess, domain, company)

            # Combine email options with validation
            if email_options_normal:
                all_emails.extend([e.strip() for e in email_options_normal if e and '@' in e])
            
            # Handle AI-generated emails
            if isinstance(email_options_ai, str) and '@' in email_options_ai:
                all_emails.append(email_options_ai.strip())
            elif isinstance(email_options_ai, list):
                all_emails.extend([e.strip() for e in email_options_ai if e and '@' in e])

            # Only add lead if we have valid emails
            if all_emails:
                leads.append({
                    "Nombre": name_guess,
                    "Compania": company,
                    "LinkedIn": url,
                    "Email Probables": ", ".join(set(all_emails))  # Remove duplicates
                })
                
        except Exception as e:
            logging.error(f"Error processing URL {url}: {e}")
            continue

    return leads
