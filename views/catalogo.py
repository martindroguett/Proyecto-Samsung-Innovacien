"""Pestana: catalogo de especies invasoras y estado del set de entrenamiento."""

from __future__ import annotations

import streamlit as st

from core import datos
from core.theme import ficha_especie, pendiente


def render() -> None:
    st.subheader("Catalogo de especies")
    st.write("Fichas de las especies que la plataforma puede reconocer.")

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

    st.caption(f"{len(filtradas)} de {len(especies)} especies")

    columnas = st.columns(2, gap="medium")
    for i, (_, f) in enumerate(filtradas.iterrows()):
        detalle = f"{f['descripcion']}<br><b>Autoridad:</b> {f['autoridad']}"
        with columnas[i % 2]:
            st.markdown(
                ficha_especie(f["nombre_comun"], f["nombre_cientifico"], f["riesgo"], detalle),
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown("##### Set de imagenes de entrenamiento")
    pendiente("subir nuestras fotos a <code>data/imagenes/&lt;nombre_especie&gt;/</code> "
              "y registrar cuantas hay por especie. Ver <code>data/imagenes/README.md</code>.")
