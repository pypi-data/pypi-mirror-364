from holobit_sdk.asiic_holographic.instructions import ASIICInstructions
from holobit_sdk.asiic_holographic.translator import ASIICTranslator
from holobit_sdk.asiic_holographic.interpreter import ASIICInterpreter


def main():
    """Demostración de uso del conjunto ASIIC."""
    asiic = ASIICInstructions()

    def rotar_holobit(holobit, eje, angulo):
        return f"Rotando Holobit en el eje {eje} con ángulo {angulo} grados"

    asiic.agregar_instruccion("ROTAR", rotar_holobit)
    print(asiic.ejecutar_instruccion("ROTAR", "H1", "z", 90))

    traductor = ASIICTranslator()
    print(traductor.traducir("ROTAR H1 z 90"))
    print(traductor.traducir("ENTRELAZAR H1 H2"))

    interprete = ASIICInterpreter()
    print(interprete.interpretar("ROTAR H1 z 90"))
    print(interprete.interpretar("ENTRELAZAR H1 H2"))


if __name__ == "__main__":
    main()
