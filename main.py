from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding
from screens.libros import LibrosScreen
from screens.autores import AutoresScreen
from screens.categorias import CategoriasScreen
from screens.clientes import ClientesScreen
from screens.ventas import VentasScreen
from screens.resenas import ResenasScreen
from screens.estadisticas import EstadisticasScreen

class BibliotecaApp(App):
    CSS_PATH = "styles.css"

    BINDINGS = [
        Binding("l", "libros", "Libros"),
        Binding("a", "autores", "Autores"),
        Binding("c", "categorias", "Categorías"),
        Binding("v", "ventas", "Ventas"),
        Binding("r", "resenas", "Reseñas"),
        Binding("e", "estadisticas", "Estadísticas"),
        Binding("q", "quit", "Salir"),
    ]

    def on_mount(self) -> None:
        self.push_screen("libros")

    def action_libros(self) -> None:
        self.push_screen(LibrosScreen(), name="libros")

    def action_autores(self) -> None:
        self.push_screen(AutoresScreen(), name="autores")

    def action_categorias(self) -> None:
        self.push_screen(CategoriasScreen(), name="categorias")

    def action_clientes(self) -> None:
        self.push_screen(ClientesScreen(), name="clientes")

    def action_ventas(self) -> None:
        self.push_screen(VentasScreen(), name="ventas")

    def action_resenas(self) -> None:
        self.push_screen(ResenasScreen(), name="resenas")

    def action_estadisticas(self) -> None:
        self.push_screen(EstadisticasScreen(), name="estadisticas")

if __name__ == "__main__":
    BibliotecaApp().run()
