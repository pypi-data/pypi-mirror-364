import os
import json
import shutil
import datetime
from copy import deepcopy
from typing import Any, Dict, List, Optional, Callable
from .crypto import encrypt, decrypt
from .schema import validate_document
from .index import IndexManager
from .utils import match_query, apply_query_operator
import base64

class VaultSphere:
    def __init__(
        self,
        filename: str,
        encryption_key: bytes,
        tables: Optional[Dict[str, Dict]] = None,  
        autosave: bool = True,
        backups: Optional[List[Dict]] = None,  
        on_save: Optional[Callable[['VaultSphere'], None]] = None,
        on_load: Optional[Callable[['VaultSphere'], None]] = None,
    ):
        self.filename = filename
        self.encryption_key = encryption_key
        self.autosave = autosave
        self.tables = tables or {}
        self.on_save = on_save
        self.on_load = on_load
        self.backups = backups or []
        self.data = {}  
        self.index_manager = IndexManager()
        self._load_database()
        self._setup_indices()
        

    def _load_database(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                encrypted_data = f.read()
            decrypted = decrypt(encrypted_data, self.encryption_key)
            self.data = json.loads(decrypted.decode('utf-8'))
            if self.on_load:
                self.on_load(self)
        else:
            self.data = {table: [] for table in self.tables.keys()}

    def _setup_indices(self):
        for table, config in self.tables.items():
            unique_fields = config.get('unique', [])
            self.index_manager.create_index(table, unique_fields)

    def save(self):
        json_bytes = json.dumps(self.data, indent=2).encode('utf-8')
        encrypted = encrypt(json_bytes, self.encryption_key)
        with open(self.filename, 'wb') as f:
            f.write(encrypted)
        if self.on_save:
            self.on_save(self)

    def backup(self) -> str:
        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.filename}_backup_{now_str}.json"
        shutil.copyfile(self.filename, backup_file)
        return backup_file

    def restore(self, backup_path: str) -> None:
        if os.path.exists(backup_path):
            shutil.copyfile(backup_path, self.filename)
            self._load_database()
        else:
            raise FileNotFoundError(f"Backup {backup_path} no encontrado")

    def create_table(self, table_name: str, schema: Dict):
        if table_name in self.tables:
            raise ValueError(f"Tabla {table_name} ya existe")
        self.tables[table_name] = schema
        self.data[table_name] = []
        self.save()

    def insert(self, table_name: str, document: Dict) -> Dict:
        if table_name not in self.tables:
            raise ValueError(f"Tabla {table_name} no definida")
        schema = self.tables[table_name].get('schema', {})
        validate_document(document, schema)  

        primary_key = self.tables[table_name].get('primaryKey', 'id')
        unique_fields = self.tables[table_name].get('unique', [])

        if primary_key not in document:
            document[primary_key] = self._generate_id(table_name)

        for field in unique_fields:
            if any(doc.get(field) == document.get(field) for doc in self.data[table_name]):
                raise ValueError(f"Valor duplicado para campo único '{field}'")

        now_iso = datetime.datetime.utcnow().isoformat()
        document['_createdAt'] = now_iso
        document['_updatedAt'] = now_iso

        self.data[table_name].append(document)
        if self.autosave:
            self.save()
        return document

    def _generate_id(self, table_name: str) -> int:
        ids = [doc.get(self.tables[table_name].get('primaryKey', 'id'), 0) for doc in self.data[table_name]]
        return max(ids, default=0) + 1

    def find(self, table_name: str, query: Optional[Dict] = None) -> List[Dict]:
        if query is None:
            query = {}
        if table_name not in self.data:
            return []
        return [doc for doc in self.data[table_name] if self._matches_query(doc, query)]

    def findById(self, table_name: str, _id: Any) -> Optional[Dict]:
        primary_key = self.tables.get(table_name, {}).get('primaryKey', 'id')
        for doc in self.data.get(table_name, []):
            if doc.get(primary_key) == _id:
                return doc
        return None

    def has_table(self, name: str) -> bool:
        return name in self.data

    def findOne(self, table_name: str, query: Dict) -> Optional[Dict]:
        for doc in self.data.get(table_name, []): 
            if self._matches_query(doc, query):
                return doc
        return None

    def update(self, table_name: str, _id: Any, new_data: Dict) -> Optional[Dict]:
        if table_name not in self.tables:
            raise ValueError(f"Tabla {table_name} no definida")

        schema = self.tables[table_name].get('schema', {})
        unique_fields = self.tables[table_name].get('unique', [])
        primary_key = self.tables[table_name].get('primaryKey', 'id')

        for i, doc in enumerate(self.data.get(table_name, [])):
            if doc.get(primary_key) == _id:
                updated_doc = doc.copy()
                updated_doc.update(new_data)
                validate_document(updated_doc, schema)

                for field in unique_fields:
                    if field in new_data:
                        if any(
                            other_doc.get(field) == updated_doc.get(field) and
                            other_doc.get(primary_key) != _id
                            for other_doc in self.data[table_name]
                        ):
                            raise ValueError(f"Valor duplicado para campo único '{field}'")

                updated_doc['_updatedAt'] = datetime.datetime.utcnow().isoformat()

                self.data[table_name][i] = updated_doc
                if self.autosave:
                    self.save()
                return updated_doc

        return None

    def delete(self, table_name: str, _id: Any) -> bool:
        primary_key = self.tables.get(table_name, {}).get('primaryKey', 'id')
        original_len = len(self.data.get(table_name, []))
        self.data[table_name] = [doc for doc in self.data.get(table_name, []) if doc.get(primary_key) != _id]
        deleted = len(self.data[table_name]) < original_len
        if deleted and self.autosave:
            self.save()
        return deleted

    def transaction(self, func: Callable[['VaultSphere'], Any]) -> Any:
        snapshot = deepcopy(self.data)
        try:
            result = func(self)
            self.save()
            return result
        except Exception as e:
            self.data = snapshot  
            raise e

    def _matches_query(self, document: Dict, query: Dict) -> bool:
        for key, cond in query.items():
            if isinstance(cond, dict):
                for op, val in cond.items():
                    if not apply_query_operator(document.get(key), op, val):
                        return False
            else:
                if document.get(key) != cond:
                    return False
        return True

    def stats(self) -> Dict:
        total_docs = sum(len(docs) for docs in self.data.values())
        db_size = os.path.getsize(self.filename) if os.path.exists(self.filename) else 0
        return {
            "totalDocuments": total_docs,
            "databaseSize": db_size,
            "tables": list(self.data.keys())
        }

    def reset(self):
        self.backup()
        self.data = {table: [] for table in self.tables.keys()}
        self.save()

    # --- CLI simple para controlar VaultSphere desde consola ---
    def run_cli(self):
        print("🔥 VaultSphere CLI arrancado")
        print("Comandos: insert <tabla> <json>, read <tabla> <id>, update <tabla> <id> <json>, remove <tabla> <id>, exit")

        while True:
            try:
                line = input("VaultSphere> ").strip()
                if not line:
                    continue
                parts = line.split(' ', 3)
                cmd = parts[0].lower()

                if cmd == 'exit':
                    print("Adiós! 👋")
                    break
                elif cmd == 'insert' and len(parts) == 3:
                    tabla = parts[1]
                    doc = json.loads(parts[2])
                    inserted = self.insert(tabla, doc)
                    print("Insertado:", inserted)
                elif cmd == 'read' and len(parts) == 3:
                    tabla, id_str = parts[1], parts[2]
                    try:
                        id_val = int(id_str)
                    except:
                        id_val = id_str
                    doc = self.findById(tabla, id_val)
                    if doc:
                        print(json.dumps(doc, indent=2))
                    else:
                        print("No encontrado")
                elif cmd == 'update' and len(parts) == 4:
                    tabla, id_str = parts[1], parts[2]
                    try:
                        id_val = int(id_str)
                    except:
                        id_val = id_str
                    new_data = json.loads(parts[3])
                    updated = self.update(tabla, id_val, new_data)
                    if updated:
                        print("Actualizado:", updated)
                    else:
                        print("No encontrado")
                elif cmd == 'remove' and len(parts) == 3:
                    tabla, id_str = parts[1], parts[2]
                    try:
                        id_val = int(id_str)
                    except:
                        id_val = id_str
                    deleted = self.delete(tabla, id_val)
                    print("Eliminado" if deleted else "No encontrado")
                else:
                    print("Comando inválido")
            except json.JSONDecodeError:
                print("Error en JSON 😵‍💫")
            except Exception as e:
                print(f"Error: {e}")
