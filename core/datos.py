"""Carga y consulta de datos: catalogo de especies, avistamientos y reportes.

Los CSV de data/ son DATOS DE EJEMPLO para poder maquetar la app.
TODO (equipo): reemplazar por los datos reales / base de datos definitiva.
"""

from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
DIR_DATOS = RAIZ / "data"
DIR_SUBIDAS = DIR_DATOS / "subidas"

CSV_ESPECIES = DIR_DATOS / "especies.csv"
CSV_AVISTAMIENTOS = DIR_DATOS / "avistamientos.csv"
CSV_REPORTES = DIR_DATOS / "reportes.csv"

TIPOS = ["Animal", "Insecto", "Planta"]
NIVELES_RIESGO = ["Alto", "Medio", "Bajo"]

# Punto de referencia por region, para centrar el mapa mientras no tengamos
# geolocalizacion del navegador.
REGIONES = {
    "Arica y Parinacota": (-18.478, -70.321),
    "Tarapaca": (-20.214, -70.152),
    "Antofagasta": (-23.650, -70.400),
    "Atacama": (-27.366, -70.332),
    "Coquimbo": (-29.903, -71.251),
    "Valparaiso": (-33.046, -71.620),
    "Metropolitana": (-33.447, -70.660),
    "O'Higgins": (-34.171, -70.740),
    "Maule": (-35.426, -71.655),
    "Nuble": (-36.606, -72.103),
    "Biobio": (-36.827, -73.050),
    "Araucania": (-38.739, -72.598),
    "Los Rios": (-39.814, -73.245),
    "Los Lagos": (-41.471, -72.936),
    "Chiloe": (-42.482, -73.763),
    "Aysen": (-45.572, -72.068),
    "Magallanes": (-53.163, -70.917),
}


# --------------------------------------------------------------------------
# Lectura
# --------------------------------------------------------------------------
@st.cache_data
def cargar_especies() -> pd.DataFrame:
    """Catalogo de especies invasoras."""
    return pd.read_csv(CSV_ESPECIES)


@st.cache_data
def cargar_avistamientos() -> pd.DataFrame:
    """Avistamientos con los datos de la especie ya unidos."""
    av = pd.read_csv(CSV_AVISTAMIENTOS, parse_dates=["fecha"])
    esp = cargar_especies()
    return av.merge(esp, left_on="especie_id", right_on="id", suffixes=("", "_esp"))


def cargar_reportes() -> pd.DataFrame:
    """Reportes enviados desde la app. Vacio si aun no hay ninguno."""
    columnas = ["ticket", "fecha_hora", "especie", "confianza", "tipo", "riesgo",
                "region", "comuna", "lat", "lon", "autoridad", "estado",
                "contacto", "comentario", "imagen"]
    if not CSV_REPORTES.exists():
        return pd.DataFrame(columns=columnas)
    return pd.read_csv(CSV_REPORTES)


# --------------------------------------------------------------------------
# Escritura
# --------------------------------------------------------------------------
def guardar_reporte(reporte: dict) -> None:
    """Agrega un reporte al CSV local de reportes y sincroniza con avistamientos.csv."""
    df = pd.DataFrame([reporte])
    existe = CSV_REPORTES.exists()
    df.to_csv(CSV_REPORTES, mode="a", header=not existe, index=False)

    # Sincronizar automaticamente el nuevo reporte en avistamientos.csv
    try:
        guardar_avistamiento(
            especie_nombre_o_id=reporte.get("especie", ""),
            region=reporte.get("region", ""),
            comuna=reporte.get("comuna", ""),
            lat=float(reporte.get("lat", 0) or 0),
            lon=float(reporte.get("lon", 0) or 0),
            fecha=datetime.now().strftime("%Y-%m-%d"),
            estado="En revision",
        )
    except Exception:
        pass


def guardar_avistamiento(especie_nombre_o_id: str | int, region: str, comuna: str,
                        lat: float, lon: float, fecha: str = "", estado: str = "En revision") -> dict:
    """Agrega un nuevo registro a data/avistamientos.csv y refresca la cache de Streamlit."""
    especie_id = None
    if isinstance(especie_nombre_o_id, int) or (isinstance(especie_nombre_o_id, str) and especie_nombre_o_id.isdigit()):
        especie_id = int(especie_nombre_o_id)
    else:
        info = especie_por_nombre(str(especie_nombre_o_id))
        especie_id = info["id"] if info else None

    # Si la especie no se encuentra en el catalogo, se asigna 1 por defecto
    if especie_id is None:
        especie_id = 1

    if not fecha:
        fecha = datetime.now().strftime("%Y-%m-%d")

    # Obtener el siguiente ID unico
    if CSV_AVISTAMIENTOS.exists():
        df_existente = pd.read_csv(CSV_AVISTAMIENTOS)
        nuevo_id = int(df_existente["id"].max() + 1) if not df_existente.empty else 1
    else:
        nuevo_id = 1

    nuevo_avistamiento = {
        "id": nuevo_id,
        "especie_id": especie_id,
        "region": region,
        "comuna": comuna,
        "lat": round(lat, 4),
        "lon": round(lon, 4),
        "fecha": fecha,
        "estado": estado,
    }

    df = pd.DataFrame([nuevo_avistamiento])
    existe = CSV_AVISTAMIENTOS.exists()
    df.to_csv(CSV_AVISTAMIENTOS, mode="a", header=not existe, index=False)

    # Invalida el cache para que el mapa y los componentes de Streamlit muestren los nuevos datos de inmediato
    cargar_avistamientos.clear()

    return nuevo_avistamiento


def guardar_imagen(archivo, prefijo: str = "obs") -> str:
    """Guarda la foto subida en data/subidas/ y devuelve la ruta relativa."""
    DIR_SUBIDAS.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d-%H%M%S")
    nombre = f"{prefijo}-{marca}-{archivo.name}".replace(" ", "_")
    destino = DIR_SUBIDAS / nombre
    destino.write_bytes(archivo.getvalue())
    return str(destino.relative_to(RAIZ))


# --------------------------------------------------------------------------
# Consultas geograficas
# --------------------------------------------------------------------------
def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia en km entre dos coordenadas (formula de haversine)."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


def avistamientos_cerca(lat: float, lon: float, radio_km: float = 150.0) -> pd.DataFrame:
    """Avistamientos dentro de un radio, ordenados del mas cercano al mas lejano."""
    df = cargar_avistamientos().copy()
    df["distancia_km"] = df.apply(
        lambda f: distancia_km(lat, lon, f["lat"], f["lon"]), axis=1
    ).round(1)
    return df[df["distancia_km"] <= radio_km].sort_values("distancia_km").reset_index(drop=True)


def especie_por_nombre(nombre: str) -> dict | None:
    """Busca una especie del catalogo por su nombre comun."""
    esp = cargar_especies()
    fila = esp[esp["nombre_comun"].str.lower() == nombre.lower()]
    return None if fila.empty else fila.iloc[0].to_dict()
