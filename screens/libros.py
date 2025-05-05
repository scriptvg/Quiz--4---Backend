from textual.screen import Screen
from textual.widgets import Static

class LibrosScreen(Screen):
    def compose(self):
        yield Static("Gestión de Libros")
