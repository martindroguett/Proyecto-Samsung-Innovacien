"""Pestana: especies invasoras registradas cerca del usuario."""

from __future__ import annotations

import pandas as pd
import pydeck as pdk
import streamlit as st

from core import datos, ubicacion
from core.theme import RIESGO_COLOR, ficha_especie, pendiente

COLOR_RGB = {
    "Alto": [210, 50, 40],       # Terracota / Rojo
    "Medio": [215, 160, 30],     # Ocre / Amarillo
    "Bajo": [74, 124, 89],       # Verde
}


def render() -> None:
    ubi = ubicacion.actual()
    st.subheader("Especies invasoras en tu area")
    st.write(f"Registros a menos de **{ubi['radio_km']} km** de "
             f"**{ubi['region']}**. Cambia la zona en la barra lateral.")

    cerca = datos.avistamientos_cerca(ubi["lat"], ubi["lon"], ubi["radio_km"])

    # Filtros principales en fila limpia de 3 columnas
    filtros = st.columns([1, 1, 1])
    tipos = filtros[0].multiselect("Tipo", datos.TIPOS, default=datos.TIPOS)
    riesgos = filtros[1].multiselect("Riesgo", datos.NIVELES_RIESGO, default=datos.NIVELES_RIESGO)
    estados = filtros[2].multiselect("Estado del registro",
                                     ["Confirmado", "En revision", "Descartado"],
                                     default=["Confirmado", "En revision"])

    # Filtro de Especie opcional (compacto en desplegable para no ensuciar la vista)
    especies_disponibles = sorted(datos.cargar_especies()["nombre_comun"].unique().tolist())
    with st.expander("🔍 Filtrar por especie específica (opcional)", expanded=False):
        especies_filtro = st.multiselect(
            "Seleccionar especies a mostrar",
            especies_disponibles,
            default=[],
            placeholder="Mostrar todas las especies (selecciona aquí solo si deseas filtrar especies específicas)"
        )

    if not cerca.empty:
        cerca = cerca[cerca["tipo"].isin(tipos)
                      & cerca["riesgo"].isin(riesgos)
                      & cerca["estado"].isin(estados)]

        # Solo filtrar por especie si el usuario selecciono especies especificas
        if especies_filtro:
            cerca = cerca[cerca["nombre_comun"].isin(especies_filtro)]

    if cerca.empty:
        st.info("Sin registros para esos filtros en tu zona. Prueba ampliando el radio "
                "en la barra lateral o ajustando los filtros superiores.")
        pendiente("cargar la base real de avistamientos (hoy son datos de ejemplo).")
        return

    _resumen(cerca)
    st.divider()

    col_mapa, col_lista = st.columns([1.3, 1], gap="large")
    with col_mapa:
        _mapa(cerca, ubi["lat"], ubi["lon"])
    with col_lista:
        _lista(cerca)

    with st.expander("Ver todos los registros en tabla"):
        st.dataframe(
            cerca[["nombre_comun", "nombre_cientifico", "tipo", "riesgo",
                   "comuna", "region", "fecha", "estado", "distancia_km"]]
            .rename(columns={"nombre_comun": "Especie", "nombre_cientifico": "Nombre cientifico",
                             "tipo": "Tipo", "riesgo": "Riesgo", "comuna": "Comuna",
                             "region": "Region", "fecha": "Fecha", "estado": "Estado",
                             "distancia_km": "Distancia (km)"}),
            hide_index=True, width="stretch",
        )


def _resumen(cerca) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros cercanos", len(cerca))
    c2.metric("Especies distintas", cerca["nombre_comun"].nunique())
    c3.metric("Riesgo alto", int((cerca["riesgo"] == "Alto").sum()))
    c4.metric("Mas cercano", f"{cerca['distancia_km'].min():.0f} km")


def _mapa(cerca, lat_center: float, lon_center: float) -> None:
    st.markdown("##### Mapa de avistamientos (Áreas de afección)")
    df = cerca.copy()

    # Alpha 35 para fondo transparente que permite ver la zona geografica afectada
    df["fill_color"] = df["riesgo"].map(lambda r: COLOR_RGB.get(r, [74, 124, 89]) + [35])
    # Alpha 255 para contorno limpio y definido
    df["line_color"] = df["riesgo"].map(lambda r: COLOR_RGB.get(r, [74, 124, 89]) + [255])
    df["radius"] = df["riesgo"].map({"Alto": 8000, "Medio": 5000, "Bajo": 3000}).fillna(4000)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_fill_color="fill_color",
        get_line_color="line_color",
        get_radius="radius",
        stroked=True,
        filled=True,
        line_width_min_pixels=2,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=lat_center,
        longitude=lon_center,
        zoom=7,
        pitch=0,
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": "<b>{nombre_comun}</b> (<i>{nombre_cientifico}</i>)<br/>"
                        "📍 {comuna}, {region}<br/>"
                        "⚠️ Riesgo: <b>{riesgo}</b> | Estado: {estado}"
            },
        )
    )
    st.caption("🔴 Riesgo alto &nbsp; 🟡 Riesgo medio &nbsp; 🟢 Riesgo bajo &nbsp; (contorno sólido con área transparente)")


def _lista(cerca) -> None:
    st.markdown("##### Las mas cercanas")
    resumen = (cerca.sort_values("distancia_km")
                    .drop_duplicates("nombre_comun")
                    .head(6))
    for _, f in resumen.iterrows():
        detalle = (f"A {f['distancia_km']:.0f} km · {f['comuna']}, {f['region']} · "
                   f"visto el {f['fecha']:%d-%m-%Y} · {f['estado']}")
        es_vector = str(f.get("portador_enfermedades", "")).strip().lower() in ["si", "sí", "true", "1"]
        st.markdown(
            ficha_especie(f["nombre_comun"], f["nombre_cientifico"], f["riesgo"], detalle, es_vector=es_vector),
            unsafe_allow_html=True,
        )
