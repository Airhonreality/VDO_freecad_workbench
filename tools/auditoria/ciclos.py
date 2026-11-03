"""tools/auditoria/ciclos.py — grafo de imports del paquete: ciclos y aristas entre capas.

Uso:
    python3 -I tools/auditoria/ciclos.py

Lee todos los .py de freecad/vdo/ con ast (no grep). Cuenta imports de nivel superior y
dentro de funciones. Imprime:
  - componentes fuertemente conexos de más de un módulo (ciclos reales, Tarjan);
  - aristas de core hacia cad (violación de MN-03, plan §2).

Sale con código 1 si hay algún ciclo. Las aristas core->cad se imprimen pero no
hacen fallar el script: esa violación la mide tests/test_arquitectura.py.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PAQUETE = ROOT / "freecad" / "vdo"
PREFIJO = "freecad.vdo"


def _nombre_modulo(ruta: Path) -> str:
    relativa = ruta.relative_to(ROOT)
    return ".".join(relativa.with_suffix("").parts)


def _grafo() -> dict[str, set[str]]:
    modulos = {_nombre_modulo(f): f for f in PAQUETE.rglob("*.py")}
    grafo: dict[str, set[str]] = {m: set() for m in modulos}
    for modulo, ruta in modulos.items():
        arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=str(ruta))
        for nodo in ast.walk(arbol):
            objetivos: list[str] = []
            if isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.module.startswith(PREFIJO):
                objetivos.append(nodo.module)
                objetivos += [f"{nodo.module}.{a.name}" for a in nodo.names]
            elif isinstance(nodo, ast.Import):
                objetivos += [a.name for a in nodo.names if a.name.startswith(PREFIJO)]
            for destino in objetivos:
                if destino in modulos and destino != modulo:
                    grafo[modulo].add(destino)
    return grafo


def _componentes_con_ciclo(grafo: dict[str, set[str]]) -> list[list[str]]:
    """Componentes fuertemente conexos de tamaño > 1 (algoritmo de Tarjan, iterativo)."""
    indice: dict[str, int] = {}
    bajo: dict[str, int] = {}
    en_pila: set[str] = set()
    pila: list[str] = []
    resultado: list[list[str]] = []
    contador = 0
    for raiz in grafo:
        if raiz in indice:
            continue
        trabajo = [(raiz, iter(sorted(grafo[raiz])))]
        indice[raiz] = bajo[raiz] = contador
        contador += 1
        pila.append(raiz)
        en_pila.add(raiz)
        while trabajo:
            nodo, vecinos = trabajo[-1]
            siguiente = next(vecinos, None)
            if siguiente is not None:
                if siguiente not in indice:
                    indice[siguiente] = bajo[siguiente] = contador
                    contador += 1
                    pila.append(siguiente)
                    en_pila.add(siguiente)
                    trabajo.append((siguiente, iter(sorted(grafo[siguiente]))))
                elif siguiente in en_pila:
                    bajo[nodo] = min(bajo[nodo], indice[siguiente])
                continue
            trabajo.pop()
            if trabajo:
                padre = trabajo[-1][0]
                bajo[padre] = min(bajo[padre], bajo[nodo])
            if bajo[nodo] == indice[nodo]:
                componente = []
                while True:
                    w = pila.pop()
                    en_pila.discard(w)
                    componente.append(w)
                    if w == nodo:
                        break
                if len(componente) > 1:
                    resultado.append(sorted(componente))
    return resultado


def main() -> int:
    grafo = _grafo()
    ciclos = _componentes_con_ciclo(grafo)
    print(f"CICLOS: {len(ciclos)} componentes")
    for componente in ciclos:
        print("  - " + ", ".join(m.replace(PREFIJO + ".", "") for m in componente))

    core_cad = sorted(
        (origen, destino)
        for origen, destinos in grafo.items()
        if origen.startswith(PREFIJO + ".core.")
        for destino in destinos
        if destino.startswith(PREFIJO + ".cad.")
    )
    print(f"ARISTAS core->cad: {len(core_cad)}")
    for origen, destino in core_cad:
        print(f"  {origen.replace(PREFIJO + '.', '')} -> {destino.replace(PREFIJO + '.', '')}")
    return 1 if ciclos else 0


if __name__ == "__main__":
    sys.exit(main())
