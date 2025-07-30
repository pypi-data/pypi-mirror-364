"""Herramientas para exportar evaluaciones a sistemas de prueba formal."""

from typing import Dict


def export_to_coq(resultados: Dict[str, float], ruta: str) -> str:
    """Guarda los resultados en un archivo Coq (.v)."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("(* Resultados generados por AGI Core *)\n")
        for nombre, valor in resultados.items():
            f.write(f"Definition {nombre} := {valor}.\n")
    return ruta


def export_to_lean(resultados: Dict[str, float], ruta: str) -> str:
    """Guarda los resultados en un archivo Lean (.lean)."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("-- Resultados generados por AGI Core\n")
        for nombre, valor in resultados.items():
            f.write(f"def {nombre} := {valor}\n")
    return ruta

