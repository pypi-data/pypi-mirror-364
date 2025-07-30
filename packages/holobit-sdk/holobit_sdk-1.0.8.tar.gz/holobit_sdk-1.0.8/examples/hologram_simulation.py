from holobit_sdk.core.quark import Quark
from holobit_sdk.core.holobit import Holobit
from holobit_sdk.quantum_holocron.core.hologram_simulator import HologramSimulator


def main():
    """Demostración de animación de un Holobit."""
    quarks = [Quark(0.1 * i, 0.1 * i, 0.1 * i) for i in range(6)]
    antiquarks = [Quark(-q.posicion[0], -q.posicion[1], -q.posicion[2]) for q in quarks]
    holobit = Holobit(quarks, antiquarks)

    simulator = HologramSimulator()

    pasos = [
        {"traslacion": (0.1, 0.0, 0.0), "rotacion": ("z", 15)},
        {"traslacion": (0.0, 0.1, 0.0), "rotacion": ("y", 15)},
        {"traslacion": (0.0, 0.0, 0.1), "rotacion": ("x", 15)},
    ]

    simulator.animate(holobit, pasos, interval=700, output_path="hologram_animation.gif")


if __name__ == "__main__":
    main()
