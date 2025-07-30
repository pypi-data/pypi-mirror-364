from typing import Any, Dict

def apply_query_operator(value: Any, operator: str, query_val: Any) -> bool:
    if operator == "$gt":
        return value > query_val
    elif operator == "$gte":
        return value >= query_val
    elif operator == "$lt":
        return value < query_val
    elif operator == "$lte":
        return value <= query_val
    elif operator == "$ne":
        return value != query_val
    elif operator == "$in":
        return value in query_val
    elif operator == "$nin":
        return value not in query_val
    else:
        # operador desconocido, hacer igualdad simple
        return value == query_val

def match_query(document: Dict[str, Any], query: Dict[str, Any]) -> bool:
    for key, condition in query.items():
        value = document.get(key)
        if isinstance(condition, dict):
            for op, v in condition.items():
                if not apply_query_operator(value, op, v):
                    return False
        else:
            if value != condition:
                return False
    return True
