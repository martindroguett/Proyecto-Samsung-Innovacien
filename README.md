# Proyecto Innovacien

**Especies invasoras en Chile** — análisis de datos, modelo de visión por computadora YOLO11 y
plataforma de reporte ciudadano.

Proyecto final del curso **Código y Programación**, Samsung Innovation Campus Chile 2026 — Cohort 2.

- **Aplicación publicada:** `PENDIENTE` (Streamlit Cloud — agregar URL antes de la entrega)
- **Integrantes:** Equipo Innovacien

---

## El alcance del proyecto: tres especies

El modelo de visión entrenado (`core/best.pt`, YOLO11s) reconoce **tres especies**, y solo tres:

| Etiqueta del modelo | Especie | Nombre científico | `speciesKey` GBIF |
|---|---|---|---|
| `jabali` | Jabalí | *Sus scrofa* | 7705930 |
| `liebre` | Liebre europea | *Lepus europaeus* | 7952072 |
| `rata gris` | Rata gris | *Rattus norvegicus* | 2439261 |

**Todo el proyecto se limita a estas tres.** El catálogo de la app, el mapa, los datos y el
análisis comparten exactamente el mismo alcance que el modelo: no analizamos especies que la app
no puede identificar, ni mostramos en el catálogo especies que el modelo no reconoce.

## Pregunta de análisis

> **¿Cómo se distribuye en Chile cada una de las tres especies invasoras que nuestro modelo
> identifica, y en qué se diferencian sus patrones territoriales?**

---

## 🤖 Modelo de Visión por Computadora (YOLO11)

Para automatizar la identificación de fauna invasora a partir de fotos tomadas por la ciudadanía,
implementamos un modelo de detección de objetos **YOLO11s** mediante Transfer Learning y
Fine-Tuning en Kaggle GPU T4.

### Características del Modelo

- **Dataset unificado y procesado:** **554 imágenes anotadas** y validadas con Bounding Boxes
  para **Jabalí** (*Sus scrofa*), **Liebre europea** (*Lepus europaeus*) y **Rata gris**
  (*Rattus norvegicus*).
- **Umbrales adaptativos por especie:**
  - 🐗 **Jabalí:** ≥ 80% (exigencia alta por tamaño y facilidad de reconocimiento).
  - 🐇 **Liebre europea:** ≥ 45% (umbral accesible para animales pequeños o en movimiento).
  - 🐀 **Rata gris:** ≥ 45% (umbral accesible para roedores pequeños y mimetizados).
- **Filtro de seguridad para Especies No Identificadas:** si la coincidencia es inferior al
  umbral o el animal no pertenece a las especies registradas, la app lo clasifica como
  `"Objeto / Especie No Identificada"` y **deshabilita el envío de alertas erróneas** a las
  autoridades.

### Métricas del entrenamiento

Leídas del propio checkpoint (`core/best.pt`, mejor época de 150, AdamW, `imgsz=640`):

| Métrica | Valor |
|---|---|
| Precision | 0,720 |
| Recall | 0,732 |
| mAP@50 | 0,736 |
| mAP@50-95 | 0,509 |

Son las agregadas de las tres clases; el desglose por especie requiere el set de validación, que
no está en el repositorio.

### Verificación con fotos reales

Probamos el modelo con fotos de GBIF tomadas en Chile, por la ruta completa de la app: **4 de 6
aciertos**. Los dos fallos son informativos y motivaron los umbrales adaptativos:

- Una **liebre** inequívoca fue clasificada como **jabalí con 0,711** de confianza. Con un umbral
  único de 50% habría pasado como detección confiable y generado un aviso al SAG por la especie
  equivocada. El umbral de 80% para jabalí bloquea exactamente este caso.
- Una **rata atropellada** en el pavimento no fue detectada (0,0). El set de entrenamiento tiene
  animales vivos en postura normal; fotografiar fauna muerta en la calle es un caso de uso real
  que todavía no está cubierto.

---

## 💻 Características de la Aplicación Streamlit

1. **🚨 Alertar animal (detección e inferencia en tiempo real):**
   - Inferencia instantánea de la imagen subida mediante `core/modelo.py` y `best.pt`.
   - **Desplegable interactivo de comunas:** selección dinámica según la región elegida.
   - **Geolocalización automática:** autocompletado de coordenadas GPS al seleccionar la comuna,
     con ajuste fino manual.
   - **Sincronización instantánea:** al registrar una alerta se guarda el reporte y se añade al
     mapa global (`data/avistamientos.csv`), invalidando la caché de Streamlit.

2. **📍 Registros en tu área (mapa PyDeck):**
   - **PyDeck ScatterplotLayer** con un punto por observación, coloreado **por especie**.
   - Filtros por **especie**, **entorno** (urbano/rural) y **fuente del registro**, con una
     advertencia visible cuando se mezclan fuentes (ver el hallazgo más abajo).
   - Cada punto es una observación puntual, no un área de afectación: con 49.133 registros
     reales, los círculos de 8 km del prototipo tapaban el mapa entero.

3. **📖 Catálogo de especies:**
   - Las tres fichas con **fotografías reales de GBIF tomadas en Chile** (licencia CC0 en las tres
     portadas) y métricas de cada especie calculadas por el pipeline.
   - Distintivo de riesgo sanitario **`☣️ Portador de enfermedades`** para vectores biológicos
     (jabalí y rata gris).

4. **🗂️ Mis reportes:** historial ciudadano de alertas y tickets generados.

5. **ℹ️ Acerca del proyecto:** metodología, estado del modelo y umbrales vigentes.

---

## Datos

### Fuente única: GBIF

Consultamos la API de ocurrencias por `speciesKey`, filtrando en origen por `country=CL` y
`hasCoordinate=true`.

- **49.165 registros** con coordenada, de 1907 a 2026, en 15 de las 17 regiones
- **Licencias:** CC-BY-NC 4.0 (48.703), CC-BY 4.0 (318), CC0 1.0 (144)
- **Publicadores principales:** CONAF (48.303), iNaturalist (336), Museo de Zoología de la
  Universidad de Concepción, MMA
- **Acceso:** GBIF Occurrence Search API, julio 2026

### Por qué el proyecto ya no usa GRIIS

Las versiones anteriores partían del **GRIIS Chile** (Global Register of Introduced and Invasive
Species) para descubrir cuáles de las 844 especies exóticas del país están declaradas invasoras, y
luego cruzarlas con GBIF.

Ese paso desapareció con el re-enfoque a tres especies, por una razón simple: **las especies ya
están fijadas por el modelo**. No hay nada que descubrir. Mantener GRIIS significaría descargar un
registro de 844 taxones, resolver 844 nombres contra la taxonomía de GBIF y descartar 841 filas.

Como beneficio secundario desaparece el problema que GRIIS causaba: sus sinónimos taxonómicos
desactualizados (*Neovison vison*, hoy *Neogale vison*). Consultar por `speciesKey` es inmune.

El material del enfoque anterior quedó archivado en [data/legacy/](data/legacy/) y
[notebooks/legacy/](notebooks/legacy/), sin borrarse.

---

## Hallazgo principal del análisis

### 1. El 98% de los datos son cámaras trampa, no observaciones de gente

**48.303 de los 49.165 registros (98,2%) provienen de un programa de monitoreo con cámaras trampa
de CONAF en áreas silvestres protegidas**, activo entre 2017 y 2023.

Eso invalida cualquier lectura ingenua del conjunto. Que "el 96% de los registros sea rural" no
describe a las especies: describe que **no se instalan cámaras trampa en ciudades**. Y el programa
no tiene **ni un solo registro de rata gris** — la especie más urbana de las tres es invisible
para la fuente que aporta casi todos los datos.

El mismo indicador, sobre la misma especie, cambia radicalmente según quién la observó:

| Registros en zona urbana | Jabalí | Liebre europea | Rata gris |
|---|---|---|---|
| Cámaras trampa (CONAF) | 0,0% *(n=3.114)* | 3,5% *(n=45.189)* | **sin datos** |
| Ciencia ciudadana (iNaturalist) | 13,5% *(n=37)* | 8,6% *(n=256)* | **55,8%** *(n=43)* |
| Colección museológica | sin datos | 6,5% *(n=31)* | 34,7% *(n=173)* |
| Otros estudios | 20,0% *(n=5)* | 1,0% *(n=302)* | 0,0% *(n=15)* |

Por eso **la fuente es una dimensión de primera clase** en el pipeline, todo resultado territorial
se reporta desagregado, y la app permite filtrar por ella con una advertencia visible. El sesgo no
se puede corregir con estos datos; lo que sí se puede es hacerlo imposible de ignorar.

### 2. La rata gris ocupa un nicho territorial distinto, y es la conclusión más sólida

Con un 98% de los datos viniendo de una fuente sesgada, la pregunta útil no es "¿qué dicen los
datos?" sino **"¿coinciden fuentes que no comparten metodología?"**.

La rata gris pasa ese test: ciencia ciudadana (iNaturalist, 2009–2026) y colecciones museológicas
(especímenes, 1907–2022) coinciden en un pico latitudinal en **−33°** (30% y 29% de sus registros
respectivamente). Son fuentes independientes, de épocas y métodos distintos, sin un mecanismo
común que las sesgue igual.

Es la única de las tres con presencia urbana mayoritaria (**55,8%**), la única concentrada en la
zona central y la única ausente del monitoreo en áreas protegidas. **Con apenas 231 registros —el
0,5% del total— es la conclusión más defendible del análisis.**

### 3. El jabalí muestra el problema en su forma más cruda

El **91%** de los 3.114 registros de jabalí de las cámaras trampa cae en **una única franja de 2°
de latitud**, en torno a −41°. Ninguna especie se distribuye así: ese pico describe un puñado de
cámaras en una zona acotada disparándose muchas veces.

La liebre europea, por su parte, cambia de mediana latitudinal en **14 grados** según la fuente
—de −33,7° en "otros estudios" a −47,1° en ciencia ciudadana—. Es imposible que ambas describan la
misma realidad biológica.

### Por qué importa para el producto

El análisis apunta directo a una decisión de diseño: **la rata gris es la especie donde una app de
reporte ciudadano aporta información que hoy no existe**. Es la que un ciudadano efectivamente se
encuentra y fotografía en una ciudad, y justo la que el monitoreo institucional no cubre. También
es la que menos datos tiene, así que es la que más se beneficia de cada foto nueva.

Para el jabalí y la liebre, en cambio, la app duplicaría lo que las cámaras trampa ya registran
mucho mejor.

Hay una tensión que conviene tener presente: la rata gris es también **la clase más débil del
modelo** (en la verificación, una detección a 0,21 y otra fallida). La especie más valiosa para el
producto es la que peor reconoce hoy.

---

## Notebooks

| Notebook | Contenido |
|---|---|
| [01_obtencion_y_limpieza.ipynb](notebooks/01_obtencion_y_limpieza.ipynb) | Fuente, descarga por `speciesKey`, limpieza auditable, asignación geográfica y el descubrimiento del sesgo de fuente |
| [02_analisis_territorial.ipynb](notebooks/02_analisis_territorial.ipynb) | 6 visualizaciones, análisis desagregado por fuente, respuesta a la pregunta y límites |

Ambos están ejecutados, con salidas y gráficos incluidos. Versiones HTML en
[notebooks/html/](notebooks/html/).

### Decisiones metodológicas documentadas

| # | Problema | Solución |
|---|---|---|
| 1 | GRIIS ya no aporta: las especies están fijadas por el modelo | Eliminado el registro y el emparejamiento taxonómico; `speciesKey` directo |
| 2 | Sinónimos taxonómicos | Desaparece al consultar por `speciesKey` en vez de por nombre |
| 3 | `eventDate` en 5 formatos; pandas infiere uno y descarta el resto en silencio | Recorte a los 10 primeros caracteres + formato explícito (rescató 48.935 registros) |
| 4 | `stateProvince` de GBIF sucio e inconsistente | No se usa: región y comuna se derivan de la coordenada |
| 5 | Comunas del sur enormes: la comuna asignada queda a 34 km de mediana | Marcada como poco confiable; se agrega por región, no por comuna |
| 6 | Registros de ausencia contarían como avistamientos | Filtrados por `occurrenceStatus` |
| 7 | **98% de los datos son cámaras trampa de CONAF en áreas protegidas** | **`fuente` como dimensión de primera clase; todo resultado desagregado** |
| 8 | Desbalance de 198:1 entre liebre y rata gris | Escala logarítmica y `n=` visible en cada barra; nunca se comparan volúmenes absolutos |
| 9 | Territorio insular distorsionaría el análisis latitudinal | Marcado en `territorio` (resultó ser 1 solo registro) |
| 10 | La paleta natural de la marca falla como código de categorías | Paleta de especie verificada para contraste y daltonismo; la marca viste la UI, los datos usan colores validados |

### Limitaciones declaradas

- **El sesgo de muestreo no se corrige, solo se declara.** No hay forma de estimar la distribución
  real de las especies con estos datos.
- **Los datos miden presencia observada, no abundancia.** 45.778 registros de liebre contra 231 de
  rata gris no significan que haya 198 veces más liebres.
- **No hay análisis de tendencia temporal.** La ventana 2017–2023 es la del programa de cámaras,
  no la de la invasión.
- **La ausencia no prueba ausencia.** Que no haya jabalíes registrados en el norte puede
  significar que nadie está observando.
- Las zonas urbanas se aproximan con círculos (centro + radio), no con límites reales.
- Los porcentajes calculados sobre `n < 40` se reportan siempre con su tamaño de muestra.

---

## Correr el proyecto localmente

```bash
python -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate

# 1. Dependencias de la aplicación
pip install -r requirements.txt

# 2. Ejecutar la aplicación
streamlit run app.py               # http://localhost:8501

# 3. (Opcional) Herramientas para los notebooks
pip install -r requirements-dev.txt
jupyter lab notebooks/
```

Los datos procesados ya vienen en `data/procesado/`. Para regenerarlos:

```bash
python -m core.ingesta             # descarga (con caché), limpia y publica para la app
```

La descarga cruda queda en caché en `data/crudo/`, así que una segunda ejecución es instantánea.
La primera toma varios minutos: son ~165 peticiones paginadas solo para la liebre, y GBIF se
vuelve lento con offsets altos.

> **Nota sobre PyTorch.** `ultralytics` arrastra `torch`, que no tiene wheels para todas las
> versiones de Python. Verificado funcionando en **Python 3.13** con torch 2.13.

### Notas para el despliegue en Streamlit Cloud

Tres cosas que hacen fallar el despliegue si no se configuran:

1. **`torch` en versión solo-CPU.** `requirements.txt` incluye
   `--extra-index-url https://download.pytorch.org/whl/cpu`. Sin eso, pip instala la build con
   CUDA (~2,5 GB de wheels) y el build revienta por espacio o timeout.
2. **`packages.txt` con `libgl1`.** `ultralytics` depende de `opencv-python`, que necesita
   `libGL.so.1` — ausente en ese contenedor. Sin esto la app arranca y muere con `ImportError`.
   (Declarar `opencv-python-headless` no sirve: `ultralytics` exige `opencv-python`.)
3. **Memoria.** El pico medido es ~615 MB (modelo cargado + una inferencia + los avistamientos), y
   con el runtime de Streamlit ronda los 750 MB. El tier gratuito da ~1 GB: entra, pero con poco
   margen. Si el contenedor se reinicia por memoria, la salida es muestrear
   `data/avistamientos.csv` para la app y dejar el dataset completo solo para los notebooks.

---

## Estructura del Código

```
app.py                       # Entrada principal: tema, barra lateral y navegación por pestañas
core/
  best.pt                    # Pesos entrenados del modelo YOLO11s (19,1 MB)
  modelo.py                  # Inferencia en tiempo real con YOLO11s y umbrales adaptativos
  ingesta.py                 # Descarga desde GBIF, limpieza, geografía y tablas de análisis
  comunas.py                 # 346 comunas de Chile con coordenadas GPS, por región
  datos.py                   # Carga de datos, búsqueda por radio vectorizada, sincronización
  autoridades.py             # Generación de tickets y derivación a SAG / CONAF / SERNAPESCA / MMA
  ubicacion.py               # Zona del usuario con callbacks de coordenadas automáticas
  theme.py                   # Paleta de la marca + colores de especie validados
views/
  alertar.py                 # Pestaña 1: Foto → Inferencia IA → Comuna / Coordenadas → Alerta
  cerca.py                   # Pestaña 2: Mapa PyDeck por especie y filtros por fuente
  catalogo.py                # Pestaña 3: Las tres fichas con fotos reales de GBIF
  reportes.py                # Pestaña 4: Historial ciudadano de alertas y tickets
  acerca.py                  # Pestaña 5: Descripción, metodología y umbrales vigentes
notebooks/
  01_obtencion_y_limpieza.ipynb
  02_analisis_territorial.ipynb
  html/                      # Versiones exportadas
  legacy/                    # El análisis urbano del enfoque anterior (GRIIS, 812 especies)
data/
  especies.csv               # Las 3 fichas del catálogo (generado)
  avistamientos.csv          # 49.133 registros de GBIF + los que envía la app (generado)
  zonas_urbanas.csv          # 30 zonas urbanas con centro y radio
  crudo/                     # Caché de la descarga de GBIF
  procesado/                 # Resultado de la ingesta y del análisis
  legacy/                    # Datasets del enfoque GRIIS, archivados
requirements.txt             # Dependencias de la app (lo que instala Streamlit Cloud)
requirements-dev.txt         # Herramientas de notebooks
packages.txt                 # Librerías de sistema para Streamlit Cloud (libgl1)
```

---

## Estado del Proyecto

- [x] Entrenamiento e integración del modelo **YOLO11s** real (`core/modelo.py` + `best.pt`).
- [x] **Umbrales adaptativos por especie** y fallback de especie no identificada.
- [x] Selección dinámica de **comunas de Chile** y coordenadas GPS automáticas (`core/comunas.py`).
- [x] Mapa **PyDeck** coloreado por especie con filtros por fuente (`views/cerca.py`).
- [x] Catálogo con **fotografías reales de GBIF** e insignias de portador de enfermedades.
- [x] Sincronización automática de alertas con la base de avistamientos (`core/datos.py`).
- [x] **Re-enfoque a tres especies:** pipeline GBIF sin GRIIS, notebooks y datos regenerados.
- [ ] Publicar en Streamlit Cloud y agregar la URL oficial al README.
- [ ] Evaluar el modelo con un set de prueba independiente y reportar métricas **por clase**.
- [ ] Ampliar el set de entrenamiento, sobre todo de rata gris (la clase más débil).
- [ ] Confirmar los canales oficiales de aviso con SAG.
- [ ] Integrar la rama `catalogo` (renombre riesgo → impacto ambiental), aún sin mergear.
- [ ] Decidir si `data/crudo/` (18 MB de caché regenerable) debe ir al repositorio.
