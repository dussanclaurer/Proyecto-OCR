"""Ejecuta PP-OCRv6 y guarda texto, confianza, coordenadas y visualización."""

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path
from time import perf_counter


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Experimenta con PaddleOCR sobre imágenes locales."
    )
    parser.add_argument("imagenes", nargs="+", type=Path, help="Rutas PNG o JPEG")
    parser.add_argument("--salida", type=Path, default=Path("resultados"))
    parser.add_argument("--modelo", choices=("tiny", "small", "medium"), default="tiny")
    parser.add_argument("--idioma", default="es", help="Código de idioma de PaddleOCR (predeterminado: es)")
    parser.add_argument("--min-confianza", type=float, default=0.0,
                        help="Filtra líneas en el resumen; el JSON original conserva todas")
    args = parser.parse_args()
    if not 0 <= args.min_confianza <= 1:
        parser.error("--min-confianza debe estar entre 0 y 1")
    for imagen in args.imagenes:
        if not imagen.is_file():
            parser.error(f"No existe la imagen: {imagen}")
        if imagen.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            parser.error(f"Formato no admitido: {imagen} (usa PNG o JPEG)")
    return args


def leer_lineas(datos: dict, min_confianza: float) -> list[dict]:
    """Las tres listas de PaddleOCR están alineadas por posición."""
    textos = datos.get("rec_texts", [])
    puntajes = datos.get("rec_scores", [])
    poligonos = datos.get("rec_polys", [])
    if not (len(textos) == len(puntajes) == len(poligonos)):
        raise ValueError("PaddleOCR devolvió listas de texto, confianza y polígonos desalineadas")
    return [
        {"texto": texto, "confianza": float(puntaje), "poligono": poligono}
        for texto, puntaje, poligono in zip(textos, puntajes, poligonos)
        if float(puntaje) >= min_confianza
    ]


def main() -> int:
    args = argumentos()
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        print("Falta PaddleOCR. Sigue las instrucciones de instalación en README.md.", file=sys.stderr)
        return 2

    args.salida.mkdir(parents=True, exist_ok=True)
    print(f"Iniciando PP-OCRv6 {args.modelo} en CPU; la primera ejecución descarga los modelos...")
    inicio_modelo = perf_counter()
    ocr = PaddleOCR(
        ocr_version="PP-OCRv6",
        lang=args.idioma,
        text_detection_model_name=f"PP-OCRv6_{args.modelo}_det",
        text_recognition_model_name=f"PP-OCRv6_{args.modelo}_rec",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        device="cpu",
        engine="paddle",
    )
    print(f"Carga de modelos: {perf_counter() - inicio_modelo:.2f} s")

    resumen = []
    filas = []
    for numero, imagen in enumerate(args.imagenes, start=1):
        carpeta = args.salida / f"{numero:02d}_{imagen.stem}"
        carpeta.mkdir(parents=True, exist_ok=True)
        inicio = perf_counter()
        resultados = list(ocr.predict(str(imagen.resolve())))
        duracion = perf_counter() - inicio
        lineas_imagen = []

        for pagina, resultado in enumerate(resultados, start=1):
            json_crudo = carpeta / f"pagina_{pagina:02d}_paddleocr.json"
            resultado.save_to_json(str(json_crudo))
            resultado.save_to_img(str(carpeta))
            contenido = json.loads(json_crudo.read_text(encoding="utf-8"))
            datos = contenido.get("res", contenido)
            lineas = leer_lineas(datos, args.min_confianza)
            for indice, linea in enumerate(lineas, start=1):
                filas.append({
                    "imagen": str(imagen),
                    "pagina": pagina,
                    "linea": indice,
                    "texto": linea["texto"],
                    "confianza": f"{linea['confianza']:.4f}",
                    "poligono": json.dumps(linea["poligono"], ensure_ascii=False),
                })
                lineas_imagen.append(linea)

        (carpeta / "texto.txt").write_text(
            "\n".join(linea["texto"] for linea in lineas_imagen) + "\n", encoding="utf-8"
        )
        confianza_media = (
            statistics.mean(linea["confianza"] for linea in lineas_imagen)
            if lineas_imagen else None
        )
        resumen.append({
            "imagen": str(imagen),
            "modelo": args.modelo,
            "idioma": args.idioma,
            "min_confianza": args.min_confianza,
            "segundos_inferencia": round(duracion, 3),
            "lineas": len(lineas_imagen),
            "confianza_media": round(confianza_media, 4) if confianza_media is not None else None,
        })
        print(f"\n{imagen.name}: {duracion:.2f} s, {len(lineas_imagen)} líneas")
        for linea in lineas_imagen:
            print(f"  {linea['confianza']:.3f}  {linea['texto']}")

    with (args.salida / "lineas.csv").open("w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(
            archivo, fieldnames=("imagen", "pagina", "linea", "texto", "confianza", "poligono")
        )
        escritor.writeheader()
        escritor.writerows(filas)
    (args.salida / "resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nResultados guardados en {args.salida.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

