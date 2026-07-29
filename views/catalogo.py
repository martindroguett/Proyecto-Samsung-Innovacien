"""Pestana: catalogo de especies invasoras y estado del set de entrenamiento."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core import datos
from core.theme import tag_riesgo, tag_sanitaria, pendiente


def render() -> None:
    st.subheader("Catalogo de especies")
    st.write("Fichas e imagenes de referencia de las especies reconocidas por la plataforma.")

    especies = datos.cargar_especies()

    c1, c2 = st.columns([2, 1])
    busqueda = c1.text_input("Buscar", placeholder="Nombre comun o cientifico…")
    tipo = c2.selectbox("Tipo", ["Todos"] + datos.TIPOS)

    filtradas = especies
    if busqueda:
        q = busqueda.lower()
        filtradas = filtradas[
            filtradas["nombre_comun"].str.lower().str.contains(q)
            | filtradas["nombre_cientifico"].str.lower().str.contains(q)
        ]
    if tipo != "Todos":
        filtradas = filtradas[filtradas["tipo"] == tipo]

    st.caption(f"Mostrando {len(filtradas)} de {len(especies)} especies")

    columnas = st.columns(2, gap="large")
    for i, (_, f) in enumerate(filtradas.iterrows()):
        with columnas[i % 2]:
            with st.container(border=True):
                # Imagen de referencia por especie
                img_url = f.get("imagen_url")
                if pd.notna(img_url) and img_url:
                    st.image(str(img_url), use_container_width=True, caption=f"{f['nombre_comun']} ({f['nombre_cientifico']})")

                # Titulo y Etiquetas de Riesgo / Sanitaria
                es_vector = str(f.get("portador_enfermedades", "")).strip().lower() in ["si", "sí", "true", "1"]
                tag_vect = f" &nbsp;{tag_sanitaria()}" if es_vector else ""

                st.markdown(f"#### {f['nombre_comun']}")
                st.markdown(f"*{f['nombre_cientifico']}* &nbsp;|&nbsp; {tag_riesgo(f['riesgo'])}{tag_vect}", unsafe_allow_html=True)
                st.write(f['descripcion'])
                st.caption(f"🏛️ **Autoridad competente:** {f['autoridad']} &nbsp;|&nbsp; 🏷️ **Tipo:** {f['tipo']}")

    st.divider()
    st.markdown("##### Set de imagenes de entrenamiento")
    pendiente("subir nuestras fotos a <code>data/imagenes/&lt;nombre_especie&gt;/</code> "
              "y registrar cuantas hay por especie.")
