from googlesearch import search
from utils import guess_email_from_name, clean_name, ai_guess_email

def fallback_scrape_leads(company, role, company_domain, country):
    query = f'site:{country}.linkedin.com/in "{company}" "{role}"'
    try:
        results = list(search(query, num_results=30))
    except Exception as e:
        print(f"Search error: {e}")
        return []

    leads = []
    for url in results:
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

        # Combine email options
        all_emails.extend(email_options_normal)
        
        # Handle AI-generated emails
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
