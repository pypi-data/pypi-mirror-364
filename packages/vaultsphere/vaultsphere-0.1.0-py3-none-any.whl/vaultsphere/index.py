from typing import List, Dict, Set, Optional

class IndexManager:
    def __init__(self):
        # Estructura: { tabla: { campo: set(de valores únicos) } }
        self.indices: Dict[str, Dict[str, Set]] = {}

    def create_index(self, table: str, fields: List[str]):
        if table not in self.indices:
            self.indices[table] = {}
        for f in fields:
            self.indices[table][f] = set()

    def drop_index(self, table: str, field: str):
        if table in self.indices and field in self.indices[table]:
            del self.indices[table][field]

    def add_value(self, table: str, field: str, value):
        if table in self.indices and field in self.indices[table]:
            self.indices[table][field].add(value)

    def remove_value(self, table: str, field: str, value):
        if table in self.indices and field in self.indices[table]:
            self.indices[table][field].discard(value)

    def exists(self, table: str, field: str, value) -> bool:
        return table in self.indices and \
               field in self.indices[table] and \
               value in self.indices[table][field]

    def rebuild_index(self, table: str, field: str, data: List[dict]):
        # Limpia y reconstruye índice para un campo dado basado en los datos actuales
        if table not in self.indices:
            self.indices[table] = {}
        self.indices[table][field] = set()
        for doc in data:
            val = doc.get(field)
            if val is not None:
                self.indices[table][field].add(val)
