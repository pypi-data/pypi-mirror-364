from holobit_sdk.core.holobit import Holobit
from holobit_sdk.core.quark import Quark


class AssemblerParser:
    def __init__(self):
        """
        Inicializa el parser del ensamblador.
        """
        self.holobits = {}  # Tabla de símbolos para almacenar quarks y holobits
        self.entanglements = {}  # Registro de entrelazamientos entre Holobits

    def parse_line(self, line):
        """
        Interpreta una línea de código ensamblador.

        Args:
            line: Línea en lenguaje ensamblador.
        """
        # Eliminar comentarios y limpiar espacios adicionales
        line = line.split(";")[0].strip()
        if not line:
            return  # Saltar líneas vacías o comentarios

        tokens = line.split()  # Dividir por espacios
        if len(tokens) < 2:
            raise ValueError(f"Línea inválida: '{line}'")

        command = tokens[0]

        if command == "CREAR":
            if len(tokens) < 3:
                raise ValueError(f"Formato inválido para la instrucción CREAR: '{line}'")
            nombre = tokens[1]
            contenido = " ".join(tokens[2:]).strip()

            # Manejar la creación de un Holobit o un Quark
            if contenido.startswith("{") and contenido.endswith("}"):  # Es un Holobit
                referencias = contenido[1:-1].split(",")
                referencias = [ref.strip() for ref in referencias if ref.strip()]
                if len(referencias) != 6:
                    raise ValueError(
                        f"Un Holobit requiere exactamente 6 referencias, pero se encontraron {len(referencias)}: '{contenido}'"
                    )

                quarks = []
                for ref in referencias:
                    if ref in self.holobits:
                        quarks.append(self.holobits[ref])
                    else:
                        raise KeyError(f"El quark '{ref}' no existe en la tabla de símbolos.")

                self.holobits[nombre] = Holobit(quarks, [self._crear_antiquark(q) for q in quarks])
            elif contenido.startswith("(") and contenido.endswith(")"):  # Es un Quark
                coords = self._parse_coordinates(contenido)
                self.holobits[nombre] = Quark(*coords)
            else:
                raise ValueError(f"Formato inválido para CREAR: '{line}'")
        elif command == "ROT":
            if len(tokens) != 4:
                raise ValueError(f"Formato inválido para la instrucción ROT: '{line}'")
            holobit_name, axis, angle = tokens[1], tokens[2].lower(), tokens[3]
            if holobit_name not in self.holobits:
                raise KeyError(f"El Holobit '{holobit_name}' no existe en la tabla de símbolos.")
            if axis not in ["x", "y", "z"]:
                raise ValueError(f"Eje inválido para rotación: '{axis}'. Debe ser 'x', 'y' o 'z'.")
            try:
                angle = float(angle)
            except ValueError:
                raise ValueError(f"Ángulo inválido para rotación: '{angle}'. Debe ser un número válido.")

            holobit = self.holobits[holobit_name]
            holobit.rotar(axis, angle)
        elif command == "ENTR":
            if len(tokens) != 3:
                raise ValueError(f"Formato inválido para la instrucción ENTR: '{line}'")
            h1, h2 = tokens[1], tokens[2]
            if h1 not in self.holobits or h2 not in self.holobits:
                raise KeyError("Uno de los Holobits no existe en la tabla de símbolos.")
            from ..core.operations import entrelazar
            hb1 = self.holobits[h1]
            hb2 = self.holobits[h2]
            estado = entrelazar(hb1.quarks[0], hb2.quarks[0])
            self.entanglements[(h1, h2)] = estado
        else:
            raise ValueError(f"Comando desconocido: '{command}'")

    def _parse_coordinates(self, coords_string):
        coords_string = coords_string.strip()

        # Validar paréntesis inicial y final
        if not (coords_string.startswith("(") and coords_string.endswith(")")):
            raise ValueError(f"Las coordenadas deben estar entre paréntesis: '{coords_string}'")

        # Quitar paréntesis y procesar el contenido interno
        coords_content = coords_string[1:-1].strip()
        if not coords_content:
            raise ValueError(f"Las coordenadas están vacías: '{coords_string}'")

        # Procesar coordenadas y convertir a flotantes
        try:
            coords = [float(coord.strip()) for coord in coords_content.split(",")]
            if len(coords) != 3:
                raise ValueError(
                    f"Se requieren exactamente 3 coordenadas, pero se encontraron {len(coords)}: '{coords_string}'")
        except ValueError as e:
            raise ValueError(f"Error al procesar las coordenadas '{coords_string}': {e}")

        return tuple(coords)

    def _crear_antiquark(self, quark):
        """
        Crea un antiquark con posición opuesta.

        Args:
            quark: Objeto Quark.
        """
        return Quark(-quark.posicion[0], -quark.posicion[1], -quark.posicion[2], quark.estado)
