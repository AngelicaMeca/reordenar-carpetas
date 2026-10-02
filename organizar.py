"""Ordena los archivos de una carpeta en subcarpetas según su tipo.

Uso:
    python organizar.py                      # ordena Descargas
    python organizar.py "D:\\Mis cosas"      # ordena otra carpeta
    python organizar.py --simular            # muestra qué haría, sin mover nada
    python organizar.py --deshacer           # revierte el último ordenamiento
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
CONFIG_POR_DEFECTO = BASE / "categorias.json"
CARPETA_OTROS = "Otros"
REGISTRO = ".organizador_registro.json"

# Descargas a medio terminar o archivos del sistema: no se tocan.
IGNORAR_EXT = {".crdownload", ".part", ".partial", ".tmp", ".download", ".lnk"}
IGNORAR_NOMBRES = {"desktop.ini", "thumbs.db", ".ds_store", REGISTRO}


def carpeta_descargas() -> Path:
    home = Path.home()
    for nombre in ("Downloads", "Descargas"):
        if (home / nombre).is_dir():
            return home / nombre
    sys.exit("No encontré la carpeta de Descargas. Indicá una carpeta como argumento.")


def cargar_categorias(ruta: Path) -> dict[str, str]:
    """Devuelve un mapa extensión -> nombre de carpeta."""
    with open(ruta, encoding="utf-8") as f:
        categorias = json.load(f)
    return {ext.lower(): carpeta for carpeta, exts in categorias.items() for ext in exts}


def destino_libre(destino: Path) -> Path:
    """Si ya existe un archivo con ese nombre, agrega ' (1)', ' (2)', etc."""
    if not destino.exists():
        return destino
    n = 1
    while True:
        candidato = destino.with_name(f"{destino.stem} ({n}){destino.suffix}")
        if not candidato.exists():
            return candidato
        n += 1


def organizar(carpeta: Path, por_ext: dict[str, str], simular: bool) -> None:
    movimientos = []
    for archivo in sorted(carpeta.iterdir()):
        if not archivo.is_file():
            continue
        if archivo.name.lower() in IGNORAR_NOMBRES or archivo.suffix.lower() in IGNORAR_EXT:
            continue

        nombre_carpeta = por_ext.get(archivo.suffix.lower(), CARPETA_OTROS)
        destino = destino_libre(carpeta / nombre_carpeta / archivo.name)
        print(f"{archivo.name}  ->  {nombre_carpeta}\\{destino.name}")

        if simular:
            continue
        try:
            destino.parent.mkdir(exist_ok=True)
            shutil.move(str(archivo), str(destino))
            movimientos.append({"desde": str(archivo), "hacia": str(destino)})
        except OSError as e:  # archivo abierto en otro programa, sin permisos, etc.
            print(f"   ! No se pudo mover: {e}")

    if simular:
        print("\n(Simulación: no se movió nada.)")
        return
    if movimientos:
        registro = {"fecha": datetime.now().isoformat(timespec="seconds"), "movimientos": movimientos}
        (carpeta / REGISTRO).write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nListo: {len(movimientos)} archivo(s) ordenado(s) en {carpeta}")


def deshacer(carpeta: Path) -> None:
    ruta_registro = carpeta / REGISTRO
    if not ruta_registro.exists():
        sys.exit("No hay ningún ordenamiento para deshacer en esta carpeta.")
    registro = json.loads(ruta_registro.read_text(encoding="utf-8"))

    restaurados = 0
    for m in reversed(registro["movimientos"]):
        hacia, desde = Path(m["hacia"]), Path(m["desde"])
        if not hacia.exists():
            print(f"   ! Ya no existe: {hacia}")
            continue
        destino = destino_libre(desde)
        shutil.move(str(hacia), str(destino))
        restaurados += 1
        # Borra la subcarpeta si quedó vacía.
        try:
            hacia.parent.rmdir()
        except OSError:
            pass

    ruta_registro.unlink()
    print(f"Deshecho: {restaurados} archivo(s) devueltos a {carpeta} (ordenamiento del {registro['fecha']})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ordena archivos en subcarpetas por tipo.")
    parser.add_argument("carpeta", nargs="?", help="Carpeta a ordenar (por defecto: Descargas)")
    parser.add_argument("--simular", action="store_true", help="Muestra qué haría sin mover nada")
    parser.add_argument("--deshacer", action="store_true", help="Revierte el último ordenamiento")
    parser.add_argument("--config", type=Path, default=CONFIG_POR_DEFECTO, help="JSON de categorías")
    args = parser.parse_args()

    carpeta = Path(args.carpeta).expanduser().resolve() if args.carpeta else carpeta_descargas()
    if not carpeta.is_dir():
        sys.exit(f"La carpeta no existe: {carpeta}")

    if args.deshacer:
        deshacer(carpeta)
    else:
        organizar(carpeta, cargar_categorias(args.config), args.simular)


if __name__ == "__main__":
    main()
