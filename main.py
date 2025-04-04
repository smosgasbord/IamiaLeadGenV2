import streamlit as st
import pandas as pd
from scraper_leads import fallback_scrape_leads
from scraper_empresas import search_empresa
from utils import score_lead

st.set_page_config(
    page_title='IamiaLeadGen',
    page_icon='https://msgsndr-private.storage.googleapis.com/companyPhotos/188dfebd-9007-4256-b8f5-c989d447d2da.png'
)

st.sidebar.image('https://msgsndr-private.storage.googleapis.com/companyPhotos/188dfebd-9007-4256-b8f5-c989d447d2da.png', width=75)
st.sidebar.title("Extrae Leads o busca empresas")

# SIDEBAR SETUP

with st.sidebar:
    st.sidebar.markdown("---")
    selected_option = st.sidebar.radio(
        "Que deseas hacer?",
        ["Extraer Leads", "Buscar Empresas"],
        index=0,
        key="sidebar_option"
    )
    st.sidebar.markdown("---")

## LEADS EXTRACTION FUNCTIONALITY

if selected_option == "Extraer Leads":
    st.title("IAMIA LeadGenAI")
    st.subheader("Generacion de Leads Impulsada con AI")
    st.write("Ingresa una empresa y el puesto objetivo para descubrir al instante contactos relevantes con enlaces verificados de LinkedIn y estimaciones inteligentes de correo electrónico. Utiliza la calificación impulsada por IA para priorizar los contactos de mayor impacto, ordena/filtra según tus necesidades y descarga los resultados en un archivo CSV listo para usar.")

    st.divider()

    company = st.text_input("Nombre de la compania")
    role = st.text_input("Rol de los usuarios en la compania")
    company_domain = st.text_input("Dominio Principal")
    country = st.selectbox("Selecciona un país", 
                        options=['www', 'ar', 'cl', 'mx', 'co'],
                        format_func=lambda x: {'www': 'Default', 
                                            'ar': 'Argentina',
                                            'cl': 'Chile',
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

## COMPANY EXTRACTION FUNCTIONALITY

if selected_option == 'Buscar Empresas':
    st.title("Buscar Empresas")
    st.subheader("Buscar Empresas en una ciudad especifica")
    st.write("Explora y descubre empresas relacionadas con tu objetivo profesional. Accede al instante a información útil de cada organización y avanza rápidamente en la identificación de contactos clave.")

    st.divider()

    tipo_empresa = st.text_input("Tipo de empresa", placeholder="Ej: Construccion, Inmobiliarias, etc.")
    ubicacion_empresa = st.text_input("Ubicacion de las empresas", placeholder="Ej: Ciudad, Provincia, etc.")
    
    if st.button("Buscar Empresas"):

        raw_empresas = search_empresa(tipo_empresa, ubicacion_empresa)

        if not raw_empresas:
            st.warning("No se encontraron empresas.")
        else:
            empresas = []
            for empresa in raw_empresas:
                try:
                    empresas.append(empresa)
                except Exception as e:
                    st.error(f"Error processing empresa: {empresa}\n{e}")

            # Save to session state
            st.session_state["empresas"] = empresas
            st.session_state["tipo_empresa"] = tipo_empresa
            st.session_state["ubicacion_empresa"] = ubicacion_empresa
            st.success("Hemos encontrado sus empresas.")

    # Display leads if present in session state
    if "empresas" in st.session_state:
        empresas = st.session_state["empresas"]
        df = pd.DataFrame(empresas)
        st.dataframe(df)
        st.download_button(
            "Download Empresas CSV",
            df.to_csv(index=False),
            "empresas.csv",
            "text/csv"
        )
