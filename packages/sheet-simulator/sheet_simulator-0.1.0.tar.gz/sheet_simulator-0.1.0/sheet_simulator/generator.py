


import numpy as np
from typing import Dict, Any, Callable, List


class InputGenerator:
    """
    Clase utilitaria para generar variaciones de inputs:
    - Permite transformaciones deterministas o aleatorias sobre scalars o vectores.
    - Genera múltiples escenarios que pueden luego pasarse al simulador.

    Cada función de perturbación recibe un input base (escalar o array) 
    y devuelve una versión transformada.
    """

    @staticmethod
    def scale_geometrically(vector: np.ndarray, start_idx: int, rate: float) -> np.ndarray:
        """
        Escala geométricamente los valores del vector a partir del índice start_idx
        usando la fórmula: v_t = v_T * exp(r * (t - T))
        """
        result = vector.copy()
        base_value = result[start_idx]
        for t in range(start_idx + 1, len(result)):
            result[t] = base_value * np.exp(rate * (t - start_idx))
        return result

    @staticmethod
    def perturb_scalar(value: float, dist: str = "normal", scale: float = 1.0) -> float:
        """
        Perturba un escalar usando una distribución de probabilidad centrada en el valor.
        Actualmente soporta: 'normal', 'uniform'
        """
        if dist == "normal":
            return np.random.normal(loc=value, scale=scale)
        elif dist == "uniform":
            return np.random.uniform(low=value - scale, high=value + scale)
        else:
            raise ValueError(f"Distribución '{dist}' no soportada")

    @staticmethod
    def generate_scenarios(
        base_inputs: Dict[str, Any],
        perturbations: Dict[str, Callable[[Any], Any]],
        n: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Genera n escenarios a partir de los inputs base y una definición de perturbación por input.
        Cada perturbation debe ser una función que recibe un valor y devuelve una versión modificada.
        
        Args:
            base_inputs: dict con los inputs de referencia
            perturbations: dict con funciones por input a aplicar (puede ser parcial)
            n: número de escenarios a generar

        Returns:
            Lista de dicts con inputs perturbados
        """
        scenarios = []
        for _ in range(n):
            scenario = {}
            for name, value in base_inputs.items():
                if name in perturbations:
                    scenario[name] = perturbations[name](value)
                else:
                    scenario[name] = value
            scenarios.append(scenario)
        return scenarios



