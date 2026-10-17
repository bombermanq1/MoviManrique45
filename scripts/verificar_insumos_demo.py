"""Verifica, sin escribir, los insumos no versionados del MVP local."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
RUTA_MANIFIESTO = RAIZ / "data" / "manifest_demo_v1.json"


def sha256(ruta: Path) -> str:
    """Calcula el hash por bloques para no cargar archivos completos en memoria."""
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def verificar() -> list[str]:
    """Devuelve errores de presencia, tamaño o hash sin alterar ningún insumo."""
    if not RUTA_MANIFIESTO.exists():
        return [f"No existe el manifiesto requerido: {RUTA_MANIFIESTO.relative_to(RAIZ)}"]

    manifiesto = json.loads(RUTA_MANIFIESTO.read_text(encoding="utf-8"))
    errores: list[str] = []
    for item in manifiesto["archivos"]:
        ruta = RAIZ / item["ruta"]
        if not ruta.is_file():
            errores.append(f"Falta: {item['ruta']}")
            continue
        if ruta.stat().st_size != item["bytes"]:
            errores.append(f"Tamaño distinto: {item['ruta']}")
            continue
        if sha256(ruta) != item["sha256"]:
            errores.append(f"Hash SHA-256 distinto: {item['ruta']}")
    return errores


def main() -> int:
    errores = verificar()
    if errores:
        print("Insumos no verificados:")
        for error in errores:
            print(f"- {error}")
        return 1
    print("Insumos del cierre v1 verificados correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
