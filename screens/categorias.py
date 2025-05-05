from textual.screen import Screen
from textual.widgets import Static

class CategoriasScreen(Screen):
    def compose(self):
        yield Static("Gestión de Categorías")
