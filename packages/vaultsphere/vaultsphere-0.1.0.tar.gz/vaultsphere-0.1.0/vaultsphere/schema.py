def validate_document(doc: dict, schema: dict) -> None:
    for field, rules in schema.items():
        if rules.get('required') and field not in doc:
            raise ValueError(f"Campo obligatorio '{field}' no encontrado.")
        if field in doc:
            val = doc[field]
            expected_type = rules.get('type')
            nullable = rules.get('nullable', False)
            if val is None and not nullable:
                raise ValueError(f"Campo '{field}' no puede ser None.")
            if expected_type and val is not None and not isinstance(val, expected_type):
                raise TypeError(f"Campo '{field}' debe ser de tipo {expected_type.__name__}, no {type(val).__name__}.")
