class AuthManager:
    USUARIOS = {
        "admin": "admin123",
        "usuario": "clave"
    }

    @staticmethod
    def verificar_credenciales(usuario: str, clave: str) -> bool:
        return AuthManager.USUARIOS.get(usuario) == clave
