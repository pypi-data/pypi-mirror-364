# 🔐 VaultSphere

**VaultSphere** es una base de datos NoSQL encriptada desarrollada en Python. Guarda todos los valores de forma segura usando cifrado AES-256 (CBC) con padding y una clave secreta generada al inicializar. Ideal para almacenar datos sensibles, simples o complejos, sin depender de ningún motor externo.

---

## 🚀 Características

- 📦 Base de datos basada en archivos (`.vdb`)
- 🔐 Cifrado AES-256 CBC usando `cryptography`
- 🧠 Serialización segura con `pickle`
- 🛡️ Padding PKCS7 para mantener integridad de los bloques
- 🧰 Interfaz sencilla para `set`, `get`, `delete`, y `save`

---

## 🛠️ Requisitos:
    Python 3.7+
    Paquetes:
        cryptography

---

## 💾 Ejemplo de Uso

```python
from core import VaultDatabase

# Inicializa la DB
db = VaultDatabase('TestingFolder/test.vdb', b'mi_clave_super_segura_de_32bytes!!')

# Guardar datos
db.set("usuario", {"nombre": "Max", "rol": "Admin"})
db.set("token", "gAAAAAB...")

# Obtener datos
print(db.get("usuario"))

# Eliminar un valor
db.delete("token")

# Guardar cambios
db.save()
```

## 🔑 ¿Cómo consigo mi clave?

Al ejecutar test.py por primera vez se generará una clave aleatoria de 32 bytes codificada en base64:
```
Clave generada: OmOXtfqU0XKk8x4b7xbZegaIXUhIasLECHTJesFMdig=
```

Puedes reutilizar esa clave para futuras lecturas usando:
```
import base64
key = base64.b64decode("OmOXtfqU0XKk8x4b7xbZegaIXUhIasLECHTJesFMdig=")
```

---

## 🧪 Ejecución del Test
    Para probar la funcionalidad:
    ```
    python app.py
    ```

    Esto hará lo siguiente:
        - Generará una clave segura.
        - Creará una DB encriptada.
        - Insetará algunos datos.
        - Volverá a abrir la DB y mostrará los datos desencriptados.

---

## ⚠️ Advertencias
    - La clave debe tener exactamente 32 bytes (256 bits). Si estás usando una string, asegúrate de convertirla bien o usar base64 como arriba.
    - El sistema usa pickle, así que evita cargar archivos .vdb de fuentes desconocidas ⚠️.