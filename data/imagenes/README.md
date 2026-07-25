# Imágenes de entrenamiento

Una carpeta por especie, con el mismo nombre que aparece en la columna
`nombre_comun` de [especies.csv](../especies.csv) (en minúsculas y con `_` en
lugar de espacios).

```
data/imagenes/
  castor_americano/
    001.jpg
    002.jpg
  vison_americano/
    001.jpg
  avispa_chaqueta_amarilla/
    001.jpg
```

Recomendaciones para las fotos:

- Mínimo 30–50 fotos por especie para un primer entrenamiento decente.
- Variar ángulo, distancia, luz y fondo.
- Formato JPG o PNG, lado mayor de al menos 512 px.
- Sin marcas de agua ni texto encima.
- Anotar la fuente de cada set (para no usar imágenes con licencia restringida).

Cuando el set esté armado, el entrenamiento / fine-tuning se conecta en
[core/modelo.py](../../core/modelo.py).
