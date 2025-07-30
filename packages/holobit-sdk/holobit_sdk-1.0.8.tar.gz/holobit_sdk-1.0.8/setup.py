from setuptools import setup, find_packages

setup(
    name="holobit-sdk",
    version="1.0.7",
    author="Adolfo González Hernández",
    author_email="adolfogonzal@gmail.com",
    description="SDK para la transpilación y ejecución de código holográfico cuántico.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Alphonsus411/holobit_SDK",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "setuptools",
        "wheel",
        "twine",
        "numpy",
        "matplotlib",
    ],
    extras_require={
        "qiskit": ["qiskit"],
    },
    entry_points={
        "console_scripts": [
            "holobit-transpiler=holobit_sdk.transpiler.machine_code_transpiler:main",
            "hololang=holobit_sdk.multi_level.high_level.hololang_cli:main",
        ],
    },
)
