import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="HealthExpert AI", page_icon="🩺", layout="centered")

# --- CONFIGURACIÓN DE LA API (SECRETS) ---
# Intentamos obtener la API Key de los secretos de Streamlit
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("⚠️ Error: No se encontró la API Key. Configúrala en los 'Secrets' de Streamlit.")
    st.stop()

# --- SYSTEM PROMPT (TU EXPERTO) ---
SYSTEM_PROMPT = """
Eres un Asistente Experto en Contexto de Salud. 
REGLA DE ORO: En TODAS tus respuestas incluye: "⚠️ IMPORTANTE: No soy un profesional de la salud. Información educativa. Acuda a un médico."
Tu tono y profundidad dependen estrictamente del nivel seleccionado.
- Nivel Básica: Lenguaje sencillo, analogías, para público general.
- Nivel Media: Lenguaje formal, cita fuentes generales.
- Nivel Experto: Lenguaje científico, cita protocolos, NOMs, patologías y efectos secundarios.
"""

# --- GESTIÓN DEL ESTADO (MEMORIA) ---
if "nivel" not in st.session_state:
    st.session_state.nivel = None
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Función para reiniciar todo (Botón Nueva Consulta)
def reiniciar():
    st.session_state.nivel = None
    st.session_state.mensajes = []
    # No usamos st.rerun() aquí porque el botón ya recarga la página al hacer click

# --- INTERFAZ DE USUARIO ---

# 1. PANTALLA DE SELECCIÓN DE NIVEL
if st.session_state.nivel is None:
    st.title("🩺 HealthExpert AI")
    st.markdown("### Bienvenido. Para iniciar, selecciona el nivel de profundidad:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🟢 Nivel Básico", use_container_width=True):
            st.session_state.nivel = "Básica"
            st.rerun()
            
    with col2:
        if st.button("🟡 Nivel Medio", use_container_width=True):
            st.session_state.nivel = "Media"
            st.rerun()
            
    with col3:
        if st.button("🔴 Nivel Experto", use_container_width=True):
            st.session_state.nivel = "Experto"
            st.rerun()

    st.info("ℹ️ Selecciona un nivel para habilitar el chat de consulta.")

# 2. PANTALLA DE CHAT (Solo aparece si ya eligieron nivel)
else:
    # Encabezado con botón de "Nueva Consulta"
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader(f"Modo: Nivel {st.session_state.nivel}")
    with c2:
        if st.button("🔄 Nueva Consulta"):
            reiniciar()
            st.rerun()

    # Mostrar historial de chat
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])

    # Caja de texto (Input)
    prompt = st.chat_input("Escribe tu consulta de salud aquí...")
    
    if prompt:
        # Mostrar mensaje del usuario
        st.chat_message("user").markdown(prompt)
        st.session_state.mensajes.append({"role": "user", "content": prompt})

        # --- CONEXIÓN CON GEMINI ---
        try:
            # Aquí ocurre la MAGIA: Inyectamos el nivel sin que el usuario lo escriba
            prompt_con_contexto = f"""
            {SYSTEM_PROMPT}
            ----------------
            CONTEXTO ACTUAL: El usuario ha seleccionado explícitamente el NIVEL: {st.session_state.nivel}.
            Responde la siguiente pregunta bajo ese nivel: "{prompt}"
            """
            
            # Llamada al modelo
         model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt_con_contexto)
            respuesta_ia = response.text
            
            # Mostrar respuesta IA
            with st.chat_message("assistant"):
                st.markdown(respuesta_ia)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
            
        except Exception as e:
            st.error(f"Ocurrió un error al conectar: {e}")
