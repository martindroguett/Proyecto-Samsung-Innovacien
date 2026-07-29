"""Paleta de colores naturales y estilos compartidos de la app."""

import streamlit as st

# Paleta natural (bosque / arena / corteza / terracota)
VERDE = "#4A7C59"
VERDE_OSCURO = "#2F4F3E"
VERDE_CLARO = "#8FB996"
ARENA = "#EFEADB"
ARENA_CLARA = "#FBF9F3"
CORTEZA = "#5C4A38"
TERRACOTA = "#B4622F"
TEXTO = "#2B2B26"

# Colores por nivel de riesgo (se usan en el mapa y en las fichas)
RIESGO_COLOR = {
    "Alto": "#B4622F",     # terracota
    "Medio": "#C9A227",    # ocre
    "Bajo": "#4A7C59",     # verde
}

_CSS = f"""
<style>
  /* ---- Encabezado ---- */
  .inv-hero {{
      background: linear-gradient(135deg, {VERDE_OSCURO} 0%, {VERDE} 55%, {VERDE_CLARO} 100%);
      border-radius: 16px;
      padding: 1.6rem 1.9rem;
      color: {ARENA_CLARA};
      margin-bottom: 0.4rem;
  }}
  .inv-hero h1 {{
      margin: 0;
      font-size: 2.1rem;
      letter-spacing: -0.5px;
      color: {ARENA_CLARA};
  }}
  .inv-hero p {{
      margin: 0.35rem 0 0 0;
      font-size: 1rem;
      opacity: 0.92;
  }}

  /* ---- Fichas / tarjetas ---- */
  .inv-card {{
      background: #FFFFFF;
      border: 1px solid {ARENA};
      border-left: 5px solid {VERDE};
      border-radius: 12px;
      padding: 0.9rem 1.1rem;
      margin-bottom: 0.7rem;
  }}
  .inv-card h4 {{ margin: 0 0 0.2rem 0; color: {VERDE_OSCURO}; }}
  .inv-card .sci {{ font-style: italic; color: {CORTEZA}; font-size: 0.88rem; }}
  .inv-card p {{ margin: 0.4rem 0 0 0; font-size: 0.9rem; color: {TEXTO}; }}

  /* ---- Etiquetas ---- */
  .inv-tag {{
      display: inline-block;
      padding: 0.15rem 0.6rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
      color: #FFFFFF;
  }}

  /* ---- Pestañas ---- */
  .stTabs [data-baseweb="tab-list"] {{
      gap: 0.35rem;
      border-bottom: 2px solid {ARENA};
  }}
  .stTabs [data-baseweb="tab"] {{
      font-weight: 600;
      color: {CORTEZA};
  }}

  /* Placeholder visual para secciones aún no implementadas */
  .inv-todo {{
      border: 1.5px dashed {VERDE_CLARO};
      border-radius: 12px;
      padding: 1rem 1.2rem;
      background: {ARENA_CLARA};
      color: {CORTEZA};
      font-size: 0.9rem;
  }}
</style>
"""


def aplicar_tema() -> None:
    """Inyecta el CSS de la app. Llamar una vez, al inicio de app.py."""
    st.markdown(_CSS, unsafe_allow_html=True)


def encabezado(titulo: str = "Proyecto Innovacien",
               bajada: str = "Detecta especies invasoras desde una foto y alerta a las autoridades.") -> None:
    st.markdown(
        f"""<div class="inv-hero">
              <h1>🌿 {titulo}</h1>
              <p>{bajada}</p>
            </div>""",
        unsafe_allow_html=True,
    )


def tag_riesgo(nivel: str) -> str:
    """Devuelve el HTML de una etiqueta de riesgo."""
    color = RIESGO_COLOR.get(nivel, VERDE)
    return f'<span class="inv-tag" style="background:{color}">Riesgo {nivel.lower()}</span>'


def tag_sanitaria() -> str:
    """Devuelve el HTML de la etiqueta de portador de enfermedades."""
    return '<span class="inv-tag" style="background:#A71D2A;">☣️ Portador de enfermedades</span>'


def ficha_especie(nombre: str, cientifico: str, riesgo: str, detalle: str = "", es_vector: bool = False) -> str:
    """Devuelve el HTML de una ficha de especie."""
    color = RIESGO_COLOR.get(riesgo, VERDE)
    vector_html = f" &nbsp;{tag_sanitaria()}" if es_vector else ""
    return f"""<div class="inv-card" style="border-left-color:{color}">
                 <h4>{nombre} &nbsp;{tag_riesgo(riesgo)}{vector_html}</h4>
                 <div class="sci">{cientifico}</div>
                 <p>{detalle}</p>
               </div>"""


def pendiente(texto: str) -> None:
    """Bloque visual para marcar lo que falta construir."""
    st.markdown(f'<div class="inv-todo">🚧 <b>Por completar:</b> {texto}</div>',
                unsafe_allow_html=True)
