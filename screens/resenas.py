from textual.screen import Screen
from textual.widgets import Static

class ResenasScreen(Screen):
    def compose(self):
        yield Static("Gestión de Reseñas")
