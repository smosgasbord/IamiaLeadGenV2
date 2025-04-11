import streamlit as st
import pandas as pd
from scraper_leads import fallback_scrape_leads
from scraper_empresas import search_empresa
from utils import score_lead, simple_email_validator
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("USER")
password = os.getenv("PASSWORD")

st.set_page_config(
    page_title='IamiaLeadGen',
    page_icon='https://msgsndr-private.storage.googleapis.com/companyPhotos/188dfebd-9007-4256-b8f5-c989d447d2da.png'
)

st.sidebar.image('https://msgsndr-private.storage.googleapis.com/companyPhotos/188dfebd-9007-4256-b8f5-c989d447d2da.png', width=50)
st.sidebar.title("IAMIA LeadGenAI")


if 'user' in st.session_state:
    # SIDEBAR SETUP
    with st.sidebar:
        st.sidebar.markdown("---")
        selected_option = st.sidebar.radio(
            "Que deseas hacer?",
            ["Extraer Leads", "Buscar Empresas", "Validar Emails"],
            index=0,
            key="sidebar_option"
        )
        st.sidebar.markdown("---")

    ## LEADS EXTRACTION FUNCTIONALITY
    if selected_option == "Extraer Leads":
        st.title("Extraer Leads")
        st.subheader("Generacion de Leads Impulsada con AI")
        st.write("Ingresa una empresa y el puesto objetivo para descubrir al instante contactos relevantes con enlaces verificados de LinkedIn y estimaciones inteligentes de correo electrónico. Utiliza la calificación impulsada por IA para priorizar los contactos de mayor impacto, ordena/filtra según tus necesidades y descarga los resultados en un archivo CSV listo para usar.")
        st.divider()

        with st.form("lead_form"):
            company = st.text_input("Nombre de la compania")
            role = st.text_input("Rol de los usuarios en la compania")
            company_domain = st.text_input("Dominio Principal")
            example_email = st.text_input("Email Ejemplo", placeholder="Si ya conoces un email, puedes ingresarlo aqui para que el sistema lo use como referencia")
            country = st.selectbox("Selecciona un país", 
                                options=['www','mx', 'co'],
                                format_func=lambda x: {'www': 'Global', 
                                                    'mx': 'México', 
                                                    'co': 'Colombia'}[x])

            submit_button = st.form_submit_button("Generar Leads")

        if submit_button:

            raw_leads = fallback_scrape_leads(company, role, company_domain, country, example_email)

            if not raw_leads:
                st.warning("No leads found. Try adjusting your input.")
            else:
                leads = []
                for lead in raw_leads:
                    try:
                        if "Company" not in lead:
                            lead["Company"] = company

                        lead["Lead Score"] = score_lead(lead, role)
                        leads.append(lead)
                    except Exception as e:
                        st.error(f"Error processing lead: {lead}\n{e}")

                st.session_state["leads"] = leads
                st.session_state["company"] = company
                st.session_state["role"] = role
                st.session_state["company_domain"] = company_domain
                st.session_state["example_email"] = example_email
                st.session_state['country'] = country
                st.success("Sus leads han sido generados con éxito.")

        if "leads" in st.session_state:
            leads = st.session_state["leads"]
            df = pd.DataFrame(leads)
            min_score = st.slider("Minimum Lead Score", 0, 10, 0)
            df_filtered = df[df["Lead Score"] >= min_score]
            st.dataframe(df_filtered)
            st.download_button(
                "Download Leads CSV",
                df_filtered.to_csv(index=False),
                "leads.csv",
                "text/csv"
            )

            st.subheader("Baja los emails a validar")
            emails_to_validate = []
            for lead in leads:
                if lead.get('Email Probables'):
                    emails_to_validate.extend(lead['Email Probables'].split(','))

            if len(emails_to_validate) > 0:
                df_emails = pd.DataFrame(emails_to_validate)
                df_emails.columns = ['emails']
                st.download_button(
                    "Download Emails CSV",
                    df_emails.to_csv(index=False),
                    "emails.csv",
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

    ## EMAIL VALIDATOR
    if selected_option == 'Validar Emails':
        st.title("Validar Emails")
        st.subheader("Verifica la validez de un email")
        email = st.text_input("Ingrese el email a validar")

        if st.button("Validar Email"):
            st.session_state["email"] = email
            if not email:
                st.warning("Por favor ingrese un email para validar.")
            else:
                email_validated = simple_email_validator(email)
                
                if email_validated is True:
                    st.success("El email es válido.")
                else:
                    st.error("El email no es válido.")

        st.subheader("Verifica la validez de varios emails")

        email_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])
        
        if st.button('Comenzar validacion'):
            st.session_state["email_file"] = email_file
            if email_file:
                data = pd.read_csv(email_file)
                if 'emails' in data.columns:
                    emails = data['emails'].tolist()
                    results = []
                    for email in emails:
                        print("validando:", email)
                        email_validated = simple_email_validator(email)
                        if email_validated is True:
                            results.append({"email": email, "valid": email_validated})
                            print(f"El email {email} es válido.")
                    df_results = pd.DataFrame(results)
                    st.dataframe(df_results)
                    st.download_button(
                        "Descargar Resultados",
                        df_results.to_csv(index=False),
                        "validation_results.csv",
                        "text/csv"
                    )
                else:
                    st.error("El archivo CSV no contiene una columna llamada 'emails'.")

#Login form
else:
    if "user" not in st.session_state:
        st.title("IAMIA LeadGenAI")
        st.subheader("Generacion de Leads Impulsada con AI")
        st.write("Por favor inicia sesion para acceder a la herramienta.")
        st.divider()

        user = st.text_input("Usuario", placeholder="Nombre de usuario")
        password = st.text_input("Contraseña", type="password", placeholder="Contraseña")

        if st.button("Iniciar Sesion"):
            if user and password:
                if user == os.getenv("USER") and password == os.getenv("PASSWORD"):
                    st.session_state["user"] = user
                    st.session_state["password"] = password
                    st.success("Inicio de sesión exitoso.")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Inténtalo de nuevo.")


        

