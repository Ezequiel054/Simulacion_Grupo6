"""Simulación del proyecto logístico del TP3.

La simulación es reproducible y no conserva una tabla de observaciones.
"""

from dataclasses import dataclass, field
from argparse import ArgumentParser
from math import log
from typing import Callable


@dataclass
class GeneradorCongruencialMixto:
    semilla: int
    multiplicador: int
    aditivo: int
    modulo: int
    anterior: int = field(init=False)

    def __post_init__(self) -> None:
        if self.modulo <= 0:
            raise ValueError("El modulo debe ser positivo.")
        if not 0 <= self.semilla < self.modulo:
            raise ValueError("La semilla debe estar entre 0 y modulo - 1.")
        self.anterior = self.semilla

    def siguiente(self) -> float:
        self.anterior = (
            self.multiplicador * self.anterior + self.aditivo
        ) % self.modulo
        return self.anterior / self.modulo


@dataclass(frozen=True)
class Parametros:
    semilla: int = 3922
    multiplicador: int = 1221
    aditivo: int = 1714
    legajo: int = 10007
    cantidad: int = 1000
    media_e: float = 5.0
    d_min: float = 5.0
    d_max: float = 25.0
    semillas: dict[str, int] | None = None

    def semillas_individuales(self) -> dict[str, int]:
        if self.semillas is not None:
            return self.semillas
        return {
            codigo: (self.semilla + desplazamiento) % self.legajo
            for codigo, desplazamiento in {
                "A": 1,
                "B": 2,
                "C": 3,
                "D": 4,
                "E": 5,
                "F": 6,
            }.items()
        }


@dataclass
class ResultadoIteracion:
    tiempos: dict[str, float]
    inicio: dict[str, float]
    fin: dict[str, float]
    total: float


class PercentilOnline:
    """Calcula un percentil usando frecuencias de intervalos pequenos."""

    def __init__(self, percentil: float, ancho: float = 0.01) -> None:
        self.percentil = percentil
        self.ancho = ancho
        self.frecuencias: dict[int, int] = {}
        self.cantidad = 0

    def actualizar(self, valor: float) -> None:
        indice = int(valor / self.ancho)
        self.frecuencias[indice] = self.frecuencias.get(indice, 0) + 1
        self.cantidad += 1

    def resultado(self) -> float:
        if self.cantidad == 0:
            raise ValueError("Se necesita al menos una observacion.")
        objetivo = max(1, int(self.percentil * self.cantidad + 0.999999))
        acumulada = 0
        for indice in sorted(self.frecuencias):
            acumulada += self.frecuencias[indice]
            if acumulada >= objetivo:
                return (indice + 0.5) * self.ancho
        return max(self.frecuencias) * self.ancho


def crear_generadores(parametros: Parametros) -> dict[str, GeneradorCongruencialMixto]:
    semillas = parametros.semillas_individuales()
    return {
        codigo: GeneradorCongruencialMixto(
            semillas[codigo],
            parametros.multiplicador,
            parametros.aditivo,
            parametros.legajo,
        )
        for codigo in "ABCDEF"
    }


def discreta(aleatorio: float, valores: tuple[float, ...], probabilidades: tuple[float, ...]) -> float:
    acumulada = 0.0
    for valor, probabilidad in zip(valores, probabilidades):
        acumulada += probabilidad
        if aleatorio < acumulada:
            return valor
    return valores[-1]


def simular_iteracion(
    generadores: dict[str, GeneradorCongruencialMixto],
    parametros: Parametros,
) -> ResultadoIteracion:
    duraciones = {
        "A": 15.0,
        "B": discreta(generadores["B"].siguiente(), (20.0, 30.0, 40.0), (0.25, 0.40, 0.35)),
        "C": 5.0,
        "D": parametros.d_min + (parametros.d_max - parametros.d_min) * generadores["D"].siguiente(),
        "E": -parametros.media_e * log(1.0 - generadores["E"].siguiente()),
        "F": discreta(generadores["F"].siguiente(), (15.0, 25.0), (0.50, 0.50)),
    }
    fin_a = duraciones["A"]
    fin_b = fin_a + duraciones["B"]
    fin_c = duraciones["C"]
    fin_d = fin_c + duraciones["D"]
    fin_e = fin_d + duraciones["E"]
    inicio_f = max(fin_b, fin_e)
    fin_f = inicio_f + duraciones["F"]
    return ResultadoIteracion(
        duraciones,
        {"A": 0.0, "B": fin_a, "C": 0.0, "D": fin_c, "E": fin_d, "F": inicio_f},
        {"A": fin_a, "B": fin_b, "C": fin_c, "D": fin_d, "E": fin_e, "F": fin_f},
        fin_f,
    )


def recorrer(parametros: Parametros, accion: Callable[[int, ResultadoIteracion], None]) -> None:
    generadores = crear_generadores(parametros)
    for iteracion in range(1, parametros.cantidad + 1):
        accion(iteracion, simular_iteracion(generadores, parametros))


def estadisticas(parametros: Parametros) -> dict[str, object]:
    suma = 0.0
    minimo = float("inf")
    maximo = float("-inf")
    menores_60 = 0
    mayores_90 = 0
    criticas = {codigo: 0 for codigo in "ABCDEF"}
    duraciones = {codigo: 0.0 for codigo in "ABCDEF"}
    percentil = PercentilOnline(0.95)

    def acumular(_: int, resultado: ResultadoIteracion) -> None:
        nonlocal suma, minimo, maximo, menores_60, mayores_90
        suma += resultado.total
        percentil.actualizar(resultado.total)
        minimo = min(minimo, resultado.total)
        maximo = max(maximo, resultado.total)
        menores_60 += resultado.total <= 60.0
        mayores_90 += resultado.total >= 90.0
        for codigo, tiempo in resultado.tiempos.items():
            duraciones[codigo] += tiempo
        producto = resultado.fin["B"] >= resultado.fin["E"]
        criticas["F"] += 1
        for codigo in ("A", "B") if producto else ("C", "D", "E"):
            criticas[codigo] += 1

    recorrer(parametros, acumular)
    return {
        "promedio": suma / parametros.cantidad,
        "minimo": minimo,
        "maximo": maximo,
        "duraciones_promedio": {codigo: tiempo / parametros.cantidad for codigo, tiempo in duraciones.items()},
        "proporcion_critica": {codigo: cantidad / parametros.cantidad for codigo, cantidad in criticas.items()},
        "p_t_menor_igual_60": menores_60 / parametros.cantidad,
        "p_t_mayor_igual_90": mayores_90 / parametros.cantidad,
        "percentil_95": percentil.resultado(),
    }


def percentil_95(parametros: Parametros) -> float:
    return float(estadisticas(parametros)["percentil_95"])


def frecuencias(parametros: Parametros, minimo: float) -> list[int]:
    """Usa 9 intervalos de 10 minutos y un ultimo intervalo abierto."""
    intervalos = [0] * 10

    def contar(_: int, resultado: ResultadoIteracion) -> None:
        indice = int((resultado.total - minimo) // 10.0)
        intervalos[min(indice, 9)] += 1

    recorrer(parametros, contar)
    return intervalos


def imprimir_informe(parametros: Parametros) -> None:
    resultados = estadisticas(parametros)
    print(f"Simulaciones: {parametros.cantidad}")
    print(f"Tiempo minimo: {resultados['minimo']:.4f} min")
    print(f"Tiempo promedio: {resultados['promedio']:.4f} min")
    print(f"Tiempo maximo observado: {resultados['maximo']:.4f} min")
    print(f"Percentil 95: {resultados['percentil_95']:.4f} min")
    print(f"P(T <= 60): {resultados['p_t_menor_igual_60']:.4%}")
    print(f"P(T >= 90): {resultados['p_t_mayor_igual_90']:.4%}")
    print("Duracion promedio por actividad:")
    for codigo, tiempo in resultados["duraciones_promedio"].items():
        print(f"  {codigo}: {tiempo:.4f} min")
    print("Proporcion critica / cuello de botella:")
    for codigo, proporcion in resultados["proporcion_critica"].items():
        print(f"  {codigo}: {proporcion:.4%}")
    print("Frecuencias (primeros 9 intervalos de 10 min; ultimo abierto):")
    for indice, cantidad in enumerate(frecuencias(parametros, float(resultados["minimo"])), 1):
        print(f"  Intervalo {indice}: {cantidad}")


def leer_parametros() -> Parametros:
    parser = ArgumentParser(description="Simulacion del TP3 de proyecto logistico")
    parser.add_argument("--legajo", type=int, default=10007)
    parser.add_argument("--cantidad", type=int, default=1000)
    parser.add_argument("--semilla", type=int, default=3922)
    parser.add_argument("--multiplicador", type=int, default=1221)
    parser.add_argument("--aditivo", type=int, default=1714)
    parser.add_argument("--media-e", type=float, default=5.0)
    parser.add_argument("--d-min", type=float, default=5.0)
    parser.add_argument("--d-max", type=float, default=25.0)
    argumentos = parser.parse_args()
    return Parametros(
        semilla=argumentos.semilla,
        multiplicador=argumentos.multiplicador,
        aditivo=argumentos.aditivo,
        legajo=argumentos.legajo,
        cantidad=argumentos.cantidad,
        media_e=argumentos.media_e,
        d_min=argumentos.d_min,
        d_max=argumentos.d_max,
    )


if __name__ == "__main__":
    imprimir_informe(leer_parametros())