import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
class HologramSimulator:
    """
    Simulador para visualizar operaciones cuánticas y holográficas en el Holocron.
    Incluye herramientas para mover y rotar Holobits paso a paso.
    """

    def simulate(self, holobits, operation):
        """
        Genera una simulación holográfica para una operación cuántica.
        """
        print(f"Simulando operación '{operation.name}' en {len(holobits)} Holobits...")
        result = operation.apply(holobits)
        print(f"Resultado: {result}")
        return result

    def simulate_steps(self, holobit, steps):
        """
        Aplica una serie de traslaciones y rotaciones a un Holobit.

        Args:
            holobit: Objeto ``Holobit`` a manipular.
            steps: Lista de diccionarios con las claves ``traslacion`` y
                ``rotacion``. ``traslacion`` debe ser una tupla ``(dx, dy, dz)`` y
                ``rotacion`` una tupla ``(eje, angulo)``.

        Returns:
            Lista con las posiciones de los quarks y antiquarks después de cada
            paso.
        """
        snapshots = []
        for step in steps:
            if "traslacion" in step:
                dx, dy, dz = step["traslacion"]
                delta = np.array([dx, dy, dz])
                for q in holobit.quarks + holobit.antiquarks:
                    q.posicion += delta
            if "rotacion" in step:
                eje, angulo = step["rotacion"]
                holobit.rotar(eje, angulo)
            snapshots.append([q.posicion.copy() for q in holobit.quarks + holobit.antiquarks])
        return snapshots

    def animate(self, holobit, steps, interval=500, output_path=None):
        """
        Visualiza en 3D la trayectoria y rotaciones de un Holobit.

        Args:
            holobit: Objeto ``Holobit`` a animar.
            steps: Pasos de movimiento utilizados por :meth:`simulate_steps`.
            interval: Tiempo entre fotogramas en milisegundos.
            output_path: Ruta opcional para guardar la animación en un archivo.
        """
        snapshots = self.simulate_steps(holobit, steps)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        quark_scatter = ax.scatter([], [], [], color='blue', label='Quark')
        antiquark_scatter = ax.scatter([], [], [], color='red', label='Antiquark')

        positions = np.array(snapshots).reshape(-1, 3)
        limit = float(np.abs(positions).max() or 1)
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)

        def update(frame):
            pos = snapshots[frame]
            q_pos = pos[:len(holobit.quarks)]
            a_pos = pos[len(holobit.quarks):]
            quark_scatter._offsets3d = ([p[0] for p in q_pos],
                                        [p[1] for p in q_pos],
                                        [p[2] for p in q_pos])
            antiquark_scatter._offsets3d = ([p[0] for p in a_pos],
                                            [p[1] for p in a_pos],
                                            [p[2] for p in a_pos])
            ax.set_title(f"Paso {frame + 1}/{len(snapshots)}")
            return quark_scatter, antiquark_scatter

        ani = animation.FuncAnimation(
            fig,
            update,
            frames=len(snapshots),
            interval=interval,
            blit=False
        )
        plt.legend()
        if output_path:
            ani.save(output_path)
        plt.show()
        return ani
