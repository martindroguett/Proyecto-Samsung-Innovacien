"""Proyecto Innovacien — deteccion de especies invasoras a partir de fotos.

Ejecutar con:  streamlit run app.py

Cada pestana vive en su propio archivo dentro de views/, para que podamos
trabajar en paralelo sin pisarnos.
"""

import streamlit as st

from core import ubicacion
from core.theme import aplicar_tema, encabezado
from views import acerca, alertar, catalogo, cerca, reportes

st.set_page_config(
    page_title="Proyecto Innovacien",
    page_icon="🌿",
    layout="wide",
)

aplicar_tema()
encabezado()

# Zona del usuario: la eligen una vez en la barra lateral y la usan todas las pestanas.
ubicacion.selector_sidebar()

# El orden define el orden de las pestanas. La primera es la principal.
PESTANAS = [
    ("🚨 Alertar animal", alertar),
    ("📍 Especies invasoras en tu area", cerca),
    ("📖 Catalogo de especies", catalogo),
    ("🗂️ Mis reportes", reportes),
    ("ℹ️ Acerca del proyecto", acerca),
]

for pestana, (_, vista) in zip(st.tabs([t for t, _ in PESTANAS]), PESTANAS):
    with pestana:
        vista.render()

st.divider()
st.caption("Proyecto Innovacien · version base en construccion · "
           "datos de ejemplo y modelo simulado")
