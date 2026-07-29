# Proyecto Innovacien

**Especies invasoras en las ciudades de Chile** — Análisis de datos, modelo de visión por computadora YOLO11 y plataforma de reporte ciudadano.

Proyecto final del curso **Código y Programación**, Samsung Innovation Campus Chile 2026 — Cohort 2.

- **Aplicación publicada:** `PENDIENTE` (Streamlit Cloud — agregar URL antes de la entrega)
- **Integrantes:** Equipo Innovacien

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

---

## 🤖 Modelo de Visión por Computadora (YOLO11)

Para automatizar la identificación de fauna invasora a partir de fotos tomadas por la ciudadanía, implementamos un modelo de detección de objetos **YOLO11s** mediante Transfer Learning y Fine-Tuning en Kaggle GPU T4.

### Características del Modelo
- **Dataset unificado y procesado:** **554 imágenes anotadas** y validadas con Bounding Boxes para **Jabalí** (*Sus scrofa*), **Liebre europea** (*Lepus europaeus*) y **Rata gris** (*Rattus norvegicus*).
- **Umbrales adaptativos por especie:**
  - 🐗 **Jabalí:** ≥ 80% (exigencia alta por tamaño y facilidad de reconocimiento).
  - 🐇 **Liebre europea:** ≥ 45% (umbral accesible para animales pequeños o en movimiento).
  - 🐀 **Rata gris:** ≥ 45% (umbral accesible para roedores pequeños y mimetizados).
- **Filtro de seguridad para Especies No Identificadas:** Si la coincidencia es inferior al umbral o el animal no pertenece a las especies invasoras registradas, la app lo clasifica como `"Objeto / Especie No Identificada"` y deshabilita el envío de alertas erróneas a las autoridades.

---

## 💻 Características de la Aplicación Streamlit

1. **🚨 Alertar animal (Detección e Inferencia en Tiempo Real):**
   - Inferencia instantánea de la imagen subida mediante `core/modelo.py` y `best.pt`.
   - **Desplegable interactivo de Comunas:** Selección dinámica de comunas según la Región elegida.
   - **Geolocalización automática:** Autocompletado de coordenadas GPS (Latitud/Longitud) al seleccionar la comuna, con opción de ajuste fino manual.
   - **Sincronización instantánea:** Al registrar una alerta, se guarda el reporte y se añade de inmediato al mapa global de avistamientos (`data/avistamientos.csv`), invalidando la caché de Streamlit para actualización inmediata.

2. **📍 Especies invasoras en tu área (Mapa PyDeck de Áreas de Afección):**
   - Visualización con **PyDeck Scatterplot Layer**: círculos con contorno sólido y relleno transparente (Alpha 35) que permiten apreciar el terreno y el área de afección sin tapar la geografía.
   - Filtros dinámicos por **Tipo** (Animal, Insecto, Planta), **Riesgo** (Alto, Medio, Bajo), **Estado** (Confirmado, En revisión) y **Especie específica** (en contenedor desplegable limpio).

3. **📖 Catálogo de Especies:**
   - Fichas informativas con **fotografías de referencia HD** por especie.
   - Distinctivo de riesgo sanitario: **`☣️ Portador de enfermedades`** para especies clasificadas como vectores biológicos (Jabalí, Rata gris, Visón americano).

---

## Datos y Métricas

### Fuentes
- **GRIIS Chile:** Registro oficial de 844 taxones exóticos/invasores.
- **GBIF / iNaturalist:** 571.091 observaciones georreferenciadas con fotos validadas en Chile.

### Métrica central

$$\text{presión de invasión} = \frac{\text{registros de especies exóticas}}{\text{registros totales de la zona}}$$

---

## Estructura del Código

```
app.py                    # Entrada principal: tema, barra lateral y navegación por pestañas
core/
  modelo.py               # Inferencia en tiempo real con YOLO11s y umbrales adaptativos
  comunas.py              # Base completa de 16 regiones y comunas de Chile con coordenadas GPS
  datos.py                # Carga de datos, sincronización dinámica y actualización de avistamientos
  autoridades.py          # Generación de tickets y derivación a SAG / CONAF / SERNAPESCA / MMA
  ubicacion.py            # Gestión de zona del usuario con callbacks de coordenadas automáticas
  theme.py                # Paleta de colores naturales y componentes visuales (etiquetas, badges)
  best.pt                 # Pesos entrenados del modelo YOLO11s (19.1 MB)
views/
  alertar.py              # Pestaña 1: Foto → Inferencia IA → Comuna / Coordenadas → Alerta
  cerca.py                # Pestaña 2: Mapa PyDeck de áreas de afección y filtros de avistamientos
  catalogo.py             # Pestaña 3: Fichas informativas con fotos HD y etiquetas sanitarias
  reportes.py             # Pestaña 4: Historial ciudadano de alertas y tickets generados
  acerca.py               # Pestaña 5: Descripción y metodología del proyecto
data/
  especies.csv            # Catálogo con URLs de fotos de referencia y banderas sanitarias
  avistamientos.csv       # Historial de avistamientos georreferenciados por comuna
  reportes.csv            # Reportes registrados por usuarios en la app
  zonas_urbanas.csv       # 30 zonas urbanas analizadas
```

---

## Correr el proyecto localmente

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar la aplicación Streamlit
streamlit run app.py          # Abre automáticamente en http://localhost:8501
```

---

## Estado del Proyecto

- [x] Entrenamiento e integración del modelo **YOLO11s** real (`core/modelo.py` + `best.pt`).
- [x] Selección dinámica de **Comunas de Chile** y coordenadas GPS automáticas (`core/comunas.py`).
- [x] Mapa de áreas de afección transparente con contornos sólidos en **PyDeck** (`views/cerca.py`).
- [x] Catálogo con **fotografías HD** e insignias de **Portador de Enfermedades** (`views/catalogo.py`).
- [x] Sincronización automática de alertas con la base de avistamientos (`core/datos.py`).
- [ ] Publicar en Streamlit Cloud y agregar la URL oficial al README.
