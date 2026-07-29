"""Clasificador de especies utilizando el modelo YOLO11 real entrenado."""

from __future__ import annotations

import io
from pathlib import Path
from dataclasses import dataclass, field
import streamlit as st
from PIL import Image

from core.datos import cargar_especies

RUTA_LOCAL_KAGGLE = Path(r"C:\Users\rapha\Documents\Samsung\resultados_entrenamiento\weights\best.pt")
MODELO_PATH = Path(__file__).parent / "best.pt"
if not MODELO_PATH.exists() and RUTA_LOCAL_KAGGLE.exists():
    MODELO_PATH = RUTA_LOCAL_KAGGLE

MODELO_HF = "YOLO11s (Entrenado en Kaggle - 554 imágenes)"
USAR_MODELO_REAL = True

# Mapeo de etiquetas del modelo -> nombre_comun en data/especies.csv
MAPA_ETIQUETAS: dict[str, str] = {
    "jabali": "Jabali",
    "liebre": "Liebre europea",
    "rata gris": "Rata gris",
}

UMBRAL_CONFIANZA = 0.50  # Confianza mínima para considerar detección válida


@dataclass
class Prediccion:
    """Resultado de la clasificacion de una foto."""
    especie: str
    confianza: float
    es_invasora: bool
    tipo: str = "Desconocido"
    riesgo: str = "Bajo"
    autoridad: str = "SAG"
    descripcion: str = ""
    alternativas: list[tuple[str, float]] = field(default_factory=list)
    simulado: bool = False

    @property
    def confiable(self) -> bool:
        return self.confianza >= UMBRAL_CONFIANZA


@st.cache_resource(show_spinner="Cargando modelo de IA...")
def _cargar_modelo():
    from ultralytics import YOLO
    if not MODELO_PATH.exists():
        raise FileNotFoundError(f"No se encontró el modelo en {MODELO_PATH}")
    return YOLO(str(MODELO_PATH))


def clasificar(imagen_bytes: bytes) -> Prediccion:
    """Clasifica una foto usando el modelo YOLO11 entrenado."""
    try:
        model = _cargar_modelo()
        imagen = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")

        # Inferencia con YOLO
        results = model.predict(source=imagen, conf=0.20, verbose=False)
        res = results[0]
        boxes = res.boxes

        if boxes is None or len(boxes) == 0:
            return Prediccion(
                especie="No identificada",
                confianza=0.0,
                es_invasora=False,
                descripcion="No se detecto ninguna especie invasora conocida en la imagen.",
                simulado=False,
            )

        # Ordenar por confianza y tomar la mayor
        boxes_sorted = sorted(boxes, key=lambda b: float(b.conf[0]), reverse=True)
        top_box = boxes_sorted[0]
        clase_id = int(top_box.cls[0])
        nombre_raw = model.names[clase_id]
        confianza = float(top_box.conf[0])

        # Nombre común según nuestro mapa
        nombre_comun = MAPA_ETIQUETAS.get(nombre_raw, nombre_raw.title())

        # Buscar ficha en el catálogo CSV de especies
        especies = cargar_especies()
        ficha = especies[especies["nombre_comun"].str.lower() == nombre_comun.lower()]

        # Alternativas de otras detecciones en la foto
        alternativas = []
        for b in boxes_sorted[1:]:
            c_name = MAPA_ETIQUETAS.get(model.names[int(b.cls[0])], model.names[int(b.cls[0])])
            alternativas.append((c_name, round(float(b.conf[0]), 3)))

        if ficha.empty:
            return Prediccion(
                especie=nombre_comun,
                confianza=round(confianza, 3),
                es_invasora=True,
                tipo="Animal",
                riesgo="Alto",
                autoridad="SAG",
                alternativas=alternativas,
                simulado=False,
            )

        f = ficha.iloc[0]
        return Prediccion(
            especie=f["nombre_comun"],
            confianza=round(confianza, 3),
            es_invasora=True,
            tipo=f.get("tipo", "Animal"),
            riesgo=f.get("riesgo", "Alto"),
            autoridad=f.get("autoridad", "SAG"),
            descripcion=f.get("descripcion", ""),
            alternativas=alternativas,
            simulado=False,
        )

    except Exception as e:
        st.error(f"Error en la inferencia del modelo: {e}")
        return Prediccion(
            especie="Error de deteccion",
            confianza=0.0,
            es_invasora=False,
            descripcion=str(e),
            simulado=False,
        )
