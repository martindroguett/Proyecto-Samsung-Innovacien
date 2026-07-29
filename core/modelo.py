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

# Umbrales diferenciados por especie (accesible para rata/liebre, estricto para jabalí)
UMBRALES_POR_ESPECIE: dict[str, float] = {
    "jabali": 0.80,       # 80% mínimo para Jabalí (fácil reconocimiento)
    "liebre": 0.45,       # 45% accesible para Liebre europea
    "rata gris": 0.45,    # 45% accesible para Rata gris
}

UMBRAL_DEFAULT = 0.50
UMBRAL_CONFIANZA = 0.45  # Compatibilidad


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
        return self.confianza >= UMBRALS_POR_ESPECIE.get(self.especie.lower(), UMBRAL_DEFAULT)


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
        results = model.predict(source=imagen, conf=0.15, verbose=False)
        res = results[0]
        boxes = res.boxes

        if boxes is None or len(boxes) == 0:
            return Prediccion(
                especie="Objeto / Especie No Identificada",
                confianza=0.0,
                es_invasora=False,
                tipo="Desconocido",
                riesgo="Bajo",
                descripcion="No se detectó ninguna especie invasora conocida en la imagen.",
                simulado=False,
            )

        # Ordenar por confianza y tomar la mayor
        boxes_sorted = sorted(boxes, key=lambda b: float(b.conf[0]), reverse=True)
        top_box = boxes_sorted[0]
        clase_id = int(top_box.cls[0])
        nombre_raw = str(model.names[clase_id]).lower()
        confianza = float(top_box.conf[0])

        # Alternativas de otras detecciones en la foto
        alternativas = []
        for b in boxes_sorted[1:]:
            raw_c = str(model.names[int(b.cls[0])]).lower()
            c_name = MAPA_ETIQUETAS.get(raw_c, raw_c.title())
            alternativas.append((c_name, round(float(b.conf[0]), 3)))

        # 1. Si no es una de las 3 especies reconocidas por el modelo
        if nombre_raw not in MAPA_ETIQUETAS:
            return Prediccion(
                especie="Objeto / Animal No Identificado",
                confianza=round(confianza, 3),
                es_invasora=False,
                tipo="Desconocido",
                riesgo="Bajo",
                descripcion="La imagen no coincide con las especies invasoras del modelo (Jabalí, Liebre europea o Rata gris).",
                alternativas=alternativas,
                simulado=False,
            )

        nombre_comun = MAPA_ETIQUETAS[nombre_raw]
        umbral_requerido = UMBRALES_POR_ESPECIE.get(nombre_raw, UMBRAL_DEFAULT)

        # 2. Si la confianza es inferior al umbral especifico de esa especie
        if confianza < umbral_requerido:
            alternativas.insert(0, (f"{nombre_comun} (coincidencia parcial)", round(confianza, 3)))
            return Prediccion(
                especie="No identificado (Confianza insuficiente)",
                confianza=round(confianza, 3),
                es_invasora=False,
                tipo="Desconocido",
                riesgo="Bajo",
                descripcion=f"Se detectó una posible coincidencia con '{nombre_comun}' al {confianza*100:.1f}%, pero requiere un mínimo del {umbral_requerido*100:.0f}% de certeza para confirmar. Te sugerimos tomar una foto más cercana o nítida.",
                alternativas=alternativas,
                simulado=False,
            )

        # 3. Detección válida y confirmada
        especies = cargar_especies()
        ficha = especies[especies["nombre_comun"].str.lower() == nombre_comun.lower()]

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
