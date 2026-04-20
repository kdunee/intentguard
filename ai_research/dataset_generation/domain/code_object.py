from dataclasses import dataclass


@dataclass
class CodeObject:
    name: str
    code: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "code": self.code}
