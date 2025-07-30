import numpy as np


class Holobit:
    def __init__(self, quarks, antiquarks):
        """
        Clase para representar un Holobit compuesto por quarks y antiquarks.

        Args:
            quarks: Lista de 6 objetos Quark.
            antiquarks: Lista de 6 objetos Quark (representan antiquarks).
        """
        if len(quarks) != 6 or len(antiquarks) != 6:
            raise ValueError("Un Holobit debe tener exactamente 6 quarks y 6 antiquarks.")
        self.quarks = quarks
        self.antiquarks = antiquarks

    def rotar(self, eje, angulo):
        """
        Rota el Holobit en el eje especificado por un ángulo dado.

        Args:
            eje: Eje de rotación ('x', 'y', 'z').
            angulo: Ángulo de rotación en grados.
        """
        radianes = np.deg2rad(angulo)
        matriz_rotacion = self._crear_matriz_rotacion(eje, radianes)
        for quark in self.quarks + self.antiquarks:
            quark.posicion = np.dot(matriz_rotacion, quark.posicion)

    def _crear_matriz_rotacion(self, eje, radianes):
        """
        Genera una matriz de rotación en 3D.

        Args:
            eje: Eje de rotación ('x', 'y', 'z').
            radianes: Ángulo de rotación en radianes.
        """
        if eje == 'x':
            return np.array([[1, 0, 0],
                             [0, np.cos(radianes), -np.sin(radianes)],
                             [0, np.sin(radianes), np.cos(radianes)]])
        elif eje == 'y':
            return np.array([[np.cos(radianes), 0, np.sin(radianes)],
                             [0, 1, 0],
                             [-np.sin(radianes), 0, np.cos(radianes)]])
        elif eje == 'z':
            return np.array([[np.cos(radianes), -np.sin(radianes), 0],
                             [np.sin(radianes), np.cos(radianes), 0],
                             [0, 0, 1]])
        else:
            raise ValueError("El eje debe ser 'x', 'y' o 'z'.")

    def __repr__(self):
        """Representación legible del Holobit."""
        return f"Holobit(quarks={self.quarks}, antiquarks={self.antiquarks})"
