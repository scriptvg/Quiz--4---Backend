from textual.screen import Screen
from textual.widgets import Static

class AutoresScreen(Screen):
    def compose(self):
        yield Static("Gestión de Autores")
