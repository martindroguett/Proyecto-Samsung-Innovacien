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

# Colores por nivel de impacto ambiental (se usan en el mapa y en las fichas)
IMPACTO_COLOR = {
    "Alto": "#B4622F",     # terracota
    "Medio": "#C9A227",    # ocre
    "Bajo": "#4A7C59",     # verde
}

# Color de la etiqueta de especie portadora de enfermedades
ENFERMEDAD_COLOR = "#8E3B46"  # burdeo, para distinguirla del impacto ambiental

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
      overflow: hidden;
      height: 480px;
      display: flex;
      flex-direction: column;
  }}
  .inv-card h4 {{
      margin: 0 0 0.2rem 0;
      color: {VERDE_OSCURO};
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
  }}
  .inv-card .sci {{
      font-style: italic;
      color: {CORTEZA};
      font-size: 0.88rem;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
  }}
  .inv-card p {{
      margin: 0.4rem 0 0 0;
      font-size: 0.9rem;
      color: {TEXTO};
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      flex: 1;
  }}
  .inv-card .tags {{ display: flex; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.3rem; flex-shrink: 0; }}

  /* ---- Foto de la especie ---- */
  .inv-foto {{
      width: 100%;
      height: 260px;
      object-fit: cover;
      border-radius: 8px;
      margin-bottom: 0.6rem;
      display: block;
      flex-shrink: 0;
  }}
  .inv-foto-placeholder {{
      width: 100%;
      height: 260px;
      border-radius: 8px;
      margin-bottom: 0.6rem;
      flex-shrink: 0;
      background: {ARENA};
      color: {CORTEZA};
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.85rem;
  }}

  /* ---- Etiquetas (impacto ambiental / portador de enfermedades) ---- */
  .inv-tag {{
      display: inline-block;
      padding: 0.12rem 0.6rem;
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


def tag_impacto(nivel: str) -> str:
    """Devuelve el HTML de una etiqueta de impacto ambiental."""
    color = IMPACTO_COLOR.get(nivel, VERDE)
    return f'<span class="inv-tag" style="background:{color}">Impacto {nivel.lower()}</span>'


def tag_enfermedad() -> str:
    """Devuelve el HTML de la etiqueta de especie portadora de enfermedades."""
    return f'<span class="inv-tag" style="background:{ENFERMEDAD_COLOR}">🦠 Portadora de enfermedades</span>'


def ficha_especie(nombre: str, cientifico: str, impacto_ambiental: str, detalle: str = "",
                  imagen_url: str | None = None, portador_enfermedades: bool = False) -> str:
    """Devuelve el HTML de una ficha de especie, con foto y etiquetas."""
    color = IMPACTO_COLOR.get(impacto_ambiental, VERDE)

    if imagen_url:
        foto_html = f'<img class="inv-foto" src="{imagen_url}" alt="{nombre}">'
    else:
        foto_html = '<div class="inv-foto-placeholder">📷 Sin foto disponible</div>'

    tags = tag_impacto(impacto_ambiental)
    if portador_enfermedades:
        tags += tag_enfermedad()

    return f"""<div class="inv-card" style="border-left-color:{color}">
                 {foto_html}
                 <h4>{nombre}</h4>
                 <div class="sci">{cientifico}</div>
                 <div class="tags">{tags}</div>
                 <p>{detalle}</p>
               </div>"""


def pendiente(texto: str) -> None:
    """Bloque visual para marcar lo que falta construir."""
    st.markdown(f'<div class="inv-todo">🚧 <b>Por completar:</b> {texto}</div>',
                unsafe_allow_html=True)