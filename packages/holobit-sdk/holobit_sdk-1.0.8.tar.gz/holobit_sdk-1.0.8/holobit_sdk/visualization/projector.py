import matplotlib.pyplot as plt


def proyectar_holograma(holobit):
    """
    Proyecta las posiciones de los quarks y antiquarks en 3D.

    Args:
        holobit: Objeto Holobit.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for quark in holobit.quarks:
        ax.scatter(quark.posicion[0], quark.posicion[1], quark.posicion[2], color='blue', label='Quark')
    for antiquark in holobit.antiquarks:
        ax.scatter(antiquark.posicion[0], antiquark.posicion[1], antiquark.posicion[2], color='red', label='Antiquark')

    ax.set_title("Proyección Holográfica del Holobit")
    plt.show()
