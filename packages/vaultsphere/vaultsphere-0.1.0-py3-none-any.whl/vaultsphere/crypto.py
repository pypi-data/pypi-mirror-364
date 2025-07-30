from cryptography.fernet import Fernet, InvalidToken

def generate_key() -> bytes:
    """Genera una clave segura para cifrado symétrico."""
    return Fernet.generate_key()

def encrypt(data: bytes, key: bytes) -> bytes:
    """Cifra bytes con la clave dada."""
    f = Fernet(key)
    return f.encrypt(data)

def decrypt(token: bytes, key: bytes) -> bytes:
    """Descifra bytes cifrados con la clave dada. Lanza error si falla."""
    f = Fernet(key)
    try:
        return f.decrypt(token)
    except InvalidToken:
        raise ValueError("Clave inválida o datos corruptos, no se pudo descifrar.")
