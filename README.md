# Proyecto Innovacien

Plataforma para detectar **especies invasoras** a partir de una foto, avisar a
la autoridad competente y mostrar las especies invasoras registradas cerca de
cada zona.

Estado: **base en construcción**. La interfaz completa ya funciona, pero el
modelo y el envío de avisos están simulados a propósito, con los puntos de
conexión marcados.

## Correr la app

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre <http://localhost:8501>.

## Estructura

```
app.py                    # entrada: tema, barra lateral y pestañas
core/
  theme.py                # paleta de colores naturales y componentes visuales
  datos.py                # carga de CSV, búsqueda por radio, guardado de reportes
  modelo.py               # clasificador (SIMULADO — aquí se conecta Hugging Face)
  autoridades.py          # envío de alertas (SIMULADO — aquí va el canal real)
  ubicacion.py            # zona del usuario, compartida por las pestañas
views/
  alertar.py              # pestaña principal: foto → especie → aviso
  cerca.py                # especies invasoras en tu área (mapa + fichas)
  catalogo.py             # catálogo de especies reconocibles
  reportes.py             # historial de reportes enviados
  acerca.py               # qué es el proyecto y qué falta
data/
  especies.csv            # catálogo (datos de ejemplo, editable a mano)
  avistamientos.csv       # avistamientos (datos de ejemplo)
  imagenes/               # fotos para entrenar, una carpeta por especie
  subidas/                # fotos que suben los usuarios (no se versiona)
```

## Pestañas

| Pestaña | Archivo | Qué hace hoy |
|---|---|---|
| 🚨 Alertar animal | [views/alertar.py](views/alertar.py) | Sube o toma foto, identifica la especie, muestra riesgo y arma el aviso |
| 📍 Especies invasoras en tu área | [views/cerca.py](views/cerca.py) | Mapa y fichas por radio de distancia, con filtros |
| 📖 Catálogo de especies | [views/catalogo.py](views/catalogo.py) | Fichas buscables de las 15 especies cargadas |
| 🗂️ Mis reportes | [views/reportes.py](views/reportes.py) | Historial de avisos + descarga en CSV |
| ℹ️ Acerca del proyecto | [views/acerca.py](views/acerca.py) | Explicación, estado del modelo y lista de pendientes |

## Cómo agregar cosas

- **Nueva pestaña**: crea `views/mi_vista.py` con una función `render()` y agrégala
  a la lista `PESTANAS` en [app.py](app.py).
- **Nueva especie**: agrega una fila a [data/especies.csv](data/especies.csv).
- **Cambiar colores**: [core/theme.py](core/theme.py) y
  [.streamlit/config.toml](.streamlit/config.toml).

## Conectar el modelo de Hugging Face

1. Definir el modelo en `MODELO_HF` de [core/modelo.py](core/modelo.py).
2. Descomentar las dependencias opcionales de [requirements.txt](requirements.txt).
3. Completar `MAPA_ETIQUETAS` (etiqueta del modelo → `nombre_comun` del catálogo).
4. Correr con el modelo real:

```bash
INNOVACIEN_MODELO=hf streamlit run app.py
```

## Pendientes

- [ ] Cargar nuestras fotos y entrenar/afinar el modelo.
- [ ] Reemplazar los CSV de ejemplo por la base de datos real.
- [ ] Confirmar los canales oficiales de aviso (SAG, CONAF, SERNAPESCA, MMA).
- [ ] Geolocalización automática desde el navegador.
- [ ] Cuentas de usuario.
- [ ] Identidad visual final.
