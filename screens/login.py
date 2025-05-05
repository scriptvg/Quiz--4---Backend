from textual.screen import Screen
from textual.widgets import Static

class LoginScreen(Screen):
    def compose(self):
        yield Static("Inicio de Sesión")
