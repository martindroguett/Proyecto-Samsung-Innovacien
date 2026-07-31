"""Pestana: que es el proyecto, como funciona y que falta."""

from __future__ import annotations

import streamlit as st

from core import autoridades, datos, modelo
from core.ingesta import ESPECIES_OBJETIVO


def render() -> None:
    st.subheader("Acerca del proyecto")

    st.markdown("""
**Proyecto Innovacien** es una plataforma ciudadana para detectar especies
exoticas invasoras a partir de una foto, avisar a la autoridad competente y
mostrar donde se ha registrado cada especie.

El proyecto trabaja sobre **tres especies**, y solo sobre esas tres: son las que
el modelo de vision aprendio a reconocer. Todo el resto del sistema —catalogo,
mapa y analisis— se limita al mismo alcance, para que lo que la app muestra sea
exactamente lo que el modelo puede identificar.

**Como funciona**

1. La persona sube o toma una foto del animal.
2. El modelo YOLO11 la analiza y devuelve la especie con su nivel de confianza.
3. Si es una de las tres especies invasoras, se arma un aviso con la ubicacion
   y se dirige al servicio que corresponde.
4. El registro queda en el mapa junto a los avistamientos historicos de GBIF.
""")

    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("##### Especies del proyecto")
        for info in sorted(ESPECIES_OBJETIVO.values(), key=lambda i: i["id"]):
            st.write(f"- **{info['nombre_comun']}** — *{info['nombre_cientifico']}* "
                     f"(impacto {info['impacto_ambiental'].lower()}, "
                     f"avisa a {info['autoridad']})")
        st.caption("Las tres clases que reconoce el modelo, y el alcance completo "
                   "del catalogo y del analisis.")

    with c2:
        st.markdown("##### Estado del modelo")
        estado = "Modelo real entrenado" if modelo.USAR_MODELO_REAL else "Simulado"
        st.write(f"- Modo actual: **{estado}**")
        st.write(f"- Pesos: `{modelo.MODELO_NOMBRE}`")
        st.write(f"- Archivo: `core/{modelo.MODELO_PATH.name}`")
        st.write("- Umbrales de confianza por especie:")
        for etiqueta, umbral in modelo.UMBRALES_POR_ESPECIE.items():
            nombre = modelo.MAPA_ETIQUETAS.get(etiqueta, etiqueta)
            st.write(f"    - {nombre}: **{umbral:.0%}**")
        st.caption("El jabali exige mas certeza porque es grande y facil de "
                   "reconocer; la liebre y la rata usan un umbral mas accesible "
                   "por ser pequenas y mimetizarse.")

    st.divider()
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("##### Datos que usa la app")
        try:
            av = datos.cargar_avistamientos()
            st.write(f"- **{len(av):,}** avistamientos historicos")
            st.write(f"- Fuente: GBIF (iNaturalist y colecciones), Chile")
            st.write(f"- Cobertura: {av['fecha'].dt.year.min():.0f}–{av['fecha'].dt.year.max():.0f}")
            st.write(f"- Regiones con registro: {av['region'].nunique()} de 16")
        except Exception as e:
            st.warning(f"No se pudieron leer los avistamientos: {e}")
        st.caption("Datos reales descargados de GBIF, no de ejemplo. "
                   "El pipeline vive en `core/ingesta.py`.")

    with c4:
        st.markdown("##### Autoridades destinatarias")
        for sigla, info in autoridades.AUTORIDADES.items():
            st.write(f"- **{sigla}** — {info['nombre']}: {info['ambito']}")
        st.caption("Canales de contacto por confirmar antes de cualquier envio real.")

    st.divider()
    st.markdown("##### Pendientes del equipo")
    st.markdown("""
- [x] Definir la identidad visual final (logo, tipografia, colores).
- [ ] Ampliar el set de entrenamiento: hoy son 554 imagenes para tres clases.
- [ ] Evaluar el modelo con un set de prueba independiente y reportar metricas.
- [ ] Conseguir y confirmar los canales oficiales de aviso (SAG, CONAF).
- [ ] Geolocalizacion automatica desde el navegador (hoy la comuna se elige a mano).
- [ ] Base de datos compartida y cuentas de usuario: en Streamlit Cloud los
      reportes se pierden al reiniciar el contenedor.
""")
