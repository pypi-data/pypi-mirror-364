from holobit_sdk.assembler.parser import AssemblerParser
from holobit_sdk.assembler.executor import AssemblerExecutor


class HolocronInstruction:
    """Representa una instrucción básica del ensamblador holográfico."""

    def __init__(self, name, func):
        self.name = name
        self.func = func

    def execute(self, parser, *args):
        return self.func(parser, *args)


def _crear(parser, nombre, *coords):
    line = f"CREAR {nombre} ({', '.join(coords)})"
    parser.parse_line(line)


def _crear_holobit(parser, nombre, refs):
    line = f"CREAR {nombre} {{{refs}}}"
    parser.parse_line(line)


def _rotar(parser, nombre, eje, angulo):
    line = f"ROT {nombre} {eje} {angulo}"
    parser.parse_line(line)


def _entrelazar(parser, h1, h2):
    """Registra el entrelazamiento entre dos Holobits."""
    line = f"ENTR {h1} {h2}"
    parser.parse_line(line)


DEFAULT_INSTRUCTIONS = {
    "CREAR": HolocronInstruction("CREAR", _crear),
    "CREAR_HOLOBIT": HolocronInstruction("CREAR_HOLOBIT", _crear_holobit),
    "ROT": HolocronInstruction("ROT", _rotar),
    "ENTR": HolocronInstruction("ENTR", _entrelazar),
}


class AssemblerVM:
    """Pequeña máquina virtual para ejecutar instrucciones holográficas."""

    def __init__(self):
        self.parser = AssemblerParser()
        self.executor = AssemblerExecutor(self.parser)
        self.instructions = DEFAULT_INSTRUCTIONS

    def execute_instruction(self, name, *args):
        if name not in self.instructions:
            raise ValueError(f"Instrucción desconocida: {name}")
        instr = self.instructions[name]
        instr.execute(self.parser, *args)

    def run_program(self, lines):
        for line in lines:
            clean = line.strip()
            if clean:
                self.executor.execute(clean)

    def run_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            self.run_program(f.readlines())
