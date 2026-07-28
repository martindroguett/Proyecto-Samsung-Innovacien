"""Clasificador de especies.

Estado actual: SIMULADO. Devuelve un resultado deterministico a partir del
contenido de la imagen, para poder construir y demostrar la interfaz.

TODO (equipo) — conectar el modelo real:
  1. Elegir/entrenar el modelo en Hugging Face y poner su id en MODELO_HF.
  2. Instalar las dependencias opcionales de requirements.txt.
  3. Activar el modelo real con la variable de entorno INNOVACIEN_MODELO=hf
     (o cambiar USAR_MODELO_REAL a True).
  4. Mapear las etiquetas del modelo a los nombres del catalogo (data/especies.csv)
     en MAPA_ETIQUETAS.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field

import streamlit as st

from core.datos import cargar_especies

# Candidato inicial: modelo generico de clasificacion de imagenes.
# TODO (equipo): reemplazar por nuestro modelo fine-tuneado con las fotos propias.
MODELO_HF = "google/vit-base-patch16-224"

USAR_MODELO_REAL = os.getenv("INNOVACIEN_MODELO", "").lower() == "hf"

# Etiqueta que devuelve el modelo -> nombre_comun en data/especies.csv
# TODO (equipo): completar cuando sepamos las etiquetas reales del modelo.
MAPA_ETIQUETAS: dict[str, str] = {
    # "beaver": "Castor americano",
    # "wild_boar": "Jabali",
}

UMBRAL_CONFIANZA = 0.60  # bajo este valor pedimos revision humana


@dataclass
class Prediccion:
    """Resultado de la clasificacion de una foto."""
    especie: str
    confianza: float
    es_invasora: bool
    tipo: str = "Desconocido"
    impacto_ambiental: str = "Bajo"
    autoridad: str = "SAG"
    descripcion: str = ""
    alternativas: list[tuple[str, float]] = field(default_factory=list)
    simulado: bool = True

    @property
    def confiable(self) -> bool:
        return self.confianza >= UMBRAL_CONFIANZA


# --------------------------------------------------------------------------
# API publica
# --------------------------------------------------------------------------
def clasificar(imagen_bytes: bytes) -> Prediccion:
    """Clasifica una foto y devuelve la especie mas probable."""
    if USAR_MODELO_REAL:
        return _clasificar_hf(imagen_bytes)
    return _clasificar_simulado(imagen_bytes)


# --------------------------------------------------------------------------
# Implementacion simulada (la que corre hoy)
# --------------------------------------------------------------------------
def _clasificar_simulado(imagen_bytes: bytes) -> Prediccion:
    """Elige una especie del catalogo segun el hash de la imagen.

    La misma foto siempre da el mismo resultado, asi las demos son estables.
    """
    especies = cargar_especies()
    semilla = int(hashlib.sha256(imagen_bytes).hexdigest(), 16)

    idx = semilla % len(especies)
    fila = especies.iloc[idx]
    confianza = 0.55 + (semilla % 4400) / 10000  # 0.55 - 0.99

    # Dos alternativas distintas a la principal.
    otras_idx = [i for i in ((idx + 1 + semilla % 3) % len(especies),
                             (idx + 4 + semilla % 5) % len(especies))
                 if i != idx][:2]
    alternativas = [
        (especies.iloc[i]["nombre_comun"], round(max(0.02, (1 - confianza) * peso), 3))
        for i, peso in zip(otras_idx, (0.6, 0.3))
    ]

    return Prediccion(
        especie=fila["nombre_comun"],
        confianza=round(confianza, 3),
        es_invasora=True,  # todo el catalogo de ejemplo es invasor
        tipo=fila["tipo"],
        impacto_ambiental=fila["impacto_ambiental"],
        autoridad=fila["autoridad"],
        descripcion=fila["descripcion"],
        alternativas=alternativas,
        simulado=True,
    )


# --------------------------------------------------------------------------
# Implementacion real con Hugging Face (pendiente de activar)
# --------------------------------------------------------------------------
@st.cache_resource(show_spinner="Cargando modelo…")
def _cargar_pipeline():
    """Carga el pipeline de Hugging Face una sola vez por sesion del servidor."""
    from transformers import pipeline  # import diferido: dependencia opcional

    return pipeline("image-classification", model=MODELO_HF)


def _clasificar_hf(imagen_bytes: bytes) -> Prediccion:
    import io

    from PIL import Image

    clasificador = _cargar_pipeline()
    imagen = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")
    resultados = clasificador(imagen, top_k=3)

    mejor = resultados[0]
    nombre = MAPA_ETIQUETAS.get(mejor["label"], mejor["label"])

    especies = cargar_especies()
    ficha = especies[especies["nombre_comun"].str.lower() == nombre.lower()]

    if ficha.empty:
        # El modelo reconocio algo que no esta en nuestro catalogo de invasoras.
        return Prediccion(
            especie=nombre,
            confianza=round(float(mejor["score"]), 3),
            es_invasora=False,
            alternativas=[(r["label"], round(float(r["score"]), 3)) for r in resultados[1:]],
            simulado=False,
        )

    f = ficha.iloc[0]
    return Prediccion(
        especie=f["nombre_comun"],
        confianza=round(float(mejor["score"]), 3),
        es_invasora=True,
        tipo=f["tipo"],
        impacto_ambiental=f["impacto_ambiental"],
        autoridad=f["autoridad"],
        descripcion=f["descripcion"],
        alternativas=[(r["label"], round(float(r["score"]), 3)) for r in resultados[1:]],
        simulado=False,
    )
