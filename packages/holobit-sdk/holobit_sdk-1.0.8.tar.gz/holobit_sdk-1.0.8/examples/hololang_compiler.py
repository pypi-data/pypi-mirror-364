from holobit_sdk.multi_level.high_level.compiler import HoloLangCompiler


def main():
    """Ejemplo de compilación y ejecución de instrucciones HoloLang."""
    compiler = HoloLangCompiler("x86")
    codigo_hololang = [
        "CREAR H1 (0.1, 0.2, 0.3)",
        "IMPRIMIR H1",
        "EJECUTAR MULT H1 H2",
    ]

    for linea in codigo_hololang:
        resultado = compiler.compilar_y_ejecutar(linea)
        print(resultado)


if __name__ == "__main__":
    main()
