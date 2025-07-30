from holobit_sdk.core.quark import Quark
from holobit_sdk.core.holobit import Holobit
from holobit_sdk.visualization.projector import proyectar_holograma


def main():
    """Ejemplo básico de creación y visualización de un Holobit.

    Los objetos ``Quark`` y ``Holobit`` cuentan con un método ``__repr__`` que
    permite mostrar sus atributos de forma clara al imprimirlos.
    """
    print("Bienvenido al SDK Holobit")
    print("Creando quarks...")

    q1 = Quark(0.1, 0.2, 0.3)
    q2 = Quark(0.4, 0.5, 0.6)
    q3 = Quark(0.7, 0.8, 0.9)
    q4 = Quark(-0.1, -0.2, -0.3)
    q5 = Quark(-0.4, -0.5, -0.6)
    q6 = Quark(-0.7, -0.8, -0.9)

    print("Quarks creados:")
    for i, q in enumerate([q1, q2, q3, q4, q5, q6], start=1):
        print(f"  Q{i}: {q}")

    print("\nCreando un Holobit con los quarks...")
    holobit = Holobit([q1, q2, q3, q4, q5, q6], [q4, q5, q6, q1, q2, q3])

    print("Holobit creado:")
    print(f"  {holobit}")

    print("\nProyectando holograma del Holobit...")
    proyectar_holograma(holobit)
    print("Holograma proyectado con éxito.")


if __name__ == "__main__":
    main()
