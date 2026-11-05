# Laboratorio pequeño de PaddleOCR

Este proyecto usa la API local de [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) para observar cómo cambian la detección de líneas, el texto reconocido, la confianza y el tiempo de inferencia cuando cambia la calidad de una imagen. Las tres muestras contienen el mismo texto: una es limpia, otra está inclinada y otra tiene poco contraste.

## Preparación en Windows (CPU)

Usa **Python 3.12 de 64 bits**. La máquina donde se creó este proyecto solo tiene Python 3.14; por eso la inferencia no se pudo ejecutar aquí. Los modelos se descargan en el primer uso y requieren conexión a Internet.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install paddlepaddle==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
.\.venv\Scripts\python -m pip install -r requirements.txt
```

La instalación de PaddlePaddle sigue la [guía oficial para CPU](https://www.paddleocr.ai/main/en/version3.x/paddlepaddle_installation.html); PaddleOCR 3.7.0 se fija en `requirements.txt` para mantener estable este ejemplo. Puedes comprobar ambas bibliotecas así:

```powershell
.\.venv\Scripts\python -c "import paddle, paddleocr; print(paddle.__version__, paddleocr.__version__)"
```

## Ejecutar el experimento

Las imágenes están incluidas. También puedes regenerarlas con `python generar_muestras.py` una vez instaladas las dependencias.

```powershell
.\.venv\Scripts\python demo.py muestras\01_limpia.png muestras\02_inclinada.png muestras\03_bajo_contraste.png
```

`--modelo tiny` (valor inicial) reduce el tiempo y el tamaño de la descarga. Repite con `--modelo medium --salida resultados_medium` para explorar la diferencia entre un modelo pequeño y otro de mayor capacidad. Usa `--min-confianza 0.8` para ver qué líneas desaparecen del resumen cuando se filtran las predicciones débiles. El JSON original siempre conserva todas las predicciones. Puedes indicar tus propias imágenes PNG o JPEG.

## Qué mirar

- `resultados/resumen.json`: tiempo de inferencia, número de líneas y confianza media por imagen. La carga y descarga inicial de modelos se informa aparte en pantalla; el tiempo de cada imagen incluye la llamada a `predict`, no el guardado de archivos.
- `resultados/lineas.csv`: texto, puntuación de reconocimiento y polígono de cada línea.
- Cada subcarpeta contiene `texto.txt`, el JSON original de PaddleOCR y una imagen con los recuadros dibujados.
- `muestras/referencia.txt`: texto previsto para comprobar manualmente errores y omisiones. La confianza es una puntuación del reconocedor, no una medida directa de exactitud frente a esta referencia.

Compara primero la imagen limpia con las variantes. Una línea ausente suele apuntar a un problema de detección; una línea presente con letras equivocadas apunta al reconocimiento. El modelo `medium` puede mejorar algunos casos y tardar más: compruébalo con los resultados de tu equipo, sin asumir que siempre será mejor.

El programa desactiva orientación, corrección de perspectiva y orientación de líneas para centrar el experimento en detección y reconocimiento. La [documentación de la API de PP-OCRv6](https://www.paddleocr.ai/main/en/version3.x/pipeline_usage/OCR.html) describe esas opciones y los campos `rec_texts`, `rec_scores` y `rec_polys`.

