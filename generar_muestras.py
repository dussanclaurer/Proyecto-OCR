"""Crea tres imágenes con el mismo texto para observar cambios en el OCR."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


DESTINO = Path(__file__).resolve().parent / "muestras"
LINEAS = [
    "RECIBO DE PRUEBA",
    "Fecha: 20/10/2026",
    "Cliente: Ana Perez",
    "Total: Bs 125,50",
]


def fuente(tamano: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for nombre in ("DejaVuSans.ttf", "arial.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(nombre, tamano)
        except OSError:
            continue
    return ImageFont.load_default()


def crear_muestras() -> None:
    DESTINO.mkdir(exist_ok=True)
    limpia = Image.new("RGB", (1050, 460), "white")
    dibujar = ImageDraw.Draw(limpia)
    dibujar.rectangle((45, 40, 1005, 420), outline="#394b59", width=3)
    for indice, linea in enumerate(LINEAS):
        dibujar.text(
            (90, 75 + indice * 82),
            linea,
            font=fuente(43 if indice == 0 else 36),
            fill="#182027",
        )
    limpia.save(DESTINO / "01_limpia.png")

    inclinada = limpia.rotate(8, expand=True, fillcolor="white")
    inclinada.save(DESTINO / "02_inclinada.png")

    dificil = ImageEnhance.Contrast(limpia).enhance(0.29)
    dificil = dificil.resize((735, 322), Image.Resampling.BICUBIC)
    dificil = dificil.filter(ImageFilter.GaussianBlur(1.1))
    dificil.save(DESTINO / "03_bajo_contraste.png")

    (DESTINO / "referencia.txt").write_text("\n".join(LINEAS) + "\n", encoding="utf-8")
    print(f"Muestras creadas en {DESTINO}")


if __name__ == "__main__":
    crear_muestras()

