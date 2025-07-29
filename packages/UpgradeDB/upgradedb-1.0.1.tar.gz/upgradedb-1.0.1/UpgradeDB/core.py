import json
import os
from typing import Any, Callable, List, Optional, Union

class UpgradeDB:
    def __init__(self, file_path="database.json"):
        self.file_path = file_path
        self.data = {}
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    self.data = json.load(f)
                except json.JSONDecodeError:
                    self.data = {}
        else:
            self.data = {}

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self._save()

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def delete(self, key: str) -> bool:
        if key in self.data:
            del self.data[key]
            self._save()
            return True
        return False

    def has(self, key: str) -> bool:
        return key in self.data

    def all(self) -> dict:
        return self.data

    def clear(self) -> None:
        self.data = {}
        self._save()

    def push(self, key: str, value: Any) -> None:
        arr = self.data.get(key, [])
        if not isinstance(arr, list):
            arr = []
        arr.append(value)
        self.data[key] = arr
        self._save()

    def pop(self, key: str) -> Optional[Any]:
        arr = self.data.get(key, [])
        if isinstance(arr, list) and arr:
            val = arr.pop()
            self.data[key] = arr
            self._save()
            return val
        return None

    def shift(self, key: str) -> Optional[Any]:
        arr = self.data.get(key, [])
        if isinstance(arr, list) and arr:
            val = arr.pop(0)
            self.data[key] = arr
            self._save()
            return val
        return None

    def unshift(self, key: str, value: Any) -> None:
        arr = self.data.get(key, [])
        if not isinstance(arr, list):
            arr = []
        arr.insert(0, value)
        self.data[key] = arr
        self._save()

    def add(self, key: str, amount: Union[int, float]) -> None:
        current = self.data.get(key, 0)
        if not isinstance(current, (int, float)):
            current = 0
        self.data[key] = current + amount
        self._save()

    def subtract(self, key: str, amount: Union[int, float]) -> None:
        current = self.data.get(key, 0)
        if not isinstance(current, (int, float)):
            current = 0
        self.data[key] = current - amount
        self._save()

    def math(self, key: str, operator: str, amount: Union[int, float]) -> None:
        current = self.data.get(key, 0)
        if not isinstance(current, (int, float)):
            current = 0

        if operator == '+':
            self.data[key] = current + amount
        elif operator == '-':
            self.data[key] = current - amount
        elif operator == '*':
            self.data[key] = current * amount
        elif operator == '/':
            self.data[key] = current / amount if amount != 0 else current
        else:
            raise ValueError("Operador inválido, use '+', '-', '*', '/'")
        self._save()

    def filter(self, key: str, func: Callable[[Any], bool]) -> List[Any]:
        arr = self.data.get(key, [])
        if isinstance(arr, list):
            return list(filter(func, arr))
        return []

    def find(self, key: str, func: Callable[[Any], bool]) -> Optional[Any]:
        arr = self.data.get(key, [])
        if isinstance(arr, list):
            for item in arr:
                if func(item):
                    return item
        return None

    def includes(self, key: str, value: Any) -> bool:
        arr = self.data.get(key, [])
        if isinstance(arr, list):
            return value in arr
        return False

    def includes_value(self, key: str, value: Any) -> bool:
        return self.includes(key, value)

    def keys(self) -> list:
        return list(self.data.keys())

    def values(self) -> list:
        return list(self.data.values())

    def type(self, key: str) -> Optional[str]:
        val = self.data.get(key)
        if val is None:
            return None
        return type(val).__name__

    def starts_with(self, prefix: str) -> dict:
        return {k: v for k, v in self.data.items() if k.startswith(prefix)}

class Table:
    def __init__(self, name: str, db: UpgradeDB):
        self.name = name
        self.db = db
        if self.name not in self.db.data:
            self.db.data[self.name] = {}
            self.db._save()

    def set(self, key: str, value: Any) -> None:
        self.db.data[self.name][key] = value
        self.db._save()

    def get(self, key: str, default: Any = None) -> Any:
        return self.db.data[self.name].get(key, default)

    def delete(self, key: str) -> bool:
        if key in self.db.data[self.name]:
            del self.db.data[self.name][key]
            self.db._save()
            return True
        return False

    def has(self, key: str) -> bool:
        return key in self.db.data[self.name]

    def all(self) -> dict:
        return self.db.data[self.name]

    def clear(self) -> None:
        self.db.data[self.name] = {}
        self.db._save()

    def push(self, key: str, value: Any) -> None:
        arr = self.db.data[self.name].get(key, [])
        if not isinstance(arr, list):
            arr = []
        arr.append(value)
        self.db.data[self.name][key] = arr
        self.db._save()

    def pop(self, key: str) -> Optional[Any]:
        arr = self.db.data[self.name].get(key, [])
        if isinstance(arr, list) and arr:
            val = arr.pop()
            self.db.data[self.name][key] = arr
            self.db._save()
            return val
        return None

    def shift(self, key: str) -> Optional[Any]:
        arr = self.db.data[self.name].get(key, [])
        if isinstance(arr, list) and arr:
            val = arr.pop(0)
            self.db.data[self.name][key] = arr
            self.db._save()
            return val
        return None

    def unshift(self, key: str, value: Any) -> None:
        arr = self.db.data[self.name].get(key, [])
        if not isinstance(arr, list):
            arr = []
        arr.insert(0, value)
        self.db.data[self.name][key] = arr
        self.db._save()

    def add(self, key: str, amount: Union[int, float]) -> None:
        current = self.db.data[self.name].get(key, 0)
        if not isinstance(current, (int, float)):
            current = 0
        self.db.data[self.name][key] = current + amount
        self.db._save()

    def subtract(self, key: str, amount: Union[int, float]) -> None:
        current = self.db.data[self.name].get(key, 0)
        if not isinstance(current, (int, float)):
            current = 0
        self.db.data[self.name][key] = current - amount
        self.db._save()

    def math(self, key: str, operator: str, amount: Union[int, float]) -> None:
        current = self.db.data[self.name].get(key, 0)
        if not isinstance(current, (int, float)):
            current = 0

        if operator == '+':
            self.db.data[self.name][key] = current + amount
        elif operator == '-':
            self.db.data[self.name][key] = current - amount
        elif operator == '*':
            self.db.data[self.name][key] = current * amount
        elif operator == '/':
            self.db.data[self.name][key] = current / amount if amount != 0 else current
        else:
            raise ValueError("Operador inválido, use '+', '-', '*', '/'")
        self.db._save()

    def filter(self, key: str, func: Callable[[Any], bool]) -> List[Any]:
        arr = self.db.data[self.name].get(key, [])
        if isinstance(arr, list):
            return list(filter(func, arr))
        return []

    def find(self, key: str, func: Callable[[Any], bool]) -> Optional[Any]:
        arr = self.db.data[self.name].get(key, [])
        if isinstance(arr, list):
            for item in arr:
                if func(item):
                    return item
        return None

    def includes(self, key: str, value: Any) -> bool:
        arr = self.db.data[self.name].get(key, [])
        if isinstance(arr, list):
            return value in arr
        return False

    def includes_value(self, key: str, value: Any) -> bool:
        return self.includes(key, value)

    def keys(self) -> list:
        return list(self.db.data[self.name].keys())

    def values(self) -> list:
        return list(self.db.data[self.name].values())

    def type(self, key: str) -> Optional[str]:
        val = self.db.data[self.name].get(key)
        if val is None:
            return None
        return type(val).__name__

    def starts_with(self, prefix: str) -> dict:
        return {k: v for k, v in self.db.data[self.name].items() if k.startswith(prefix)}
