from textual.widgets import DataTable
from controllers import LibroController

class TablaLibros(DataTable):
    def on_mount(self):
        self.controller = LibroController()
        self.add_columns("ID", "Título", "Autor", "Precio", "Stock")
        self.cargar()

    def cargar(self):
        for libro in self.controller.obtener_todos():
            self.add_row(
                str(libro["libro_id"]),
                libro["titulo"],
                libro["autores"],
                f"{libro['precio']:.2f}",
                str(libro["stock"])
            )
