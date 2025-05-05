from textual.screen import Screen
from textual.widgets import Static

class EstadisticasScreen(Screen):
    def compose(self):
        yield Static("Estadísticas")
