"""Ubicacion del usuario, compartida por todas las pestanas.

Hoy la region se elige a mano en la barra lateral.
TODO (equipo): detectar la ubicacion desde el navegador (componente de
geolocalizacion o streamlit-js-eval) y usarla como valor por defecto.
"""

from __future__ import annotations

import streamlit as st

from core.datos import REGIONES

REGION_POR_DEFECTO = "Metropolitana"


def selector_sidebar() -> dict:
    """Dibuja el selector de zona en la barra lateral y devuelve la ubicacion."""
    with st.sidebar:
        st.markdown("### 📍 Tu zona")
        region = st.selectbox(
            "Region",
            list(REGIONES),
            index=list(REGIONES).index(REGION_POR_DEFECTO),
            key="ubi_region",
        )
        lat_ref, lon_ref = REGIONES[region]

        radio = st.slider("Radio de busqueda (km)", 25, 500, 150, step=25, key="ubi_radio")

        with st.expander("Ajustar coordenadas"):
            lat = st.number_input("Latitud", value=float(lat_ref), format="%.4f", key="ubi_lat")
            lon = st.number_input("Longitud", value=float(lon_ref), format="%.4f", key="ubi_lon")

        st.caption("Los datos mostrados son de ejemplo mientras cargamos la base real.")

    return {"region": region, "lat": lat, "lon": lon, "radio_km": radio}


def actual() -> dict:
    """Ubicacion vigente, para usar desde cualquier vista."""
    region = st.session_state.get("ubi_region", REGION_POR_DEFECTO)
    lat_ref, lon_ref = REGIONES[region]
    return {
        "region": region,
        "lat": st.session_state.get("ubi_lat", lat_ref),
        "lon": st.session_state.get("ubi_lon", lon_ref),
        "radio_km": st.session_state.get("ubi_radio", 150),
    }
