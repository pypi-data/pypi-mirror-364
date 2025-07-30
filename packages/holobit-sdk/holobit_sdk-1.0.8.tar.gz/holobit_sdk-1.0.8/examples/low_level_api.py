from holobit_sdk.multi_level.low_level.low_level_api import LowLevelAPI


def main():
    """Ejemplo de interacción con la API de bajo nivel."""
    api = LowLevelAPI()
    print(api.ejecutar_comando("ALLOCATE", "H1", 0.1, 0.2, 0.3))
    print(api.ejecutar_comando("GET_POSITION", "H1"))
    print(api.ejecutar_comando("DEALLOCATE", "H1"))


if __name__ == "__main__":
    main()
