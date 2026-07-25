"""Pestana: que es el proyecto, como funciona y que falta."""

from __future__ import annotations

import streamlit as st

from core import autoridades, modelo


def render() -> None:
    st.subheader("Acerca del proyecto")

    st.markdown("""
**Proyecto Innovacien** es una plataforma ciudadana para detectar especies
exoticas invasoras a partir de una foto, avisar a la autoridad competente y
mostrar que especies invasoras hay cerca de cada zona.

**Como funciona**

1. La persona sube o toma una foto de un animal, insecto o planta.
2. Un modelo de clasificacion de imagenes identifica la especie.
3. Si la especie esta en el catalogo de invasoras, se arma un aviso con la
   ubicacion y se dirige al servicio que corresponde.
4. Los registros alimentan el mapa de especies invasoras por zona.
""")

    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("##### Estado del modelo")
        estado = "Modelo real (Hugging Face)" if modelo.USAR_MODELO_REAL else "Simulado"
        st.write(f"- Modo actual: **{estado}**")
        st.write(f"- Modelo configurado: `{modelo.MODELO_HF}`")
        st.write(f"- Umbral de confianza: {modelo.UMBRAL_CONFIANZA:.0%}")
        st.caption("Para activar el modelo real: `INNOVACIEN_MODELO=hf streamlit run app.py`")

    with c2:
        st.markdown("##### Autoridades destinatarias")
        for sigla, info in autoridades.AUTORIDADES.items():
            st.write(f"- **{sigla}** — {info['nombre']}: {info['ambito']}")
        st.caption("Canales de contacto por confirmar antes de cualquier envio real.")

    st.divider()
    st.markdown("##### Pendientes del equipo")
    st.markdown("""
- [ ] Cargar nuestras fotos en `data/imagenes/<especie>/` y entrenar el modelo.
- [ ] Definir el modelo de Hugging Face y mapear sus etiquetas al catalogo.
- [ ] Reemplazar los datos de ejemplo por la base real de avistamientos.
- [ ] Conseguir y confirmar los canales oficiales de aviso (SAG, CONAF, SERNAPESCA, MMA).
- [ ] Geolocalizacion automatica desde el navegador.
- [ ] Base de datos compartida y cuentas de usuario.
- [ ] Definir la identidad visual final (logo, tipografia, colores).
""")
