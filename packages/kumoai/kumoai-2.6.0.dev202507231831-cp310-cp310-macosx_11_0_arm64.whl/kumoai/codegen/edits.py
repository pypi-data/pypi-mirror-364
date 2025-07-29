from typing import List, NamedTuple


# dummy edit class for now
class UniversalReplacementEdit:
    def __init__(self, path: str, value: object):
        self.path = path
        self.value = value
        self.required_imports: List[str] = []

    def emit_lines(self, var_name: str) -> list[str]:
        return [f"{var_name}{self.path} = {self.value}"]

    def _required_imports(self) -> list[str]:
        return []


class EditResult(NamedTuple):
    edits: List["UniversalReplacementEdit"]
    imports: List[str]
