from textual.screen import Screen
from textual.widgets import Static

class VentasScreen(Screen):
    def compose(self):
        yield Static("Registro de Ventas")
