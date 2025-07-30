class Holocron:
    """
    Representa un Holocron Cuántico que almacena y gestiona grupos de Holobits.
    """

    def __init__(self):
        self.holobits = {}  # Almacena los Holobits por identificador
        self.groups = {}   # Almacena grupos de Holobits

    def add_holobit(self, id, holobit):
        """
        Añade un Holobit al Holocron.
        """
        self.holobits[id] = holobit

    def create_group(self, group_id, holobit_ids):
        """
        Crea un grupo de Holobits.
        """
        group = [self.holobits[hid] for hid in holobit_ids if hid in self.holobits]
        if len(group) != len(holobit_ids):
            raise ValueError("Algunos Holobits no existen en el Holocron.")
        self.groups[group_id] = group

    def execute_quantum_operation(self, operation, group_id):
        """
        Ejecuta una operación cuántica en un grupo de Holobits.
        """
        if group_id not in self.groups:
            raise KeyError(f"El grupo '{group_id}' no existe.")
        group = self.groups[group_id]
        return operation.apply(group)
