"""Pestana: especies invasoras registradas cerca del usuario."""

from __future__ import annotations

import streamlit as st

from core import datos, ubicacion
from core.theme import IMPACTO_COLOR, ficha_especie, pendiente


def render() -> None:
    ubi = ubicacion.actual()
    st.subheader("Especies invasoras en tu area")
    st.write(f"Registros a menos de **{ubi['radio_km']} km** de "
             f"**{ubi['region']}**. Cambia la zona en la barra lateral.")

    cerca = datos.avistamientos_cerca(ubi["lat"], ubi["lon"], ubi["radio_km"])

    filtros = st.columns([1, 1, 1])
    tipos = filtros[0].multiselect("Tipo", datos.TIPOS, default=datos.TIPOS)
    impactos = filtros[1].multiselect("Impacto ambiental", datos.NIVELES_IMPACTO, default=datos.NIVELES_IMPACTO)
    estados = filtros[2].multiselect("Estado del registro",
                                     ["Confirmado", "En revision", "Descartado"],
                                     default=["Confirmado", "En revision"])

    if not cerca.empty:
        cerca = cerca[cerca["tipo"].isin(tipos)
                      & cerca["impacto_ambiental"].isin(impactos)
                      & cerca["estado"].isin(estados)]

    if cerca.empty:
        st.info("Sin registros para esos filtros en tu zona. Prueba ampliando el radio "
                "en la barra lateral.")
        pendiente("cargar la base real de avistamientos (hoy son datos de ejemplo).")
        return

    _resumen(cerca)
    st.divider()

    col_mapa, col_lista = st.columns([1.3, 1], gap="large")
    with col_mapa:
        _mapa(cerca)
    with col_lista:
        _lista(cerca)

    with st.expander("Ver todos los registros en tabla"):
        st.dataframe(
            cerca[["nombre_comun", "nombre_cientifico", "tipo", "impacto_ambiental",
                   "comuna", "region", "fecha", "estado", "distancia_km"]]
            .rename(columns={"nombre_comun": "Especie", "nombre_cientifico": "Nombre cientifico",
                             "tipo": "Tipo", "impacto_ambiental": "Impacto ambiental", "comuna": "Comuna",
                             "region": "Region", "fecha": "Fecha", "estado": "Estado",
                             "distancia_km": "Distancia (km)"}),
            hide_index=True, width="stretch",
        )


def _resumen(cerca) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros cercanos", len(cerca))
    c2.metric("Especies distintas", cerca["nombre_comun"].nunique())
    c3.metric("Impacto alto", int((cerca["impacto_ambiental"] == "Alto").sum()))
    c4.metric("Mas cercano", f"{cerca['distancia_km'].min():.0f} km")


def _mapa(cerca) -> None:
    st.markdown("##### Mapa de avistamientos")
    df = cerca.copy()
    df["color"] = df["impacto_ambiental"].map(IMPACTO_COLOR).fillna("#4A7C59")
    df["tamano"] = df["impacto_ambiental"].map({"Alto": 9000, "Medio": 6000, "Bajo": 4000}).fillna(4000)
    st.map(df, latitude="lat", longitude="lon", color="color", size="tamano")
    st.caption("🔴 impacto alto · 🟡 impacto medio · 🟢 impacto bajo")


def _lista(cerca) -> None:
    st.markdown("##### Las mas cercanas")
    resumen = (cerca.sort_values("distancia_km")
                    .drop_duplicates("nombre_comun")
                    .head(6))
    for _, f in resumen.iterrows():
        detalle = (f"A {f['distancia_km']:.0f} km · {f['comuna']}, {f['region']} · "
                   f"visto el {f['fecha']:%d-%m-%Y} · {f['estado']}")
        imagen_url = datos.imagen_especie(f["nombre_comun"], f["nombre_cientifico"])
        portador = str(f.get("portador_enfermedades", "No")).strip().lower() == "si"
        st.markdown(
            ficha_especie(f["nombre_comun"], f["nombre_cientifico"], f["impacto_ambiental"],
                          detalle, imagen_url=imagen_url, portador_enfermedades=portador),
            unsafe_allow_html=True,
        )
