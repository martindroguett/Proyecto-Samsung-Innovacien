"""Obtencion de los datos reales del proyecto desde GBIF.

Fuentes (ambas abiertas, con DOI y licencia verificable):

  1. GRIIS Chile — Global Register of Introduced and Invasive Species, Chile.
     Pauchard A, Sanchez P, Aldridge D, Diaz G M, Soto Volkart N, Skewes O,
     Wong L J, Pagad S (2020). Version 2.7. Invasive Species Specialist Group ISSG.
     DOI: 10.15468/n4ofia — Licencia CC-BY 4.0.
     Aporta: QUE especies son exoticas/invasoras en Chile. No trae fecha ni region.

  2. GBIF — registros de ocurrencia con fotografia en Chile (mayoritariamente
     iNaturalist Research-grade Observations, DOI 10.15468/ab3s5x, CC-BY-NC 4.0).
     Aporta: DONDE y CUANDO se fotografio cada especie, con coordenadas.

La union de ambas responde la pregunta del proyecto: que zonas urbanas de Chile
concentran mas registros de especies invasoras, y de cuales.

Uso desde el notebook:

    from core.ingesta import ejecutar_ingesta
    ejecutar_ingesta()          # descarga y deja los CSV en data/procesado/
"""

from __future__ import annotations

import io
import json
import time
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DIR_DATOS = RAIZ / "data"
DIR_CRUDO = DIR_DATOS / "crudo"
DIR_PROC = DIR_DATOS / "procesado"

URL_GRIIS = "https://cloud.gbif.org/griis/archive.do?r=chile-griis-gbif"
API = "https://api.gbif.org/v1"

# Filtros comunes: Chile, con coordenada y con fotografia.
FILTRO_BASE = "country=CL&hasCoordinate=true&hasGeospatialIssue=false&mediaType=StillImage"

CSV_ZONAS = DIR_DATOS / "zonas_urbanas.csv"


# --------------------------------------------------------------------------
# Utilidades HTTP
# --------------------------------------------------------------------------
def _get(url: str, intentos: int = 3) -> dict:
    """GET con reintentos. La API de GBIF ocasionalmente corta la conexion."""
    for i in range(intentos):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception:
            if i == intentos - 1:
                raise
            time.sleep(2 * (i + 1))
    return {}


# --------------------------------------------------------------------------
# Paso 1 — catalogo GRIIS Chile
# --------------------------------------------------------------------------
def descargar_griis() -> pd.DataFrame:
    """Descarga el archivo Darwin Core de GRIIS Chile y lo devuelve como tabla."""
    DIR_CRUDO.mkdir(parents=True, exist_ok=True)
    destino = DIR_CRUDO / "griis_chile.zip"

    if not destino.exists():
        with urllib.request.urlopen(URL_GRIIS, timeout=120) as r:
            destino.write_bytes(r.read())

    with zipfile.ZipFile(destino) as z:
        leer = lambda n: pd.read_csv(io.BytesIO(z.read(n)), sep="\t", dtype=str)
        tax = leer("taxon.txt")
        perfil = leer("speciesprofile.txt")
        dist = leer("distribution.txt")

    df = tax.merge(perfil, on="id", how="left").merge(dist, on="id", how="left")

    # El nombre GRIIS incluye la autoria ("Acacia dealbata Link"); GBIF necesita
    # solo el binomio genero + especie para el emparejamiento taxonomico.
    df["binomio"] = df["scientificName"].str.split().str[:2].str.join(" ")

    # isInvasive viene vacio para las exoticas que aun no se declaran invasoras.
    df["invasora"] = df["isInvasive"].eq("invasive")

    return df


# --------------------------------------------------------------------------
# Paso 2 — emparejar nombres GRIIS con la taxonomia de GBIF
# --------------------------------------------------------------------------
def _match_uno(fila: tuple[str, str]) -> dict:
    binomio, reino = fila
    url = (f"{API}/species/match?name={urllib.parse.quote(binomio)}"
           f"&kingdom={urllib.parse.quote(reino)}&strict=false")
    try:
        r = _get(url)
    except Exception:
        r = {}
    return {
        "binomio": binomio,
        "speciesKey": r.get("speciesKey"),
        "matchType": r.get("matchType", "NONE"),
        "confidence": r.get("confidence"),
        "nombre_gbif": r.get("scientificName"),
    }


def emparejar_con_gbif(griis: pd.DataFrame, hilos: int = 8) -> pd.DataFrame:
    """Resuelve cada nombre de GRIIS al speciesKey de GBIF.

    Es necesario porque GRIIS trae sinonimos ('Neovison vison' hoy es
    'Neogale vison'): buscar por texto perderia registros, buscar por
    speciesKey los recupera todos.
    """
    pares = list(zip(griis["binomio"], griis["kingdom"]))
    with ThreadPoolExecutor(max_workers=hilos) as ex:
        res = list(ex.map(_match_uno, pares))
    return pd.DataFrame(res).drop_duplicates("binomio")


# --------------------------------------------------------------------------
# Paso 3 — conteos por zona urbana
# --------------------------------------------------------------------------
def _facetas_zona(zona: pd.Series, claves: list[int], tam_lote: int = 120) -> pd.DataFrame:
    """Registros con foto por especie dentro del radio de una zona urbana.

    Se consulta en lotes de taxonKey porque la URL tiene largo limitado.
    Usar facetas en vez de descargar registros uno por uno baja el costo de
    miles de peticiones a unas pocas decenas.
    """
    geo = f"geoDistance={zona.lat},{zona.lon},{int(zona.radio_km)}km"
    filas = []
    for i in range(0, len(claves), tam_lote):
        lote = claves[i:i + tam_lote]
        taxones = "".join(f"&taxonKey={int(k)}" for k in lote)
        url = (f"{API}/occurrence/search?{FILTRO_BASE}&{geo}{taxones}"
               f"&facet=speciesKey&facetLimit=1000&limit=0")
        d = _get(url)
        for c in (d.get("facets") or [{}])[0].get("counts", []):
            filas.append({"zona": zona.zona, "speciesKey": int(c["name"]),
                          "registros": c["count"]})
    return pd.DataFrame(filas)


def _total_zona(zona: pd.Series) -> int:
    """Total de registros con foto de la zona, de cualquier especie.

    Es el denominador que nos permite comparar ciudades: sin el, una ciudad
    con muchos observadores parece mas invadida solo por tener mas gente
    subiendo fotos.
    """
    geo = f"geoDistance={zona.lat},{zona.lon},{int(zona.radio_km)}km"
    return _get(f"{API}/occurrence/search?{FILTRO_BASE}&{geo}&limit=0")["count"]


# --------------------------------------------------------------------------
# Paso 4 — muestra de registros con foto (para el catalogo de la app)
# --------------------------------------------------------------------------
def muestra_registros(claves: list[int], por_especie: int = 3) -> pd.DataFrame:
    """Trae algunos registros reales con URL de foto, para ilustrar el catalogo."""
    filas = []
    for k in claves:
        url = (f"{API}/occurrence/search?{FILTRO_BASE}&taxonKey={int(k)}"
               f"&limit={por_especie}")
        try:
            d = _get(url)
        except Exception:
            continue
        for r in d.get("results", []):
            medios = r.get("media") or []
            filas.append({
                "speciesKey": k,
                "nombre_gbif": r.get("species"),
                "lat": r.get("decimalLatitude"),
                "lon": r.get("decimalLongitude"),
                "anio": r.get("year"),
                "region_gbif": r.get("stateProvince"),
                "licencia": r.get("license"),
                "foto_url": medios[0].get("identifier") if medios else None,
                "gbif_id": r.get("key"),
            })
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------
# Orquestacion
# --------------------------------------------------------------------------
def ejecutar_ingesta(verbose: bool = True) -> dict[str, pd.DataFrame]:
    """Ejecuta la ingesta completa y guarda los CSV en data/procesado/."""
    log = print if verbose else (lambda *a, **k: None)
    DIR_PROC.mkdir(parents=True, exist_ok=True)

    log("1/5 Descargando catalogo GRIIS Chile…")
    griis = descargar_griis()
    log(f"     {len(griis)} taxones exoticos, {int(griis.invasora.sum())} marcados invasores")

    log("2/5 Emparejando nombres con la taxonomia de GBIF…")
    match = emparejar_con_gbif(griis)
    catalogo = griis.merge(match, on="binomio", how="left")
    catalogo = catalogo[catalogo["speciesKey"].notna()].copy()
    catalogo["speciesKey"] = catalogo["speciesKey"].astype(int)
    catalogo = catalogo.drop_duplicates("speciesKey")
    log(f"     {len(catalogo)} especies con speciesKey resuelto")

    claves = catalogo["speciesKey"].tolist()
    zonas = pd.read_csv(CSV_ZONAS)

    log(f"3/5 Consultando {len(zonas)} zonas urbanas…")
    partes, totales = [], []
    for _, z in zonas.iterrows():
        partes.append(_facetas_zona(z, claves))
        totales.append({"zona": z.zona, "registros_totales": _total_zona(z)})
        log(f"     {z.zona}")
    zonas_especies = pd.concat(partes, ignore_index=True)
    zonas_resumen = zonas.merge(pd.DataFrame(totales), on="zona")

    log("4/5 Muestra de fotos para el catalogo…")
    presentes = (zonas_especies.groupby("speciesKey").registros.sum()
                 .sort_values(ascending=False).head(60).index.tolist())
    fotos = muestra_registros(presentes)

    log("5/5 Guardando en data/procesado/…")
    salidas = {
        "catalogo_especies": catalogo,
        "zonas_especies": zonas_especies,
        "zonas_resumen": zonas_resumen,
        "fotos_muestra": fotos,
    }
    for nombre, df in salidas.items():
        df.to_csv(DIR_PROC / f"{nombre}.csv", index=False)
        log(f"     {nombre}.csv  ({len(df)} filas)")

    return salidas


if __name__ == "__main__":
    ejecutar_ingesta()
