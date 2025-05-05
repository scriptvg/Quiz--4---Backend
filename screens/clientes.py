from textual.screen import Screen
from textual.widgets import Static

class ClientesScreen(Screen):
    def compose(self):
        yield Static("Gestión de Clientes")
