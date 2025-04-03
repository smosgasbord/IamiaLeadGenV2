import streamlit as st
import pandas as pd
from scraper import fallback_scrape_leads
from utils import score_lead, generate_message_draft

st.set_page_config(
    page_title='IamiaLeadGen',
    page_icon='https://msgsndr-private.storage.googleapis.com/companyPhotos/188dfebd-9007-4256-b8f5-c989d447d2da.png'
)

st.logo('https://msgsndr-private.storage.googleapis.com/companyPhotos/188dfebd-9007-4256-b8f5-c989d447d2da.png', size='medium')

st.title("IAMIA LeadGenAI")
st.subheader("Generacion de Leads Impulsada con AI")
st.write("Ingresa una empresa y el puesto objetivo para descubrir al instante contactos relevantes con enlaces verificados de LinkedIn y estimaciones inteligentes de correo electrónico. Utiliza la calificación impulsada por IA para priorizar los contactos de mayor impacto, ordena/filtra según tus necesidades y descarga los resultados en un archivo CSV listo para usar.")

st.divider()

company = st.text_input("Nombre de la compania")
role = st.text_input("Rol de los usuarios en la compania")
company_domain = st.text_input("Dominio Principal")
country = st.selectbox("Selecciona un país", 
                      options=['www', 'ar', 'mx', 'co'],
                      format_func=lambda x: {'www': 'Default', 
                                           'ar': 'Argentina',
                                           'mx': 'México', 
                                           'co': 'Colombia'}[x])
#pitch = st.text_area("Your Outreach Pitch (used in Message drafts)")

if st.button("Generar Leads"):

    raw_leads = fallback_scrape_leads(company, role, company_domain, country)

    if not raw_leads:
        st.warning("No leads found. Try adjusting your input.")
    else:
        leads = []
        for lead in raw_leads:
            try:
                # Add company to lead if missing
                if "Company" not in lead:
                    lead["Company"] = company

                lead["Lead Score"] = score_lead(lead, role)
                #lead["Message Draft"] = generate_message_draft(
                #    lead.get("Name", "there"), lead.get("Company", "a company"), role, pitch
                #)
                leads.append(lead)
            except Exception as e:
                st.error(f"Error processing lead: {lead}\n{e}")

        # Save to session state
        st.session_state["leads"] = leads
        st.session_state["company"] = company
        st.session_state["role"] = role
        st.session_state["company_domain"] = company_domain
        st.session_state['country'] = country
        st.success("Sus leads han sidos generados con exito.")

# Display leads if present in session state
if "leads" in st.session_state:
    leads = st.session_state["leads"]
    df = pd.DataFrame(leads)
    min_score = st.slider("Minimum Lead Score", 0, 10, 0) #0 is set as default to make up for any scraping/parsing edge cases (trusting PageRank)
    df_filtered = df[df["Lead Score"] >= min_score]
    st.dataframe(df_filtered)
    st.download_button(
        "Download Leads CSV",
        df_filtered.to_csv(index=False),
        "leads.csv",
        "text/csv"
    )
