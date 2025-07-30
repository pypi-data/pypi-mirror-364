import numpy as np

class Quark:
    def __init__(self, x, y, z, estado=None):
        """
        Clase para representar un quark en un espacio tridimensional.

        Args:
            x, y, z: Coordenadas tridimensionales del quark.
            estado: Estado cuántico del quark como vector (default: |0⟩).
        """
        self.posicion = np.array([x, y, z], dtype=float)
        self.estado = estado if estado is not None else np.array([1, 0])  # Estado inicial |0⟩

    def aplicar_puerta(self, puerta):
        """
        Aplica una puerta cuántica al estado del quark.

        Args:
            puerta: Matriz de la puerta cuántica.
        """
        self.estado = np.dot(puerta, self.estado)

    def __repr__(self):
        """Representación legible del quark."""
        pos = ', '.join(f"{coord}" for coord in self.posicion)
        estado = ', '.join(str(v) for v in self.estado)
        return f"Quark(posicion=[{pos}], estado=[{estado}])"
