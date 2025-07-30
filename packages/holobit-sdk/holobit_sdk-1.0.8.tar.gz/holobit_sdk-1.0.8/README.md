
# Holobit SDK - Documentación Oficial

## 📌 Introducción
El **Holobit SDK** es un kit de desarrollo diseñado para la transpilación y ejecución de código holográfico cuántico. Su arquitectura multinivel permite trabajar con diferentes niveles de abstracción, optimizando el rendimiento en múltiples arquitecturas de hardware.

## 🔹 Características Principales
- **Transpilador Cuántico Holográfico**: Convierte código HoloLang en código máquina optimizado para arquitecturas x86, ARM y RISC-V.
- **Optimización Avanzada**: Reduce instrucciones redundantes y reutiliza registros para maximizar la eficiencia.
- **Ejecución Multinivel**: Soporte para bajo, medio y alto nivel en la programación holográfica.
- **Compatibilidad con Múltiples Arquitecturas**: x86, ARM y RISC-V.

## 📥 Instalación
Para instalar el SDK Holobit, sigue los siguientes pasos:

### 🔹 Requisitos Previos
- **Python >=3.10** (versión mínima recomendada)
- **pip** actualizado
- **Git (opcional, pero recomendado)**

### 🔹 Instalación desde GitHub
```bash
# Clonar el repositorio
git clone https://github.com/usuario/holobit_sdk.git
cd holobit_sdk

# Instalar dependencias
pip install -r requirements_optional.txt
# Para tareas de desarrollo instala también las dependencias de 
# linting y cobertura
pip install -r requirements_dev.txt
```

## 🚀 Uso del SDK
### 🔹 Transpilación de Código HoloLang
Para transpilar un archivo de código holográfico:
```bash
holobit-transpiler --input archivo.holo --arch x86
```
También puedes ejecutarlo con el módulo de Python:
```bash
python -m holobit_sdk.transpiler.machine_code_transpiler --input archivo.holo --arch x86
```
Esto generará un archivo con el código máquina optimizado para la arquitectura especificada.

### 🔹 Ejemplo de Uso en Código
```python
from transpiler.machine_code_transpiler import MachineCodeTranspiler

transpiler = MachineCodeTranspiler("x86")
instruccion = "ADD H1 H2"
codigo_maquina = transpiler.transpile(instruccion)
print(codigo_maquina)  # ADD H1, H2 ; Registro reutilizado
```

Puedes encontrar más demostraciones en el directorio `examples/`.

### 🔹 Ejecución de HoloLang desde la línea de comandos
Puedes ejecutar código HoloLang directamente con el comando `hololang`:
```bash
hololang -c "CREAR H1 (0.1, 0.2, 0.3)" -c "IMPRIMIR H1"
```
O bien pasar un archivo con varias instrucciones:
```bash
hololang --file programa.holo --arch x86
```
Esto mostrará por pantalla el resultado de cada línea procesada.

### 🔹 Máquina Virtual del Ensamblador
El módulo `assembler.virtual_machine` permite ejecutar instrucciones holográficas en un entorno controlado.
```python
from assembler.virtual_machine import AssemblerVM

vm = AssemblerVM()
programa = ["CREAR Q1 (0.1, 0.2, 0.3)", "CREAR Q2 (0.4, 0.5, 0.6)", "CREAR H1 {Q1, Q2}", "ROT H1 z 90"]
vm.run_program(programa)
```
Las instrucciones del ASIIC pueden escribirse con cualquier combinación de mayúsculas y minúsculas. Por ejemplo, `rotar`, `Rotar` y `ROTAR` se interpretan de la misma manera.
### 🔹 Simulación de Holobits
El simulador `HologramSimulator` permite mover y rotar Holobits paso a paso,
y visualizar cada estado en 3D.
```python
from holobit_sdk.quantum_holocron.core.hologram_simulator import HologramSimulator
sim = HologramSimulator()
pasos = [{"traslacion": (0.1, 0, 0), "rotacion": ("z", 15)}]
sim.animate(holobit, pasos)
```
## 🔬 Arquitectura Interna del SDK
El SDK Holobit está estructurado en varios niveles:
1. **Nivel Bajo**: Manejo directo de registros y memoria holográfica.
2. **Nivel Medio**: Procesamiento cuántico holográfico.
3. **Nivel Alto**: Lenguaje de programación HoloLang y compilador asociado.

## 📖 Referencia Técnica
- **Módulo `transpiler`**: Contiene el transpilador de código holográfico a código máquina.
- **Módulo `execution`**: Maneja la ejecución de código transpilado en arquitecturas objetivo.
- **Módulo `debugger`**: Herramientas de depuración y análisis de código transpilado.

## 📄 Ejemplos de Código
Los ejemplos del SDK se encuentran en el directorio `examples/` y pueden
ejecutarse directamente con Python. Por ejemplo:
```bash
python examples/holobit_demo.py
python examples/hololang_compiler.py
python examples/hologram_simulation.py
```
Cada script muestra una funcionalidad concreta del SDK. También puedes
utilizar el transpilador de forma manual:
```bash
holobit-transpiler --input ejemplo.holo --arch x86
```
O bien con el módulo de Python:
```bash
python -m holobit_sdk.transpiler.machine_code_transpiler --input ejemplo.holo --arch x86
```

## 📦 Despliegue y Distribución
El SDK Holobit será empaquetado y distribuido a través de **GitHub Releases** y **PyPI**.

### 🔹 Construcción del Paquete
```bash
python setup.py sdist bdist_wheel
```

### 🔹 Publicación en PyPI
```bash
pip install twine

# Subir el paquete
python -m twine upload dist/*
```

## 🧪 Pruebas
Para ejecutar las pruebas unitarias del proyecto debes instalar las dependencias opcionales.
La suite completa requiere la librería `qiskit`, incluida en este archivo, para ejecutar las pruebas de integración cuántica:
```bash
pip install -r requirements_optional.txt
```
Si además deseas comprobar la cobertura de código instala las dependencias de desarrollo y ejecuta `coverage`:
```bash
pip install -r requirements_dev.txt
```
Luego ejecuta `flake8` para verificar el estilo y `coverage run` junto con `pytest`:
```bash
flake8
coverage run -m pytest
```
Este repositorio cuenta con un flujo de **Integración Continua** en GitHub Actions que instala estas dependencias y ejecuta las pruebas en cada *push* y *pull request*.

## 🛠 Mantenimiento y Contribución
Si deseas contribuir al SDK Holobit, puedes hacer un **fork** del repositorio y enviar un **pull request** con tus mejoras.

## 📧 Contacto y Soporte
Para cualquier consulta, reportes de errores o contribuciones, puedes contactarnos en **adolfogonzal@gmail.com** o a través del repositorio en **GitHub**.

---

📌 **Holobit SDK - Computación Cuántica Holográfica para el Futuro** 🚀


