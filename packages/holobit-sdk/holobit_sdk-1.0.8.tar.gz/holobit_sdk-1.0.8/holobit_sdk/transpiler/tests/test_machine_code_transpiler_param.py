import pytest
from holobit_sdk.transpiler.machine_code_transpiler import MachineCodeTranspiler

@pytest.mark.parametrize(
    "architecture,instruction,expected",
    [
        ("x86", "ALLOCATE H1 0.1 0.2 0.3", "MOV H1 0.1 0.2 0.3"),
        ("ARM", "ALLOCATE H1 0.1 0.2 0.3", "LDR H1 0.1 0.2 0.3"),
        ("RISC-V", "ALLOCATE H1 0.1 0.2 0.3", "LW H1 0.1 0.2 0.3"),
    ],
)
def test_transpile_allocate(architecture, instruction, expected):
    transpiler = MachineCodeTranspiler(architecture)
    assert transpiler.transpile(instruction) == expected


@pytest.mark.parametrize(
    "architecture,expected",
    [
        ("x86", "JMP LABEL1"),
        ("ARM", "B LABEL1"),
        ("RISC-V", "JAL LABEL1"),
    ],
)
def test_transpile_jump(architecture, expected):
    transpiler = MachineCodeTranspiler(architecture)
    assert transpiler.transpile("JUMP LABEL1") == expected


@pytest.mark.parametrize("architecture", ["x86", "ARM", "RISC-V"])
def test_transpile_unknown_instruction(architecture):
    transpiler = MachineCodeTranspiler(architecture)
    result = transpiler.transpile("UNKNOWN_CMD H1")
    assert result == f"Instrucción holográfica desconocida para {architecture}: UNKNOWN_CMD"


def test_compare_redundant():
    transpiler = MachineCodeTranspiler("x86")
    assert transpiler.transpile("COMPARE H1 H1") == "NOP"


def test_push_pop_multi():
    transpiler = MachineCodeTranspiler("x86")
    assert transpiler.transpile("PUSH H1 H2 H3") == "PUSH_MULTI H1 H2 H3"
    assert transpiler.transpile("POP H1 H2 H3") == "POP_MULTI H1 H2 H3"


def test_register_reuse():
    transpiler = MachineCodeTranspiler("x86")
    first = transpiler.transpile("ADD H1 H2")
    second = transpiler.transpile("ADD H1 H3")
    assert "; Registro registrado" in first
    assert "; Registro reutilizado" in second


def test_eliminate_mov_redundant():
    transpiler = MachineCodeTranspiler("x86")
    assert transpiler.transpile("ALLOCATE H1 H1") == "NOP"
