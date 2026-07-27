# Proyecto Innovacien

**Especies invasoras en las ciudades de Chile** — análisis de datos y plataforma de reporte ciudadano.

Proyecto final del curso **Código y Programación**, Samsung Innovation Campus Chile 2026 — Cohort 2.

- **Aplicación publicada:** `PENDIENTE` (Streamlit Cloud — agregar URL antes de la entrega)
- **Integrantes:** `PENDIENTE` (completar con nombres del equipo)

---

## Pregunta de análisis

> **¿Qué zonas urbanas de Chile se ven más afectadas por especies invasoras dañinas, y por cuáles?**

## Hallazgo principal

Analizamos **175.379 registros fotográficos** de plantas y animales tomados por personas
comunes en 30 zonas urbanas de Chile, cruzados con el registro oficial de especies invasoras
del país. Encontramos tres cosas:

**1. Hay una franja del país claramente más invadida.** En Melipilla, Chillán, Talca y
Rancagua, entre el **22% y el 36%** de las fotos de naturaleza corresponde a una especie que
no es chilena. En Arica es el **0,6%**. La causa es climática: casi todas estas especies
llegaron de Europa, y el centro de Chile tiene el mismo clima mediterráneo del que vinieron.
El desierto del norte y el frío del sur funcionan como barreras.

**2. Una especie está en casi todo el país, y otra solo en Santiago.** El **abejorro europeo**
(*Bombus terrestris*) aparece en 26 de las 30 zonas y está desplazando al abejorro nativo
chileno. La **cotorra argentina** (*Myiopsitta monachus*) concentra el **88% de sus registros
nacionales en el Gran Santiago**: una invasión puramente metropolitana.

**3. El registro oficial mira el campo, no la ciudad.** De las 20 especies exóticas más
fotografiadas en ciudades, **solo 10 están declaradas invasoras**. Las no declaradas aportan
el **45%** de los registros. Por grupo, los peces están evaluados en un 96% y los caracoles
en un 94%, pero las plantas con flor —la mayoría de lo que se fotografía en la ciudad— solo
en un 42%.

**Por qué importa.** El monitoreo chileno está diseñado para el bosque nativo y las áreas
protegidas. Pero la ciudad es la puerta de entrada: mascotas que se escapan, plantas de
jardín que se asilvestran, especies que viajan en la carga. El reporte ciudadano con foto y
ubicación no es un complemento del monitoreo oficial — es la única fuente que hoy cubre ese
vacío. De ahí nace la aplicación.

---

## Datos

### 1. GRIIS Chile — qué especies son invasoras

Registro oficial de especies exóticas e invasoras de Chile. **844 taxones**, de los cuales
**246 están declarados invasores**. Aporta taxonomía, hábitat y el estado de invasión. No
tiene geografía interna ni fechas.

- **Licencia:** CC-BY 4.0
- **DOI:** [10.15468/n4ofia](https://doi.org/10.15468/n4ofia)
- **Cita:** Pauchard A, Sánchez P, Aldridge D, Díaz G M, Soto Volkart N, Skewes O, Wong L J,
  Pagad S (2020). *Global Register of Introduced and Invasive Species — Chile*. Version 2.7.
  Invasive Species Specialist Group ISSG.

### 2. GBIF / iNaturalist — dónde fue vista cada una

**571.091 registros fotográficos georreferenciados** en Chile. Cada registro es una foto
tomada por una persona, con coordenadas, fecha y especie validada por la comunidad. La
mayoría proviene de iNaturalist (494.783 registros).

- **Licencias:** CC-BY-NC 4.0 (434.577), CC-BY 4.0 (97.113), CC0 1.0 (39.400)
- **DOI:** [10.15468/ab3s5x](https://doi.org/10.15468/ab3s5x)
- **Cita:** iNaturalist contributors, iNaturalist (2026). *iNaturalist Research-grade
  Observations*. iNaturalist.org. Acceso vía GBIF Occurrence Search API, julio 2026.

### Métrica central

$$\text{presión de invasión} = \frac{\text{registros de especies exóticas}}{\text{registros totales de la zona}}$$

La proporción es necesaria porque el conteo bruto mide **cuánta gente saca fotos**, no cuánta
invasión hay: Santiago tiene 48.832 registros y Curicó 935. Como el esfuerzo de observación
afecta al numerador y al denominador por igual, se cancela.

---

## Notebooks

| Notebook | Contenido |
|---|---|
| [01_obtencion_y_limpieza.ipynb](notebooks/01_obtencion_y_limpieza.ipynb) | Fuentes, descarga vía API, emparejamiento taxonómico, definición de zonas urbanas y los 9 problemas de limpieza resueltos |
| [02_analisis_urbano.ipynb](notebooks/02_analisis_urbano.ipynb) | Indicadores, 6 visualizaciones, hallazgos y limitaciones |

Ambos están ejecutados con sus salidas y gráficos incluidos.

### Decisiones metodológicas documentadas

| # | Problema | Solución |
|---|---|---|
| 1 | GRIIS no tiene región ni fecha | Cruce con GBIF, que sí tiene coordenadas |
| 2 | Nombres con autoría (`"Acacia dealbata Link"`) | Extracción del binomio género + especie |
| 3 | Sinónimos antiguos (`Helix aspersa` → `Cornu aspersum`) | Emparejamiento por `speciesKey`, no por texto |
| 4 | `isInvasive` vacío en 598 filas | Separar "exótica" de "invasora declarada" |
| 5 | Conurbaciones se contarían dos veces | Gran Valparaíso, Gran Concepción y Gran La Serena unidos |
| 6 | Ciudades de distinto tamaño | Radio proporcional, verificado sin solapes |
| 7 | Más observadores ≠ más invasión | Normalización por registros totales de la zona |
| 8 | Zonas con muy pocos datos | Umbral de 500 registros, exclusiones reportadas |
| 9 | `stateProvince` sucio en GBIF | No se usa: la zona se asigna por coordenadas |

### Limitaciones declaradas

- **Sesgo de fotografiabilidad:** las exóticas son más fáciles de fotografiar, así que las
  proporciones probablemente están infladas. Lo comparable es el orden entre ciudades.
- **"No declarada invasora" ≠ "inofensiva"**, significa no evaluada.
- Las zonas urbanas se aproximan con círculos, no con límites reales.
- Medimos **presencia**, no abundancia.

---

## Correr el proyecto

```bash
pip install -r requirements.txt

# Aplicación
streamlit run app.py          # http://localhost:8501

# Notebooks
jupyter lab notebooks/
```

Los datos procesados ya vienen en `data/procesado/`. Para volver a descargarlos desde las
APIs (~3 minutos), poner `FORZAR_DESCARGA = True` en el notebook 01 o ejecutar:

```bash
python -m core.ingesta
```

## Estructura

```
app.py                    # entrada: tema, barra lateral y pestañas
notebooks/
  01_obtencion_y_limpieza.ipynb
  02_analisis_urbano.ipynb
core/
  ingesta.py              # descarga desde GRIIS y GBIF
  datos.py                # carga de CSV, búsqueda por radio, reportes
  theme.py                # paleta de colores naturales
  modelo.py               # clasificador de fotos (simulado)
  autoridades.py          # envío de alertas (simulado)
  ubicacion.py            # zona del usuario
views/
  alertar.py              # pestaña principal: foto → especie → aviso
  cerca.py                # especies invasoras en tu área
  catalogo.py             # catálogo de especies
  reportes.py             # historial de reportes
  acerca.py               # descripción del proyecto
data/
  zonas_urbanas.csv       # 30 zonas con centro y radio
  crudo/                  # archivo GRIIS descargado
  procesado/              # resultado de la ingesta y del análisis
```

## Pendientes antes de la entrega

- [ ] Conectar la app a `data/procesado/` (hoy usa datos de ejemplo)
- [ ] Publicar en Streamlit Cloud y poner la URL arriba
- [ ] Completar integrantes
- [ ] Mover a `/proyectos/nombre-del-equipo/` en el repo del curso para el Pull Request
- [ ] Definir qué hacemos con la detección por foto (modelo de Hugging Face)
